from PySide2 import QtWidgets, QtCore

from . import models

__all__ = [
    'GroceryTallies',
]


class GroceryTallies(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Tally Groceries')

        self._menu_bar = QtWidgets.QMenuBar(self)
        self._file_menu = self._menu_bar.addMenu('File')

        delegate = ComboBoxDelegate(self)
        delegate.set_items(models.UnitTypes.as_strings())

        self._grocery_view = QtWidgets.QTableView(self)
        self._grocery_view.setModel(QtCore.QSortFilterProxyModel(self))
        self._grocery_view.model().setSourceModel(models.GroceryTableModel([], self))

        self._grocery_view.setItemDelegateForColumn(2, delegate)
        self._grocery_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self._grocery_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._grocery_view.setSortingEnabled(True)
        self._grocery_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self._grocery_view.verticalHeader().hide()

        self._add_item_btn = QtWidgets.QPushButton('Add Item', self)
        self._add_item_btn.clicked.connect(self._add_item_clicked)

        self._rem_item_btn = QtWidgets.QPushButton('Remove Selected', self)
        self._rem_item_btn.clicked.connect(self._delete_item_clicked)

        self._build_ui()
        self._build_menus()

    def _build_ui(self):
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setMenuBar(self._menu_bar)
        self.layout().addWidget(self._grocery_view)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self._add_item_btn)
        btn_layout.addWidget(self._rem_item_btn)
        self.layout().addLayout(btn_layout)

    def _build_menus(self):
        new_action = self._file_menu.addAction('New List')
        new_action.triggered.connect(self._new_list_triggered)

        open_action = self._file_menu.addAction('Open List')
        open_action.triggered.connect(self._open_list_triggered)

        self._file_menu.addSeparator()

        save_action = self._file_menu.addAction('Save List')
        save_action.triggered.connect(self._save_list_triggered)

        self._file_menu.addSeparator()

        quit_action = self._file_menu.addAction('Quit')
        quit_action.triggered.connect(self._quit_triggered)

    def _new_list_triggered(self):
        ...

    def _open_list_triggered(self):
        ...

    def _save_list_triggered(self):
        ...

    def _quit_triggered(self):
        ...

    def _add_item_clicked(self):
        item_dialog = GroceryItemDialog('Add New Item', models.GroceryItem(), self)
        if not item_dialog.exec_():
            return

        self._grocery_view.model().sourceModel().add_item(item_dialog.item)

    def _delete_item_clicked(self):
        rows = self._grocery_view.selectionModel().selectedRows()
        if not rows:
            return

        src_idx = self._grocery_view.model().mapToSource(rows[0])
        item = self._grocery_view.model().sourceModel().data(
            src_idx,
            self._grocery_view.model().sourceModel().raw_data_role
        )
        self._grocery_view.model().sourceModel().remove_item(item)


class GroceryItemDialog(QtWidgets.QDialog):
    def __init__(self, title: str, item: models.GroceryItem, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setModal(True)

        self._item = item

        self._name_edit = QtWidgets.QLineEdit(self)
        self._name_edit.setText(self._item.name)

        self._qty_spin = QtWidgets.QDoubleSpinBox(self)
        self._qty_spin.setValue(self._item.quantity)

        self._unit_combo = QtWidgets.QComboBox(self)
        self._unit_combo.addItems(models.UnitTypes.as_strings())
        self._unit_combo.setCurrentText(self._item.unit.name.lower())

        self._warn_lbl = QtWidgets.QLabel('', self)
        self._warn_lbl.setWordWrap(True)
        self._warn_lbl.setStyleSheet('color: red')

        self._button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            parent=self
        )
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)

        self._build_ui()

    def _build_ui(self):
        self.setLayout(QtWidgets.QVBoxLayout())

        form = QtWidgets.QFormLayout()
        form.addRow('Label', self._name_edit)
        form.addRow('Quantity', self._qty_spin)
        form.addRow('Unit', self._unit_combo)

        self.layout().addLayout(form)
        self.layout().addWidget(self._warn_lbl)
        self.layout().addWidget(self._button_box)

    def accept(self):
        self._warn_lbl.setText('')

        errors = []
        if not self._name_edit.text():
            errors.append('An item name is required')

        if not self._qty_spin.value():
            errors.append('An item quantity is required')

        if errors:
            self._warn_lbl.setText('<br/>'.join(errors))
            return

        self._item.name = self._name_edit.text()
        self._item.quantity = self._qty_spin.value()
        self._item.unit = models.UnitTypes[self._unit_combo.currentText().upper()]

        super().accept()

    @property
    def item(self):
        return self._item


class ComboBoxDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []

    def set_items(self, items):
        self.items = items

    def createEditor(self, widget, option, index):
        editor = QtWidgets.QComboBox(widget)
        editor.addItems(self.items)
        return editor

    def setEditorData(self, editor: QtWidgets.QComboBox, index: QtCore.QModelIndex):
        value = index.model().data(index, QtCore.Qt.EditRole)
        if value:
            editor.setCurrentText(value)

    def setModelData(self, editor: QtWidgets.QComboBox, model: QtCore.QAbstractTableModel, index: QtCore.QModelIndex):
        model.setData(index, editor.currentText(), QtCore.Qt.EditRole)