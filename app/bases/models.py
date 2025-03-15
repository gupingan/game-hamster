"""
包含诸多模型类
通常客户无需修改
"""
from PySide2 import QtCore
from pathlib import Path
from .utils import calculate_md5


class Preset:
    def __init__(self, filename: str, data_md5: str):
        self.filename = filename
        self.data_md5 = data_md5

    def __eq__(self, other):
        if issubclass(other.__class__, Preset):
            return self.filename == other.filename and self.data_md5 == other.data_md5
        return False

    def to_dict(self):
        return {
            'filename': self.filename,
            'data_md5': self.data_md5
        }

    @classmethod
    def from_filename(cls, filename: str):
        filepath = Path(filename)
        if not filepath.exists():
            return None
        if filepath.is_dir():
            return None

        data_md5 = calculate_md5(filepath)
        obj = cls(filepath.name, data_md5)
        return obj


class Cell:
    def __init__(self, display_name: str, foreground_color: str):
        self.display_name = display_name
        self.foreground_color = foreground_color


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.proxies = []
        self.headers = []

    def getCheckedData(self):
        return (p for p in self.proxies if p.is_checked)

    def checkedCount(self):
        return len([p for p in self.proxies if p.is_checked])

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.proxies)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.headers)

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

    def setData(self, index, value, role=QtCore.Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False

        row = index.row()
        col = index.column()

        proxy = self.proxies[row]

        if role == QtCore.Qt.ItemDataRole.CheckStateRole and col == 0:
            proxy.is_checked = (value == QtCore.Qt.CheckState.Checked)
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags

        flags = QtCore.Qt.ItemFlag.ItemIsEnabled

        return flags

    def headerData(self, section, orientation, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                if 0 <= section < len(self.headers):
                    return self.headers[section]
            elif orientation == QtCore.Qt.Orientation.Vertical:
                return str(section + 1)

        return None

    def updateData(self):
        pass
