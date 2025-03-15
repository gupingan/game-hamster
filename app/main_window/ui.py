"""
主界面窗口
"""
from PySide2 import QtCore, QtWidgets, QtGui
from app.bases import config
from .view import Ui_MainWindow
from .task import MD5Worker, MD5WorkerPool, ProgressBarDelegate, PresetTableModel


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # 安装底层 UI
        self.init_data()  # 初始化数据
        self.build_interface()  # 构建界面
        self.binding_events()  # 事件绑定

    def init_data(self):
        """构建线程池 工作列表"""
        # 以下为校验过程中所必须（请勿修改，校验逻辑在：task.py -> MD5Worker 类中）
        self.workers = []  # 校验工作列表
        self.pool = MD5WorkerPool(self)  # 校验专用的线程池
        self.pool.setMaxThreadCount(8)  # 设置线程池最大可用 8 个

    def build_interface(self):
        """构建界面中的部分东西"""
        # 设置软件标题，不要在这里更改
        self.setWindowTitle(config.APP_NAME)

        # 设置底部提示
        # 颜色：(十六进制，百度可搜索 某某颜色 十六进制) color: #DC143C
        # 字体大小：font-size: 10pt (正常大小)
        self.ui.bottomHint.setStyleSheet('margin-left:15px;color:red;font-size:10pt;')
        self.ui.bottomHint.setText(config.REAL_BOTTOM_HINT)
        self.ui.bottomHint.setOpenExternalLinks(True)  # 假设有超链接，允许点击跳转外部应用
        # 设置底部总进度条颜色
        # QProgressBar::chunk 是进度块颜色，QProgressBar 中设置的是默认背景颜色
        self.ui.totalProgressBar.setStyleSheet("""
            QProgressBar::chunk {
                background-color: #00ad0e;
                width: 20px;
            }
            QProgressBar {
                background-color: #e6e6e6;
            }
        """)

        # 设置顶部 LOGO
        logo_height = 80  # 默认高度
        self.ui.bannerLogo.setFixedHeight(logo_height)
        logo_pixmap = QtGui.QPixmap(config.LOGO)  # 将原图片进行缩放处理
        scaled_logo = logo_pixmap.scaledToHeight(logo_height, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.ui.bannerLogo.setPixmap(scaled_logo)

        # 顶部 logo 与下方表格的间距(默认可不用修改)
        self.ui.logoTableHeight.setFixedHeight(5)

        # 根据预设的数据提前加载到表格中
        self.ui.tableView.setStyleSheet('font-size:14px')  # 表格中字体大小
        progress_delegate = ProgressBarDelegate(self)  # 表格中进度条的绘制委托
        self.ui.tableView.setItemDelegateForColumn(3, progress_delegate)
        self.preset_model = PresetTableModel()  # 表格每行数据的模型记录
        self.ui.tableView.setModel(self.preset_model)
        self.ui.tableView.setMouseTracking(False)
        self.ui.tableView.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.ui.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.ui.tableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        # 第一列到第五列的列宽度
        self.ui.tableView.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.ui.tableView.setColumnWidth(1, 280)
        self.ui.tableView.setColumnWidth(2, 280)
        self.ui.tableView.setColumnWidth(3, 150)
        self.ui.tableView.setColumnWidth(4, 90)

    def binding_events(self):
        # 鼠标点击事件：顶部 LOGO 区域点击后使用浏览器并打开指定网址
        self.ui.logoWidget.mousePressEvent = self.open_url_on_logo_click
        # 信号槽：开始校验/停止按钮对应的点击事件 点击执行函数 on_toggle_state_click
        self.ui.toggleStateBtn.clicked.connect(self.on_toggle_state_click)

    @staticmethod
    def open_url_on_logo_click(event):
        """鼠标点击 LOGO 顶部区域的事件"""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(config.URL))

    def on_toggle_state_click(self):
        """业务逻辑：校验 MD5 值或者停止校验"""
        if self.workers:  # 分支：停止校验
            self.pool.allDone.disconnect(self.on_preset_verify_all_done)  # 将线程池完成的事件断开
            for worker in self.workers:
                worker.stop()  # 停止所有工作
            self.workers = []  # 工作线程列表置空
            self.ui.toggleStateBtn.setText("开始校验")  # 恢复按钮名称
            self.ui.totalProgressBar.setValue(0)  # 总进度条归零
            self.preset_model.updateData()
        else:  # 分支：开始校验
            for row, proxy in enumerate(self.preset_model.proxies):
                worker = MD5Worker(row, proxy.filename, proxy.data_md5)
                worker.signals.beginning.connect(self.on_preset_verify_beginning)  # 将预设校验开始时的状态传递
                worker.signals.progress.connect(self.on_preset_verify_progress)  # 将预设校验过程中进度的变化传递
                worker.signals.finished.connect(self.on_preset_verify_finished)  # 将预设校验完成后的状态传递
                self.workers.append(worker)  # 工作表中添加上该线程
            if self.workers:  # 如果有工作的线程，方可执行下方的初始化
                self.ui.totalProgressBar.setMaximum(len(self.preset_model.proxies) * 100)
                self.ui.toggleStateBtn.setText("停止校验")
                self.pool.allDone.connect(self.on_preset_verify_all_done)  # 将线程池完成的事件连接上
            for worker in self.workers:
                self.pool.start(worker)  # 启动工作线程（正式执行校验）

    def on_preset_verify_beginning(self, row):
        """业务逻辑：单条预设开始校验时初始化部分数据，比如状态、本地 MD5 等"""
        self.preset_model.proxies[row].state = 2  # 表示校验中
        self.preset_model.proxies[row].local_md5 = '正在校验文件中...'  # 开始校验时 MD5 显示
        self.preset_model.proxies[row].progress = 0  # 初始进度为 0
        start_index = self.preset_model.index(row, 0)
        end_index = self.preset_model.index(row, self.preset_model.columnCount() - 1)
        self.preset_model.dataChanged.emit(start_index, end_index)  # 更新对应行数据显示

    def on_preset_verify_progress(self, row, progress):
        """业务逻辑：校验过程中，传入新的进度以及总进度计算"""
        self.preset_model.proxies[row].progress = progress
        index = self.preset_model.index(row, 3)
        self.preset_model.dataChanged.emit(index, index)  # 更新第 4 列进度
        self.update_verify_total_progress()  # 更新校验过程的总进度

    def on_preset_verify_finished(self, row, result, local_md5):
        """业务逻辑：某行预设校验完成后调用"""
        self.preset_model.proxies[row].state = result  # 更改该执行的最终状态
        self.preset_model.proxies[row].local_md5 = local_md5  # 更改本地 MD5
        start_index = self.preset_model.index(row, 0)
        end_index = self.preset_model.index(row, self.preset_model.columnCount() - 1)
        self.preset_model.dataChanged.emit(start_index, end_index)  # 更新对应行

    def update_verify_total_progress(self):
        """业务逻辑：更新总进度，在 on_preset_verify_progress 方法中执行"""
        total_progress = sum(proxy.progress for proxy in self.preset_model.proxies)
        self.ui.totalProgressBar.setValue(int(total_progress))

    def on_preset_verify_all_done(self):
        """业务逻辑：所有预设校验完成后执行的任务"""
        self.pool.allDone.disconnect(self.on_preset_verify_all_done)  # 将线程池完成的事件断开
        self.workers = []  # 重置工作任务列表，方便可以二次校验
        self.ui.toggleStateBtn.setText("开始校验")  # 修改按钮为开始校验
        total_count = self.preset_model.rowCount()  # 获取检验数量
        success_count = sum(p.state == 1 for p in self.preset_model.proxies)  # 获取通过数量
        if not self.pool.errors:  # 保证没有统计到的异常，触发正常弹窗
            if total_count == success_count:  # 分支：检验和通过数量相同，则表示全部通过
                QtWidgets.QMessageBox.information(
                    self, '校验通过', f'总共 {total_count} 个文件校验通过，可以开始安装游戏啦！')
            else:  # 分支：检验和通过数量不相同，则表示有未通过
                QtWidgets.QMessageBox.warning(
                    self, '校验未完成', f'未通过：{total_count - success_count} 个文件\n已通过：{success_count} 个文件')
        else:
            error_string = '\n'.join([f'第{r}行: {e}' for r, e in self.pool.errors])
            self.pool.errors.clear()  # 表示错误消息消费完成，清空，接下来呈现
            QtWidgets.QMessageBox.critical(self, '发生错误', error_string)
