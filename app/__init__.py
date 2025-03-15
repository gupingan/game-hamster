"""
包入口文件，通常不用修改
"""
import sys
from PySide2 import QtWidgets, QtCore, QtGui
from app.main_window import MainWindow
from app.bases.config import Config, ICON_PATH

QtCore.QCoreApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling)


def run_app():
    Config.read_json()
    # 暗色模式设置 darkmode对应值不同区别
    # 0: 禁用暗色模式（默认）
    # 1: 部分启用暗色模式
    # 2: 完全启用暗色模式（可选）
    sys.argv += ['-platform', 'windows:darkmode=0']

    app = QtWidgets.QApplication(sys.argv)
    # 设置程序风格：默认 Fusion，还有 windowsvista
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
    app.setWindowIcon(QtGui.QIcon(ICON_PATH))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
