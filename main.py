# /bin/env python3

# Exemples: https://gist.github.com/acbetter/32c575803ec361c3e82064e60db4e3e0

import os
import sys
import zipfile

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QSizePolicy, QLabel
from PyQt5.uic import loadUi


class CBZArchive(zipfile.ZipFile):
    def __init__(self, filename):
        super().__init__(filename)

        self.short_filename = os.path.basename(self.filename)
        self.pages_list = []
        self.get_pages_list()
        self.pages_count = len(self.filelist)

    def get_pages_list(self):
        allowed_extensions = (".jpg", ".jpeg", ".jp2", ".png", ".bmp", ".gif")
        for item in self.filelist:
            filename, extension = os.path.splitext(item.filename)

            if extension in allowed_extensions:
                self.pages_list.append(item.filename)

    def cbz_metadata_parse(self):
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.cbz_archive = None
        self.current_page_index = 0

        self.init_ui()
        self.init_events()
        print(sys.argv)
        if len(sys.argv) > 1:
            filename = sys.argv[1]
            self.load_cbz_archive(filename)
            self.fill_gui()

        self.show()

    def init_ui(self):
        loadUi(os.path.join(os.path.dirname(__file__), "ui.ui"), self)

        # Image viewer
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.label.setScaledContents(True)
        #self.label = QLabel()
        #self.label.setMinimalSize()

        # Taille QListWidget



    def init_events(self):
        #self.listWidget.currentItemChanged.connect(self.when_current_item_changed)
        self.pushButton.clicked.connect(self.move_to_previous_page)
        self.pushButton_2.clicked.connect(self.move_to_next_page)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.move_to_previous_page()

        if event.key() == Qt.Key_Right:
            self.move_to_next_page()

    def open(self):
        pass

    def load_cbz_archive(self, filename):
        if os.path.isfile(filename):
            self.cbz_archive = CBZArchive(filename)
            self.cbz_archive.get_pages_list()

    def fill_gui(self):
        self.set_window_title()
        self.fill_pages_counter()
        self.fill_pages_list()

    def set_window_title(self):
        current_page = self.current_page_index + 1
        msg = "[Page {} / {}] {}".format(current_page, self.cbz_archive.pages_count, self.cbz_archive.short_filename)
        self.setWindowTitle(msg)

    def fill_pages_counter(self):
        msg = "{} Pages".format(self.cbz_archive.pages_count)
        self.label_2.setText(msg)

    def move_to_previous_page(self):
        if self.cbz_archive:
            if self.current_page_index > 0:
                self.current_page_index -= 1

                #self.listWidget.setCurrentRow(self.current_page_index)
                self.display_page(self.current_page_index)
                self.set_window_title()

    def move_to_next_page(self):
        if self.cbz_archive:
            if self.current_page_index + 1 < self.cbz_archive.pages_count:
                self.current_page_index += 1

                #self.listWidget.setCurrentRow(self.current_page_index)
                self.display_page(self.current_page_index)
                self.set_window_title()

    def fill_pages_list(self):
        for index, file_data in enumerate(self.cbz_archive.pages_list):
            filename = file_data
            item = QListWidgetItem(filename)
            item.setData(Qt.UserRole, index)

            #self.listWidget.addItem(item)

        #self.listWidget.setCurrentRow(0)
        if self.cbz_archive.pages_count >0 :
            self.display_page(0)

    def when_current_item_changed(self):
        item = self.listWidget.currentItem()
        index = int(item.data(Qt.UserRole))

        self.display_page(index)
        self.set_window_title()

    def display_page(self, index):
        self.current_page_index = index
        file = self.cbz_archive.pages_list[index]

        qpixmap = self.file_data_to_qpixmap(file)
        resized_qpixmap = qpixmap.scaled(self.label.width(), self.label.height(), Qt.KeepAspectRatio)
        self.label.setPixmap(resized_qpixmap)

    def file_data_to_qpixmap(self, file):
        filename, extension = os.path.splitext(file)
        data = self.cbz_archive.read(file)
        qpixmap = QPixmap()
        qpixmap.loadFromData(data, extension)

        return qpixmap


class Application(QApplication):
    def __init__(self, args):
        super().__init__(args)

        self.setApplicationName("")
        self.setApplicationDisplayName("")
        self.setApplicationVersion("")

        self.mainwindow = MainWindow()
        self.mainwindow.show()


if __name__ == "__main__":
    import cgitb

    cgitb.enable(format='text')

    application = Application(sys.argv)
    application.exec_()
