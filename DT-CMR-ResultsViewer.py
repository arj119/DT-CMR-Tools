import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QTableView, QPushButton, QAbstractItemView
from scipy.io import loadmat
from DataAnalysis import DiffusionParameterData
from DataAnalysis import DataFrameModel


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'CMR Results Viewer'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.vLayout = QtWidgets.QVBoxLayout(self)
        self.hLayout = QtWidgets.QHBoxLayout()
        self.tableview = QtWidgets.QTableView(self)
        self.tableview.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.vLayout.addWidget(self.tableview)
        loadBtn = QtWidgets.QPushButton("Select File", self)
        loadBtn.clicked.connect(self.openFileNameDialog)
        self.hLayout.addWidget(loadBtn)
        self.vLayout.addLayout(self.hLayout)
        self.show()

    def loadSummaryDataFrame(self, df):
        model = DataFrameModel.DataFrameModel(df)
        self.tableview.setModel(model)
        self.tableview.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableview.resizeColumnsToContents()
        self.tableview.show()


    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                                  "MAT Files (*.mat)", options=options)
        if fileName:
            data = loadmat(fileName)
            diffusion_parameters = DiffusionParameterData.DiffusionParameterData(data)
            self.loadSummaryDataFrame(diffusion_parameters.summary)

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "Open files", "",
                                                "MAT Files (*.mat)", options=options)
        if files:
            print(files)

    def saveFileDialog(self):
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
