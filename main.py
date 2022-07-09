# /bin/env python3
import os
import sys
import zipfile

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem
from PyQt5.uic import loadUi


class CBZArchive(zipfile.ZipFile):
    def __init__(self, filename):
        super().__init__(filename)

        self.pages_count = len(self.filelist)

    def cbz_metadata_parse(self):
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.cbz_archive = object()
        self.current_page_index = 0

        self.init_ui()
        self.init_events()

        self.load_cbz_archive()
        self.fill_gui()

        self.show()

    def init_ui(self):
        loadUi(os.path.join(os.path.dirname(__file__), "ui.ui"), self)

    def init_events(self):
        self.listWidget.currentItemChanged.connect(self.when_current_item_changed)
        self.pushButton.clicked.connect(self.move_to_previous_page)
        self.pushButton_2.clicked.connect(self.move_to_next_page)

    def load_cbz_archive(self):
        self.cbz_archive = CBZArchive("/home/seigneurfuo/NAS/Temporaire/Megami Magazine/Megami #108 2009-05.cbz")

    def fill_gui(self):
        self.fill_pages_counter()
        self.fill_pages_list()

    def fill_pages_counter(self):
        msg = "{} Pages".format(self.cbz_archive.pages_count)
        self.label_2.setText(msg)

    def move_to_previous_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1

            self.listWidget.setCurrentRow(self.current_page_index)
            self.display_page(self.current_page_index)

    def move_to_next_page(self):
        if self.current_page_index + 1 < self.cbz_archive.pages_count:
            self.current_page_index -= 1

            self.listWidget.setCurrentRow(self.current_page_index)
            self.display_page(self.current_page_index)

    def fill_pages_list(self):
        for index, file_data in enumerate(self.cbz_archive.filelist):
            filename = str(file_data.filename)
            item = QListWidgetItem(filename)
            item.setData(Qt.UserRole, index)

            self.listWidget.addItem(item)

        self.listWidget.setCurrentRow(0)

    def when_current_item_changed(self):
        item = self.listWidget.currentItem()
        index = int(item.data(Qt.UserRole))

        self.display_page(index)

    def display_page(self, index):
        self.current_page_index = index
        file = self.cbz_archive.filelist[index].filename

        qpixmap = self.file_data_to_qpixmap(file)
        self.label.setPixmap(qpixmap)
        self.label.setScaledContents(True)

    def file_data_to_qpixmap(self, file):
        filename, extension = os.path.splitext(file)
        file_data = self.cbz_archive.read(file)
        qpixmap = QPixmap()
        qpixmap.loadFromData(file_data, extension)

        return qpixmap


class Application(QApplication):
    def __init__(self, args):
        super().__init__(args)

        self.name = "MyAnimeManager 3"
        self.version = "DEV"
        self.description = self.tr("Un gestionnaire de séries multiplateforme écrit en Python3 et Qt5")

        self.setApplicationName(self.name)
        self.setApplicationDisplayName(self.name)
        self.setApplicationVersion(self.version)

        self.mainwindow = MainWindow()
        self.mainwindow.show()


if __name__ == "__main__":
    import cgitb

    cgitb.enable(format='text')

    application = Application(sys.argv)
    application.exec_()
