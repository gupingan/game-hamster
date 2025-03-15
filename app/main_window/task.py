"""
主窗口逻辑任务列表
"""
import hashlib
import random
from pathlib import Path
from PySide2 import QtCore, QtWidgets, QtGui
from app.bases import config
from app.bases.models import TableModel, Preset


def get_cell(state, default_=config.DEFAULT_CELL):
    return config.STATE_STYLES.get(state, default_)


class MD5WorkerSignals(QtCore.QObject):
    """
    关于 state 的值:
          程序异常（-2）、失败（-1）、未校验（0）、通过（1）、校验中（2）、文件缺失（3）
    信号描述：
        beginning：任务开始时
        error：任务执行过程中异常
        progress：任务进度
        finished：任务完成时
    """
    beginning = QtCore.Signal(int)  # row
    error = QtCore.Signal(int, Exception)  # (row, exception)
    progress = QtCore.Signal(int, int)  # (row, progress)
    finished = QtCore.Signal(int, int, str)  # (row, state, md5)


class MD5Worker(QtCore.QRunnable):
    def __init__(self, row, filepath, data_md5):
        super().__init__()
        self.row = row  # 传入的行，用于回显
        self.filepath = filepath  # 传入的相对路径，用于查看校验
        self.data_md5 = data_md5  # 传入的预设 MD5，用于比较
        self._is_running = True  # 表示运行状态，正在运行中（实例化后即运行）
        self.signals = MD5WorkerSignals()  # 连接的信号槽对象
        self.chunk_size = random.randint(32, 128) * 1024  # 小文件每次读取的块大小 32kb~128kb
        self.read_size = 0  # 已读取的字节数

    def run(self):
        """执行 MD5 校验任务"""
        try:
            # 发出任务开始信号
            self.signals.beginning.emit(self.row)
            filepath = Path(self.filepath)
            # 如果文件不存在，则失败
            if not filepath.exists():
                self.signals.finished.emit(self.row, -1, '文件缺失，无法计算')
                return None

            # 初始化 MD5 哈希对象
            md5 = hashlib.md5()
            # 文件分块计算
            total_size = filepath.stat().st_size
            # 大文件 超过 1GB 分块范围则是 256kb~1mb
            if total_size >= 1024 * 1024 * 1024:
                self.chunk_size = random.randint(256, 1024) * 1024

            with filepath.open('rb') as f:
                while self._is_running:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    md5.update(chunk)
                    self.read_size += len(chunk)
                    # 计算进度，并发出信号通知
                    progress = int((self.read_size / total_size) * 100)
                    self.signals.progress.emit(self.row, progress)
            if self._is_running:
                # 计算最终的 MD5 值
                md5_value = md5.hexdigest()
                # 正确执行完成校验的情况（不代表校验通过，需要比较值）
                if total_size == 0:
                    self.signals.progress.emit(self.row, 100)
                state = -1 if md5_value != self.data_md5 else 1
                self.signals.finished.emit(self.row, state, md5_value)
            else:
                self.signals.progress.emit(self.row, 0)
                self.signals.finished.emit(self.row, 0, "本地 MD5 暂未校验")
        except Exception as e:
            # 处理其他不可预知的异常情况
            self.signals.error.emit(self.row, e)
            self.signals.finished.emit(self.row, -2, '程序异常，无法计算')

    def stop(self):
        """停止任务的执行"""
        self._is_running = False


class MD5WorkerPool(QtCore.QThreadPool):
    allDone = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.active_tasks = 0
        self.active_tasks_mutex = QtCore.QMutex()
        self.errors = []
        self.collect_error_mutex = QtCore.QMutex()

    def start(self, runnable: MD5Worker, priority=0):
        self.active_tasks_mutex.lock()
        self.active_tasks += 1
        self.active_tasks_mutex.unlock()

        runnable.signals.finished.connect(self._task_finished)
        runnable.signals.error.connect(self._task_occur_error)
        super().start(runnable, priority)

    def _task_finished(self):
        self.active_tasks_mutex.lock()
        self.active_tasks -= 1
        if self.active_tasks == 0:
            self.allDone.emit()
        self.active_tasks_mutex.unlock()

    def _task_occur_error(self, row, exception):
        self.collect_error_mutex.lock()
        self.errors.append((row, exception))
        self.collect_error_mutex.unlock()


class PresetProxy(Preset):
    def __init__(self, preset: Preset):
        super().__init__(preset.filename, preset.data_md5)
        self.is_checked = False  # 无用属性，仅做保留
        self.local_md5 = '本地 MD5 暂未校验'
        self.state = 0  # 校验失败（-1）、未校验（0）、校验通过（1）、校验中（2）
        self.progress = 0


class ProgressBarDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        if not index.isValid():
            return

        value = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
        if value is None:
            return

        try:
            progress = float(value) / 100.0
        except ValueError:
            progress = 0.0

        # 创建进度条选项
        # 设置进度条背景颜色
        background_color = QtGui.QColor(255, 255, 255)
        painter.setBrush(background_color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(option.rect)

        # 设置进度条颜色
        progress_color = QtGui.QColor(204, 245, 0)
        progress_rect = QtCore.QRect(option.rect)
        progress_rect.setWidth(int(option.rect.width() * progress))
        painter.setBrush(progress_color)
        painter.drawRect(progress_rect)

        # 绘制进度条文本
        text = f"{int(progress * 100)}%"
        painter.setPen(QtGui.QColor(50, 50, 50))
        text_rect = option.rect
        painter.drawText(text_rect, QtCore.Qt.AlignmentFlag.AlignCenter, text)

        # 恢复绘画状态
        painter.restore()


class PresetTableModel(TableModel):
    def __init__(self):
        super().__init__()
        self.proxies = [PresetProxy(p) for p in config.Config.presets if p]
        self.headers = ['文件名', '预设 MD5', '本地 MD5', '当前进度', '校验状态']

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            preset_proxy = self.proxies[row]
            if col == 0:
                return preset_proxy.filename
            elif col == 1:
                return preset_proxy.data_md5
            elif col == 2:
                return preset_proxy.local_md5
            elif col == 3:
                return f'{preset_proxy.progress}'
            elif col == 4:
                return get_cell(preset_proxy.state).display_name
            return None
        if role == QtCore.Qt.ItemDataRole.ForegroundRole:
            preset_proxy = self.proxies[row]
            if col == 4:
                color_str = get_cell(preset_proxy.state).foreground_color
                return QtGui.QBrush(QtGui.QColor(color_str))

        if role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
            return QtCore.Qt.AlignmentFlag.AlignCenter

        return None

    def updateData(self):
        self.beginResetModel()
        self.proxies = [PresetProxy(p) for p in config.Config.presets]
        self.endResetModel()
