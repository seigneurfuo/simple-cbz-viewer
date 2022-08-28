# /bin/env python3

# Exemples: https://gist.github.com/acbetter/32c575803ec361c3e82064e60db4e3e0

import os
import sys
import zipfile

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QSizePolicy, QLabel, QFileDialog, QScrollArea, \
    QAction, QMenu
from PyQt5.uic import loadUi


class CBZArchive(zipfile.ZipFile):
    def __init__(self, filename):
        filename = os.path.realpath(filename)
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

    def get_size_string(self):
        pass

    def cbz_metadata_parse(self):
        pass



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.cbz_archive = None
        self.current_page_index = 0
        self.scale_factor = 0.0

        self.init_ui()
        self.init_events()
        print(sys.argv)
        if len(sys.argv) > 1:
            filepath = sys.argv[1]
            self.load_cbz_archive(filepath)
            self.fill_gui()

        self.show()

    def init_ui(self):
        #loadUi(os.path.join(os.path.dirname(__file__), "ui.ui"), self)

        # Image viewer
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.image_label.setScaledContents(True)
        #self.label = QLabel()
        #self.label.setMinimalSize()

        # Taille QListWidget
        self.scroll_area = QScrollArea() # TODO: QGraphicsView ? https://stackoverflow.com/questions/7138113/qt-graphics-view-show-image-widget
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setVisible(False)

        self.setCentralWidget(self.scroll_area)

        self.create_menu_actions()

    def create_menu_actions(self):
        self.file_menu = QMenu("&Fichier", self)
        self.file_menu.addAction(QAction("&Ouvrir...", self, shortcut="Ctrl+O", triggered=self.when_action_open_file_clicked))
        self.file_menu.addAction(QAction("&Close...", self, shortcut="Ctrl+Q", triggered=self.when_action_close_file_clicked))
        self.file_menu.addSeparator()
        self.file_menu.addAction(QAction("&Quitter", self, shortcut="Ctrl+Q", triggered=self.close))

        self.menuBar().addMenu(self.file_menu)

        self.zoom_menu = QMenu("&Zoom", self)
        self.zoom_menu.addAction(QAction("&Zommer...", self, shortcut="Ctrl++", triggered=self.when_action_zoom_in_clicked))
        self.zoom_menu.addAction(QAction("&Dézommer...", self, shortcut="Ctrl+-", triggered=self.when_action_zoom_out_clicked))
        self.zoom_menu.addAction(QAction("Zoom 100%...", self))
        self.zoom_menu.addAction(QAction("&Réinitialiser le zoom...", self, shortcut="Ctrl+0", triggered=self.when_action_zoom_reset_clicked))

        self.menuBar().addMenu(self.zoom_menu)

    def init_events(self):
        #self.listWidget.currentItemChanged.connect(self.when_current_item_changed)
        #self.pushButton.clicked.connect(self.move_to_previous_page)
        #self.pushButton_2.clicked.connect(self.move_to_next_page)

        #self.action_close_file.triggered.connect(self.close_file_action)
        #self.action_quit.triggered.connect(self.close)


        # Permet d'avoir le focus du clavier pour les racourcis sur le fenetre principale (flcèhe gauche et droite)
        self.grabKeyboard()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.move_to_previous_page()

        if event.key() == Qt.Key_Right:
            self.move_to_next_page()

    def when_action_open_file_clicked(self):
        filepath, _filter = QFileDialog.getOpenFileName(filter="Comic Book Archive (*.cbz)")
        print(filepath)
        if filepath:
            self.load_cbz_archive(filepath)
            self.fill_gui()

    def when_action_close_file_clicked(self):
        pass

    def when_action_zoom_in_clicked(self):
        self.scale_image(1.25)

    def when_action_zoom_out_clicked(self):
        self.scale_image(0.8)

    def when_action_zoom_reset_clicked(self):
        self.image_label.adjustSize()
        self.scale_factor = 1.0

    def adjust_scroll_bar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep() / 2)))

    def scale_image(self, factor):
        print(factor)
        self.scale_factor *= factor
        self.image_label.resize(self.scale_factor * self.image_label.pixmap().size())

        self.adjust_scroll_bar(self.scroll_area.horizontalScrollBar(), factor)
        self.adjust_scroll_bar(self.scroll_area.verticalScrollBar(), factor)

        #self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        #self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def load_cbz_archive(self, filename):
        if os.path.isfile(filename):
            self.cbz_archive = CBZArchive(filename)
            self.cbz_archive.get_pages_list()

    def fill_gui(self):
        self.update_window_title()
        self.fill_pages_counter()
        self.fill_pages_list()
        self.scroll_area.setVisible(True)

    def update_window_title(self):
        current_page = self.current_page_index + 1
        msg = "[Page {} / {}] {}".format(current_page, self.cbz_archive.pages_count, self.cbz_archive.short_filename)
        self.setWindowTitle(msg)

    def fill_pages_counter(self):
        msg = "{} Pages | Fichier: {}".format(self.cbz_archive.pages_count, self.cbz_archive.filename)
        self.statusBar().showMessage(msg)

    def move_to_previous_page(self):
        if self.cbz_archive:
            if self.current_page_index > 0:
                self.current_page_index -= 1

                #self.listWidget.setCurrentRow(self.current_page_index)
                self.display_page(self.current_page_index)
                self.update_window_title()

    def move_to_next_page(self):
        if self.cbz_archive:
            if self.current_page_index + 1 < self.cbz_archive.pages_count:
                self.current_page_index += 1

                #self.listWidget.setCurrentRow(self.current_page_index)
                self.display_page(self.current_page_index)
                self.update_window_title()

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
        self.update_window_title()

    def display_page(self, index):
        self.current_page_index = index
        file = self.cbz_archive.pages_list[index]

        qpixmap = self.file_data_to_qpixmap(file)
        #resized_qpixmap = qpixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)
        self.image_label.setPixmap(qpixmap)

        self.when_action_zoom_reset_clicked()

    def file_data_to_qpixmap(self, file):
        filename, extension = os.path.splitext(file)
        data = self.cbz_archive.read(file)
        qpixmap = QPixmap()
        qpixmap.loadFromData(data, extension)

        return qpixmap

    def show_about_window(self):
        pass


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
