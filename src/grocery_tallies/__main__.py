import sys

from PySide2 import QtWidgets

from grocery_tallies import GroceryTallies


app = QtWidgets.QApplication(sys.argv)
widget = GroceryTallies()
sys.exit(widget.exec_())
