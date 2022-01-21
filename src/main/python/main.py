import csv
import io
import os
import sys
from functools import partial

import pandas as pd
from DataAnalysis import DataFrameModel as dfm, DiffusionParameterData as dpd
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFileDialog, QPushButton, QAbstractItemView, QButtonGroup, QCheckBox, \
    QVBoxLayout, QHBoxLayout, QGroupBox, QTableView, QLabel, QTabWidget, QTreeView, QListView, QGridLayout,QApplication
from scipy.io import loadmat


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'DT-CMR RAT'
        self.left = 10
        self.top = 10
        self.width = 1920
        self.height = 1080
        self.combined_patients_summary_data = dpd.DiffusionParameterData()
        self.combined_selected_regions_table = QTableView()
        self.combined_global_table = QTableView()
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

        small_hbox.addLayout(title_box)
        vbox1.addLayout(small_hbox)

        # Overall Summary Table
        vbox1.addWidget(self.create_label("Global", Qt.AlignCenter))
        summary_table = QTableView()
        summary_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        summary_table.installEventFilter(self)
        vbox1.addWidget(summary_table)

        # Regions Summary Table
        vbox1.addWidget(self.create_label("Selected Regions", Qt.AlignCenter))
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

        # Create inversion button
        inversion_button = QPushButton('Invert')
        inversion_button.clicked.connect(
            partial(self.invert_buttons, buttonGroup, region_summary_table, patient_identifier))

        vbox.addWidget(inversion_button)
        hbox.addLayout(vbox)
        box.setLayout(hbox)
        widgetBox.addWidget(box)
        widgetBox.addStretch(1)

    # Inverts buttons for region selection
    def invert_buttons(self, regions_buttons, region_summary_table, patient_identifier):
        for button in regions_buttons.buttons():
            button.toggle()
            button.repaint()
        self.update_selected_region_summary(regions_buttons, region_summary_table, patient_identifier)

    #   Updates selected region summary table
    def update_selected_region_summary(self, region_buttons, region_summary_table, patient_identifier):
        regions = [i for i, button in enumerate(region_buttons.buttons()) if button.isChecked()]
        regions_summary = self.patient_data_sets[patient_identifier].get_regions_summary(regions, patient_identifier)
        self.patient_regions[patient_identifier] = regions
        model = dfm.DataFrameModel(regions_summary)

        region_summary_table.setModel(model)
        region_summary_table.resizeColumnsToContents()
        region_summary_table.repaint()
        self.update_combined()

    #   Copy event
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

    #   Loads data into table view
    def load_table_view(self, data, table):
        model = dfm.DataFrameModel(data)
        table.setModel(model)
        table.resizeColumnsToContents()
        table.repaint()
        return self.vbox2

    # Displays combined patient summary section
    def display_combined_patient_summary(self):
        # Combined global table
        combined_global_label = self.create_title('Global Combined', Qt.AlignCenter)
        self.combined_global_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.combined_global_table.installEventFilter(self)
        self.vbox2.addWidget(combined_global_label)
        self.vbox2.addWidget(self.combined_global_table)

        # Combined selected regions table
        grid = QGridLayout()
        combined_regions_box = QVBoxLayout()
        combine_regions_label = self.create_title('Selected Regions Combined', Qt.AlignCenter)
        self.combined_selected_regions_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.combined_selected_regions_table.installEventFilter(self)
        combined_regions_box.addWidget(combine_regions_label)
        combined_regions_box.addWidget(self.combined_selected_regions_table)
        grid.addLayout(combined_regions_box, 0, 0, 1, 1)

        # Combined selected regions breakdown table
        vbox = QVBoxLayout()
        vbox.addWidget(self.create_title('Selected Regions Breakdown', Qt.AlignCenter))
        vbox.addWidget(self.combined_patients_table)
        self.combined_patients_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.combined_patients_table.clicked.connect(self.open_patient_tab)
        grid.addLayout(vbox, 0, 4, 1, 3)

        self.vbox2.addLayout(grid)
        self.update_combined()
        self.update_combined_global()

    # Open selected patient tab
    def open_patient_tab(self):
        selection = self.combined_patients_table.selectedIndexes()
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == selection[0].data():
                self.tabs.setCurrentIndex(i)

    # Combined global regions table update
    def update_combined_global(self):
        summary = self.combined_patients_summary_data.get_combined_global_summary()
        self.load_table_view(summary, self.combined_global_table)

    # Updates combined patient summary section
    def update_combined(self):
        # Combined selected regions table update
        summary = self.combined_patients_summary_data.get_combined_patient_regions_summary(self.patient_regions)
        self.load_table_view(summary, self.combined_selected_regions_table)

        # Combined patients table update
        data = [[patient_identifier, [i + 1 for i in regions]] for (patient_identifier, regions) in
                self.patient_regions.items() if len(regions) > 0]
        self.load_table_view(pd.DataFrame(data, columns=['Patients', 'Regions']),
                             self.combined_patients_table)

    # Removes patient data
    def remove_data(self, index):
        patient_identifier = self.tabs.tabText(index)
        self.patient_data_sets.pop(patient_identifier)
        if patient_identifier in self.patient_regions:
            self.patient_regions.pop(patient_identifier)
        self.combined_patients_summary_data.remove_patient_data(patient_identifier)
        for box in self.patient_data_UIs[patient_identifier]:
            self.clear_layout(box)
        self.tabs.removeTab(index)
        self.update_combined()
        self.update_combined_global()

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

    # Loads data to window
    def load_data(self, patient_identifier, data):
        self.patient_data_sets[patient_identifier] = dpd.DiffusionParameterData()
        summary = self.patient_data_sets[patient_identifier].add_data(data, patient_identifier)
        self.patient_regions[patient_identifier] = []
        self.display_patient_data(patient_identifier, summary)
        self.combined_patients_summary_data.add_data(data, patient_identifier)
        self.update_combined_global()
        self.tabs.repaint()

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
            file_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        f_tree_view = dialog.findChild(QTreeView)
        if f_tree_view:
            f_tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)

        if dialog.exec():
            paths = dialog.selectedFiles()
            for patient_data_directory in paths:
                patient_identifier = os.path.basename(patient_data_directory)
                if patient_identifier not in self.patient_data_sets:
                    dp_file_path = os.path.join(patient_data_directory, 'result_images', 'exported_data',
                                                'diffusion_parameters.mat')
                    if os.path.exists(dp_file_path):
                        data = loadmat(dp_file_path)
                        self.load_data(patient_identifier, data)
                    else:
                        error_dialog = QtWidgets.QErrorMessage()
                        error_dialog.showMessage(
                            f'File path error: {patient_data_directory} does not contain diffusion '
                            f'parameters')
                        error_dialog.exec_()


if __name__ == '__main__':
    ctx_app = QApplication([])
    ex = App()
    exit_code = ctx_app.exec_()
    sys.exit(exit_code)
