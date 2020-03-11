import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QPushButton, QAbstractItemView, QButtonGroup, QCheckBox, \
    QVBoxLayout, QHBoxLayout, QGroupBox
from scipy.io import loadmat
from DataAnalysis import DiffusionParameterData
from DataAnalysis import DataFrameModel


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Diffusion Parameter Results Viewer'
        self.left = 10
        self.top = 10
        self.width = 700
        self.height = 700
        self.diffusion_parameters = DiffusionParameterData.DiffusionParameterData()
        self.overall_summary_table = QtWidgets.QTableView()
        self.selected_segments_summary_table = QtWidgets.QTableView()
        self.segment_button_group = QButtonGroup()
        self.vbox2 = QVBoxLayout()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.overall_summary_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.selected_segments_summary_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.selected_segments_summary_table.hide()

        self.segment_button_group.setExclusive(False)

        load_file_button = QPushButton("Select File")
        load_file_button.move(100, 100)
        load_file_button.clicked.connect(self.open_file_dialog)

        vbox1 = QVBoxLayout()
        hbox1 = QHBoxLayout()

        vbox1.addWidget(self.overall_summary_table)
        vbox1.addWidget(self.selected_segments_summary_table)
        self.vbox2.addWidget(load_file_button)
        self.vbox2.addStretch(1)
        hbox1.addLayout(vbox1)
        hbox1.addLayout(self.vbox2)

        self.setLayout(hbox1)
        self.show()

    def create_segment_buttons(self):
        box = QGroupBox("Regions")
        box.setStyleSheet("QGroupBox { border: 1px solid black;}")
        vbox = QVBoxLayout()
        vbox.addSpacing(20)
        for i in range(0, 12):
            check_box = QCheckBox(str(i + 1))
            check_box.clicked.connect(self.update_segment_summary)
            vbox.addWidget(check_box)
            self.segment_button_group.addButton(check_box, i)
        box.setLayout(vbox)
        self.vbox2.addWidget(box)
        self.vbox2.addStretch(1)

    def update_segment_summary(self):
        segments = [i for i, button in enumerate(self.segment_button_group.buttons()) if button.isChecked()]
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
