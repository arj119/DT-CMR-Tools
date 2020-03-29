import csv
import io
import os
from functools import partial

import pandas as pd
from DataAnalysis import DataFrameModel as dfm, DiffusionParameterData as dpd
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFileDialog, QPushButton, QAbstractItemView, QButtonGroup, QCheckBox, \
    QVBoxLayout, QHBoxLayout, QGroupBox, QTableView, QLabel, QTabWidget, QTreeView, QListView
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
        self.combined_patients_summary_data = dpd.DiffusionParameterData()
        self.combined_patient_summary_table = QTableView()
        self.combined_patients = set()
        self.combined_patients_table = QTableView()
        self.patient_data_sets = dict()
        self.patient_regions = dict()
        self.patient_data_UIs = dict()
        self.tabs = QTabWidget()
        self.vbox2 = QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.init_ui()

    #   Initialises UI
    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        load_file_button = QPushButton("Add Patient")
        load_file_button.clicked.connect(self.open_file_dialog)
        load_file_box = QHBoxLayout()
        load_file_box.addWidget(load_file_button, 0, Qt.AlignLeading)
        self.vbox2.addLayout(load_file_box)
        self.hbox.addLayout(self.vbox2)

        self.tabs.setTabBarAutoHide(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setUsesScrollButtons(True)
        self.tabs.tabCloseRequested.connect(lambda index: self.remove_data(index))
        self.hbox.addWidget(self.tabs)

        self.display_combined_patient_summary()

        self.setLayout(self.hbox)
        self.show()

    # Method to add patient data summary to window
    def display_patient_data(self, patient_identifier, data):
        tab = QWidget()
        tab_layout = QHBoxLayout()
        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()
        self.patient_data_UIs[patient_identifier] = [vbox1, vbox2]
        small_hbox = QHBoxLayout()
        title_box = QVBoxLayout()

        # Patient Label
        patient_identifier_label = self.create_title(f'Patient: {patient_identifier}', Qt.AlignCenter)
        title_box.addWidget(patient_identifier_label, 0, Qt.AlignLeft)

        # Combine Button
        combine_button = QPushButton("Combine Data")
        combine_button.setCheckable(True)
        combine_button.clicked[bool].connect(partial(self.combine_data, patient_identifier))
        button_box = QHBoxLayout()
        button_box.addWidget(combine_button, 0, Qt.AlignRight)

        small_hbox.addLayout(title_box)
        small_hbox.addLayout(button_box)
        vbox1.addLayout(small_hbox)

        # Overall Summary Table
        vbox1.addWidget(self.create_label("Diffusion Parameters Data Summary", Qt.AlignCenter))
        summary_table = QTableView()
        summary_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        summary_table.installEventFilter(self)
        summary_table.setWindowTitle(patient_identifier)
        vbox1.addWidget(summary_table)

        # Regions Summary Table
        vbox1.addWidget(self.create_label("Selected Regions Summary", Qt.AlignCenter))
        regions_summary_table = QTableView()
        regions_summary_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        regions_summary_table.installEventFilter(self)
        vbox1.addWidget(regions_summary_table)

        # Regions Selection
        region_select_buttons = QButtonGroup()
        region_select_buttons.setExclusive(False)

        vbox2.addStretch(1)
        self.create_region_selection(vbox2, region_select_buttons, regions_summary_table, patient_identifier)
        self.load_table_view(data, summary_table)
        tab_layout.addLayout(vbox1)
        tab_layout.addLayout(vbox2)
        tab.setLayout(tab_layout)
        self.tabs.addTab(tab, patient_identifier)

    # Creates a title object
    def create_title(self, text, alignment):
        label = self.create_label(text, alignment)
        label.setStyleSheet("font-weight: bold; font-size: 16pt")
        return label

    # Creates a label object
    def create_label(self, text, alignment):
        label = QLabel()
        label.setText(text)
        label.setAlignment(alignment)
        label.setStyleSheet("font-size: 13pt")
        return label

    #   Creates region selection buttons
    def create_region_selection(self, widgetBox, buttonGroup, region_summary_table, patient_identifier):
        box = QGroupBox("Regions")
        box.setStyleSheet("QGroupBox { border: 1px solid black;}")

        vbox = QVBoxLayout()
        vbox.addSpacing(20)

        # Create check box buttons
        hbox = QHBoxLayout()
        for i in range(0, 12):
            check_box = QCheckBox(str(i + 1))
            check_box.clicked.connect(
                partial(self.update_selected_region_summary, buttonGroup, region_summary_table, patient_identifier))
            vbox.addWidget(check_box)
            buttonGroup.addButton(check_box, i)
        hbox.addLayout(vbox)

        box.setLayout(hbox)
        widgetBox.addWidget(box)
        widgetBox.addStretch(1)

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
    def update_selected_region_summary(self, region_buttons, region_summary_table, patient_identifier):
        regions = [i for i, button in enumerate(region_buttons.buttons()) if button.isChecked()]

        regions_summary = self.patient_data_sets[patient_identifier].get_regions_summary(regions, patient_identifier)
        self.patient_regions[patient_identifier] = regions
        model = dfm.DataFrameModel(regions_summary)

        region_summary_table.setModel(model)
        region_summary_table.resizeColumnsToContents()
        self.update_combined()

    #   Loads data into table view
    def load_table_view(self, data, table):
        model = dfm.DataFrameModel(data)
        table.setModel(model)
        table.resizeColumnsToContents()
        table.show()
        return self.vbox2

    # Displays combined patient summary section
    def display_combined_patient_summary(self):
        patient_identifier_label = self.create_title("Combined Patient Summary", Qt.AlignCenter)
        self.combined_patient_summary_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.combined_patient_summary_table.installEventFilter(self)
        self.vbox2.addWidget(patient_identifier_label)
        self.vbox2.addWidget(self.combined_patient_summary_table)

        vbox = QVBoxLayout()
        vbox.addWidget(self.create_title('Combined Patient Summary Breakdown', Qt.AlignCenter))
        vbox.addWidget(self.combined_patients_table)
        self.combined_patients_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.combined_patients_table.doubleClicked.connect(self.open_patient_tab)
        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addStretch(0)

        self.vbox2.addLayout(hbox)
        self.update_combined()

    def open_patient_tab(self):
        selection = self.combined_patients_table.selectedIndexes()

        if selection:
            self.tabs.setCurrentWidget(self.tabs.findChild(QWidget, str(selection[0].data())))

    # Updates combined patient summary section
    def update_combined(self):
        combined_patient_regions = {patient_identifier: regions for (patient_identifier, regions) in
                                    self.patient_regions.items()
                                    if patient_identifier in self.combined_patients}

        # Combined patient summary table update
        summary = self.combined_patients_summary_data.get_combined_patient_regions_summary(combined_patient_regions)
        self.load_table_view(summary, self.combined_patient_summary_table)

        # Combined patients table update
        data = [[patient_identifier, [i + 1 for i in regions]] for (patient_identifier, regions) in
                combined_patient_regions.items()]
        self.load_table_view(pd.DataFrame(data, columns=['Patients', 'Regions']),
                             self.combined_patients_table)

    # Removes patient data
    def remove_data(self, index):
        patient_identifier = self.tabs.tabText(index)
        print(patient_identifier)
        self.patient_data_sets.pop(patient_identifier)
        if patient_identifier in self.patient_regions:
            self.patient_regions.pop(patient_identifier)
        self.combined_patients_summary_data.remove_patient_data(patient_identifier)
        for box in self.patient_data_UIs[patient_identifier]:
            self.clear_layout(box)
        # self.tabs.currentWidget().deleteLater()
        self.tabs.removeTab(index)
        self.update_combined()

    # Combines patient data and presents summary
    def combine_data(self, patient_identifier, toggled):
        if toggled:
            self.combined_patients.add(patient_identifier)
        else:
            self.combined_patients.remove(patient_identifier)
        self.update_combined()

    # Clears UI Layout of widgets and sub-layouts
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clear_layout(child.layout())

    # Resizes tabs as number increases
    def resize_tabs(self):
        count = self.tabs.count()
        font_size = 12 - (count // 5) * 3
        self.tabs.setStyleSheet('QTabBar { font-size: ' + str(font_size) + 'pt; }')

    #   Allows user to open directories
    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.ShowDirsOnly
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setOptions(options)
        file_view = dialog.findChild(QListView, 'listView')

        # to make it possible to select multiple directories:
        if file_view:
            file_view.setSelectionMode(QAbstractItemView.MultiSelection)
        f_tree_view = dialog.findChild(QTreeView)
        if f_tree_view:
            f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)

        if dialog.exec():
            paths = dialog.selectedFiles()
            for patient_data_directory in paths:
                try:
                    patient_identifier = os.path.basename(patient_data_directory)
                    if patient_identifier not in self.patient_data_sets:
                        data = loadmat(patient_data_directory + file_extension)

                        self.patient_data_sets[patient_identifier] = dpd.DiffusionParameterData()
                        summary = self.patient_data_sets[patient_identifier].add_data(data, patient_identifier)
                        self.patient_regions[patient_identifier] = []
                        self.display_patient_data(patient_identifier, summary)
                        self.combined_patients_summary_data.add_data(data, patient_identifier)
                except:
                    error_dialog = QtWidgets.QErrorMessage()
                    error_dialog.showMessage(f'File path error: {patient_data_directory} does not contain diffusion '
                                             f'parameters')
                    error_dialog.exec_()


if __name__ == '__main__':
    ctx = ApplicationContext()
    ex = App()
    ctx.app.exec_()
