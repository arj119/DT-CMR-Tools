import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QPushButton, QAbstractItemView, QGridLayout, \
    QButtonGroup, QCheckBox, QVBoxLayout
from scipy.io import loadmat
from DataAnalysis import DiffusionParameterData
from DataAnalysis import DataFrameModel


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'CMR Results Viewer'
        self.left = 10
        self.top = 10
        self.width = 800
        self.height = 500
        self.diffusion_parameters = DiffusionParameterData.DiffusionParameterData()
        self.overall_summary_table = QtWidgets.QTableView()
        self.selected_segments_summary_table = QtWidgets.QTableView()
        self.segment_button_group = QButtonGroup()
        self.grid = QGridLayout()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.overall_summary_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.selected_segments_summary_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.selected_segments_summary_table.hide()

        self.segment_button_group.setExclusive(False)

        load_file_button = QPushButton("Select File")
        load_file_button.move(100, 100)
        load_file_button.clicked.connect(self.open_file_dialog)

        self.grid.setSpacing(10)
        # vbox1 = QVBoxLayout()
        # vbox = QVBoxLayout()
        self.grid.addWidget(self.overall_summary_table, 1, 1, 3, 1)
        self.grid.addWidget(self.selected_segments_summary_table, 8, 1, 7, 1)
        self.grid.addWidget(load_file_button, 1, 2)

        self.setLayout(self.grid)
        self.show()

    # def create_summary_table(self, segments):

    def create_segment_buttons(self):
        for i in range(0,12):
            check_box = QCheckBox(str(i+1))
            check_box.clicked.connect(self.update_segment_summary)
            self.grid.addWidget(check_box, 5 + i, 3)
            self.segment_button_group.addButton(check_box, i)

    def update_segment_summary(self):
        segments = [i for i, button in enumerate(self.segment_button_group.buttons()) if button.isChecked()]
        print(len(segments))
        if len(segments) == 0:
            self.selected_segments_summary_table.hide()
        else:
            segment_summary = self.diffusion_parameters.get_summary_segments(segments)
            model = DataFrameModel.DataFrameModel(segment_summary)
            self.selected_segments_summary_table.setModel(model)
            self.selected_segments_summary_table.resizeColumnsToContents()
            self.selected_segments_summary_table.show()

    def load_summary_data_frame(self, summary):
        model = DataFrameModel.DataFrameModel(summary)
        self.overall_summary_table.setModel(model)
        self.overall_summary_table.resizeColumnsToContents()
        self.overall_summary_table.show()

    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                                  "MAT Files (*.mat)", options=options)
        if fileName:
            data = loadmat(fileName)
            summary = self.diffusion_parameters.add_data(data)
            self.load_summary_data_frame(summary)
            self.create_segment_buttons()

    def save_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
