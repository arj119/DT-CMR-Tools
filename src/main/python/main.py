import csv
import io
import os
from functools import partial

from DataAnalysis import DataFrameModel as dfm, DiffusionParameterData as dpd
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFileDialog, QPushButton, QAbstractItemView, QButtonGroup, QCheckBox, \
    QVBoxLayout, QHBoxLayout, QGroupBox, QTableView, QLabel
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from scipy.io import loadmat

file_extension = '/result_images/exported_data/diffusion_parameters.mat'


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Diffusion Parameter Results Viewer'
        self.left = 10
        self.top = 10
        self.width = 1920
        self.height = 1080
        self.diffusion_parameters = dpd.DiffusionParameterData()
        self.summary_table = QTableView()
        self.selected_region_summary_table = QTableView()
        self.region_selection_buttons = QButtonGroup()
        self.region_buttons_show = False
        self.vbox2 = QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.init_ui()

    #   Initialises UI
    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        load_file_button = QPushButton("Select File")
        load_file_button.move(100, 100)
        load_file_button.clicked.connect(self.open_file_dialog)

        self.vbox2.addWidget(load_file_button)
        self.vbox2.addStretch(1)
        self.hbox.addLayout(self.vbox2)

        self.setLayout(self.hbox)
        self.show()

    # Method to add patient data summary to window
    def display_patient_data(self, identifier, data):
        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()

        patient_identifier_label = self.create_label(identifier, Qt.AlignCenter)
        vbox1.addWidget(patient_identifier_label)

        vbox1.addWidget(self.create_label("Diffusion Parameters Data Summary", Qt.AlignCenter))
        summary_table = QTableView()
        summary_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        summary_table.installEventFilter(self)
        summary_table.setWindowTitle(identifier)
        vbox1.addWidget(summary_table)

        vbox1.addWidget(self.create_label("Selected Regions Summary", Qt.AlignCenter))
        regions_summary_table = QTableView()
        regions_summary_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        regions_summary_table.installEventFilter(self)
        # regions_summary_table.hide()
        vbox1.addWidget(regions_summary_table)

        region_select_buttons = QButtonGroup()
        region_select_buttons.setExclusive(False)

        vbox2.addStretch(1)
        self.create_region_selection(vbox2, region_select_buttons, regions_summary_table)
        self.load_summary_table(data, summary_table)
        self.hbox.addLayout(vbox1)
        self.hbox.addLayout(vbox2)

    def create_label(self, text, alignment):
        label = QLabel()
        label.setText(text)
        label.setAlignment(alignment)
        return label

    #   Creates region selection buttons
    def create_region_selection(self, widgetBox, buttonGroup, region_summary_table):
        box = QGroupBox("Regions")
        box.setStyleSheet("QGroupBox { border: 1px solid black;}")
        vbox = QVBoxLayout()
        vbox.addSpacing(20)
        hbox = QHBoxLayout()
        for i in range(0, 12):
            check_box = QCheckBox(str(i + 1))
            check_box.clicked.connect(partial(self.update_selected_region_summary, buttonGroup, region_summary_table))
            vbox.addWidget(check_box)
            buttonGroup.addButton(check_box, i)
        hbox.addLayout(vbox)
        box.setLayout(hbox)
        widgetBox.addWidget(box)
        widgetBox.addStretch(1)
        self.region_buttons_show = True

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
    def update_selected_region_summary(self, region_buttons, region_summary_table):
        segments = [i for i, button in enumerate(region_buttons.buttons()) if button.isChecked()]
        segment_summary = self.diffusion_parameters.get_regions_summary(segments)
        model = dfm.DataFrameModel(segment_summary)
        region_summary_table.setModel(model)
        region_summary_table.resizeColumnsToContents()

    #   Loads data summary
    def load_summary_table(self, data, summary_table):
        model = dfm.DataFrameModel(data)
        summary_table.setModel(model)
        summary_table.resizeColumnsToContents()
        summary_table.show()
        return self.vbox2

    #   Allows user to open a file
    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.ShowDirsOnly
        dialog = QFileDialog(self)
        patient_data_directory = dialog.getExistingDirectory(self, 'Open Patient Data', options=options)
        if patient_data_directory != '':
            try:
                data = loadmat(patient_data_directory + file_extension)
                summary = self.diffusion_parameters.set_data(data)
                self.display_patient_data(os.path.basename(patient_data_directory), summary)
            except:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage(f'File path error: {patient_data_directory} does not contain diffusion '
                                         f'parameters')
                error_dialog.exec_()


if __name__ == '__main__':
    ctx = ApplicationContext()
    ex = App()
    ctx.app.exec_()
