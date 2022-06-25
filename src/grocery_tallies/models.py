import enum
import typing

from PySide2 import QtCore

from . import constants, database

__all__ = [
    'UnitTypes',
    'GroceryTreeModel',
]


class UnitTypes(enum.Enum):
    COUNT = constants.UNIT_REGISTRY.count
    CUP = constants.UNIT_REGISTRY.cup
    TBSP = constants.UNIT_REGISTRY.tbsp
    TSP = constants.UNIT_REGISTRY.tsp

    @classmethod
    def as_strings(cls):
        return [x.name.lower() for x in cls]


class GroceryTreeModel(QtCore.QAbstractTableModel):
    raw_data_role = QtCore.Qt.UserRole + 1

    def __init__(self, grocery_items: typing.List[database.Product], parent=None):
        super().__init__(parent)

        self._data = grocery_items

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable

    def rowCount(self, parent: QtCore.QModelIndex = None) -> int:
        if not parent.isValid():
            return len(self._data)

        return len(self._data)

    def columnCount(self, parent: QtCore.QModelIndex = None) -> int:
        return 2

    def headerData(
            self,
            section: int,
            orientation: QtCore.Qt.Orientation,
            role: int = QtCore.Qt.DisplayRole
    ) -> typing.Any:
        if orientation == QtCore.Qt.Vertical:
            return

        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return 'Product'
            if section == 1:
                return 'Amount'

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> typing.Any:
        if not index.isValid():
            return

        if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            if index.column() == 0:
                return self._data[index.row()].name
            if index.column() == 1:
                return self._data[index.row()].total_quantities()

        if role == self.raw_data_role:
            return self._data[index.row()]

    # def setData(self, index: QtCore.QModelIndex, value: typing.Any, role: int = QtCore.Qt.EditRole) -> bool:
    #     if not index.isValid():
    #         return False
    #
    #     if role == QtCore.Qt.EditRole:
    #         if index.column() == 0:
    #             self._data[index.row()].name = value
    #         elif index.column() == 1:
    #             self._data[index.row()].quantity = value
    #         elif index.column() == 2:
    #             if isinstance(value, str):
    #                 try:
    #                     value = UnitTypes[value.upper()]
    #                 except KeyError:
    #                     return False
    #
    #             self._data[index.row()].convert(value)
    #
    #         else:
    #             return False
    #
    #         self.dataChanged.emit(index, index, [role])
    #         return True
    #
    #     if role == self.raw_data_role:
    #         self._data[index.row()] += value
    #         self.dataChanged.emit(index, index, [role])
    #         return True
    #
    #     return super().setData(index, value, role)

    def add_item(self, item: database.Product):
        # for i, d in enumerate(self._data):
        #     if d != item:
        #         continue
        #
        #     self.setData(self.index(i, 0), item, self.raw_data_role)
        #     return

        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
        self._data.append(item)
        self.endInsertRows()

    def remove_item(self, item: database.Product):
        if item not in self._data:
            return

        idx = self._data.index(item)
        self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
        self._data.pop(idx)
        self.endRemoveRows()
