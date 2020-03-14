import csv
import io
import sys

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QPushButton, QAbstractItemView, QButtonGroup, QCheckBox, \
    QVBoxLayout, QHBoxLayout, QGroupBox
from scipy.io import loadmat

from DataAnalysis import DataFrameModel
from DataAnalysis import DiffusionParameterData

file_extension = '/result_images/exported_data/diffusion_parameters.mat'


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Diffusion Parameter Results Viewer'
        self.left = 10
        self.top = 10
        self.width = 700
        self.height = 700
        self.diffusion_parameters = DiffusionParameterData.DiffusionParameterData()
        self.summary_table = QtWidgets.QTableView()
        self.selected_region_summary_table = QtWidgets.QTableView()
        self.region_selection_buttons = QButtonGroup()
        self.vbox2 = QVBoxLayout()
        self.init_ui()

    #   Initialises UI
    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #   Initialises UI
        self.summary_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.summary_table.installEventFilter(self)

        self.selected_region_summary_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.selected_region_summary_table.installEventFilter(self)
        self.selected_region_summary_table.hide()

        self.region_selection_buttons.setExclusive(False)

        load_file_button = QPushButton("Select File")
        load_file_button.move(100, 100)
        load_file_button.clicked.connect(self.open_file_dialog)

        vbox1 = QVBoxLayout()
        hbox1 = QHBoxLayout()

        vbox1.addWidget(self.summary_table)
        vbox1.addWidget(self.selected_region_summary_table)
        self.vbox2.addWidget(load_file_button)
        self.vbox2.addStretch(1)
        hbox1.addLayout(vbox1)
        hbox1.addLayout(self.vbox2)

        self.setLayout(hbox1)
        self.show()

    #   Creates region selection buttons
    def create_region_selection(self):
        box = QGroupBox("Regions")
        box.setStyleSheet("QGroupBox { border: 1px solid black;}")
        vbox = QVBoxLayout()
        vbox.addSpacing(20)
        for i in range(0, 12):
            check_box = QCheckBox(str(i + 1))
            check_box.clicked.connect(self.update_selected_region_summary)
            vbox.addWidget(check_box)
            self.region_selection_buttons.addButton(check_box, i)
        box.setLayout(vbox)
        self.vbox2.addWidget(box)
        self.vbox2.addStretch(1)

    #   Creates region selection buttons
    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.KeyPress and
                event.matches(QtGui.QKeySequence.Copy)):
            self.copy_selection(source)
            return True
        return super(App, self).eventFilter(source, event)

    #   Allows user to copy their table selection
    def copy_selection(self, tableview):
        selection = tableview.selectedIndexes()
        if selection:
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table = [[''] * colcount for _ in range(rowcount)]
            for index in selection:
                row = index.row() - rows[0]
                column = index.column() - columns[0]
                table[row][column] = index.data()
            stream = io.StringIO()
            csv.writer(stream, delimiter='\t').writerows(table)
            QtWidgets.qApp.clipboard().setText(stream.getvalue())

    #   Updates selected region summary table
    def update_selected_region_summary(self):
        segments = [i for i, button in enumerate(self.region_selection_buttons.buttons()) if button.isChecked()]
        if len(segments) == 0:
            self.selected_region_summary_table.hide()
        else:
            segment_summary = self.diffusion_parameters.get_regions_summary(segments)
            model = DataFrameModel.DataFrameModel(segment_summary)
            self.selected_region_summary_table.setModel(model)
            self.selected_region_summary_table.resizeColumnsToContents()
            self.selected_region_summary_table.show()

    #   Loads data summary
    def load_summary_table(self, summary):
        model = DataFrameModel.DataFrameModel(summary)
        self.summary_table.setModel(model)
        self.summary_table.resizeColumnsToContents()
        self.summary_table.show()

    #   Allows user to open a file
    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.ShowDirsOnly
        dialog = QFileDialog(self)
        patient_data_directory = dialog.getExistingDirectory(self, 'Open Patient Data', options=options)
        if patient_data_directory != '':
            data = loadmat(patient_data_directory + file_extension)
            summary = self.diffusion_parameters.set_data(data)
            self.load_summary_table(summary)
            if not self.region_buttons_show:
                self.create_region_selection()
            else:
                self.update_selected_region_summary()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
