import enum
import typing

from PySide2 import QtCore

from . import constants

__all__ = [
    'UnitTypes',
    'GroceryItem',
    'GroceryTableModel',
]


class UnitTypes(enum.Enum):
    COUNT = constants.UNIT_REGISTRY.count
    CUP = constants.UNIT_REGISTRY.cup
    TBSP = constants.UNIT_REGISTRY.tbsp
    TSP = constants.UNIT_REGISTRY.tsp

    @classmethod
    def as_strings(cls):
        return [x.name.lower() for x in cls]


class GroceryItem:
    def __init__(self, name: str = '', quantity: float = 0, unit: UnitTypes = UnitTypes.COUNT):
        super().__init__()

        self._name = name
        self._quantity = quantity
        self._unit = unit

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.name.lower() == other.name.lower():
            return True

    def __add__(self, other):
        if self != other:
            raise ValueError(f'__add__ is unsupported for types {self.__class__.__name__}, {other.__class__.__name__}')

        if self.unit == other.unit:
            quantity = self.quantity + other.quantity
        else:
            if self.unit == UnitTypes.COUNT or other.unit == UnitTypes.COUNT:
                raise ValueError('Cannot add a count to other unit types')

            quantity = (self.quantity * self.unit.value) + (other.quantity * other.unit.value)
            quantity = quantity.to(self.unit.value).magnitude

        return GroceryItem(self.name, quantity, self.unit)

    def __repr__(self):
        return f'<{self.__class__.__name__}({self._name}: {self._quantity} {self._unit.name})>'

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, v: str):
        self._name = v

    @property
    def quantity(self) -> float:
        return self._quantity

    @quantity.setter
    def quantity(self, v: float):
        self._quantity = v

    @property
    def unit(self) -> UnitTypes:
        return self._unit

    @unit.setter
    def unit(self, v: UnitTypes):
        self._unit = v

    def convert(self, v: UnitTypes):
        if v == UnitTypes.COUNT or self.unit == UnitTypes.COUNT:
            self.unit = v
            return

        self.quantity = (self.quantity * self.unit.value).to(v.value).magnitude
        self.unit = v


class GroceryTableModel(QtCore.QAbstractTableModel):
    raw_data_role = QtCore.Qt.UserRole + 1

    def __init__(self, grocery_items: typing.List[GroceryItem], parent=None):
        super().__init__(parent)

        self._data = grocery_items

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable

    def rowCount(self, parent: QtCore.QModelIndex = None) -> int:
        return len(self._data)

    def columnCount(self, parent: QtCore.QModelIndex = None) -> int:
        return 3

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
                return 'Item Name'
            if section == 1:
                return 'Quantity'
            if section == 2:
                return 'Unit'

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> typing.Any:
        if not index.isValid():
            return

        if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            if index.column() == 0:
                return self._data[index.row()].name
            if index.column() == 1:
                return self._data[index.row()].quantity
            if index.column() == 2:
                return self._data[index.row()].unit.name.lower()

        if role == self.raw_data_role:
            return self._data[index.row()]

    def setData(self, index: QtCore.QModelIndex, value: typing.Any, role: int = QtCore.Qt.EditRole) -> bool:
        if not index.isValid():
            return False

        if role == QtCore.Qt.EditRole:
            if index.column() == 0:
                self._data[index.row()].name = value
            elif index.column() == 1:
                self._data[index.row()].quantity = value
            elif index.column() == 2:
                if isinstance(value, str):
                    try:
                        value = UnitTypes[value.upper()]
                    except KeyError:
                        return False

                self._data[index.row()].convert(value)

            else:
                return False

            self.dataChanged.emit(index, index, [role])
            return True

        if role == self.raw_data_role:
            self._data[index.row()] += value
            self.dataChanged.emit(index, index, [role])
            return True

        return super().setData(index, value, role)

    def add_item(self, item: GroceryItem):
        for i, d in enumerate(self._data):
            if d != item:
                continue

            self.setData(self.index(i, 0), item, self.raw_data_role)
            return

        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
        self._data.append(item)
        self.endInsertRows()

    def remove_item(self, item: GroceryItem):
        if item not in self._data:
            return

        idx = self._data.index(item)
        self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
        self._data.pop(idx)
        self.endRemoveRows()
