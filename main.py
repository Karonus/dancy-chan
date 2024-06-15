import os.path
import sys

from PyQt5 import QtWidgets, QtCore, QtGui


class GIFShower(QtWidgets.QWidget):
    def __init__(self, initial_path):
        super().__init__()

        self.gif_path = initial_path
        self.pin_status = False
        self.bottom_status = False
        self.old_pos = None
        self.mouse_pos = None

        self.setWindowTitle("GIF Shower")
        self.setAccessibleName("GIF Shower")
        self.setWindowIcon(QtGui.QIcon(self.gif_path))

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.movie = QtGui.QMovie(self.gif_path)
        self.movie.frameChanged.connect(self.repaint)
        self.movie.start()

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.tray = QtWidgets.QSystemTrayIcon()
        self.tray.setIcon(QtGui.QIcon(self.gif_path))
        self.tray.setVisible(True)
        self.tray.activated.connect(self.on_tray_activated)

    def paintEvent(self, event):
        current_frame = self.movie.currentPixmap()
        frame_rect = current_frame.rect()
        self.setFixedSize(frame_rect.width(), frame_rect.height())

        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, current_frame)

    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = event.globalPos() - self.old_pos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()
        self.mouse_pos = QtCore.QPointF(event.x(), event.y())

    def show_context_menu(self, position: QtCore.QPoint, is_from_tray=False):
        context_menu = QtWidgets.QMenu(self)
        change_gif_action = context_menu.addAction("Изменить гифку")
        pin_action = context_menu.addAction("Открепить" if self.pin_status else "Закрепить")
        close_action = context_menu.addAction("Закрыть")

        action = context_menu.exec_(position if is_from_tray else self.mapToGlobal(position))

        if action == change_gif_action:
            self.change_gif()
        elif action == pin_action:
            self.toggle_pin()
        elif action == close_action:
            self.close()
            sys.exit()

    def on_tray_activated(self, reason):
        if reason == 2:
            self.toggle_pin()
        else:
            self.show_context_menu(QtGui.QCursor.pos(), is_from_tray=True)

    def change_gif(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите гифку", "", "GIF Files (*.gif)")
        if not path:
            return

        self.gif_path = path

        self.movie.stop()
        self.movie.setFileName(self.gif_path)
        self.movie.start()

        self.setWindowIcon(QtGui.QIcon(self.gif_path))

    def toggle_pin(self):
        self.setWindowFlag(
            QtCore.Qt.WindowStaysOnTopHint,
            not bool(self.windowFlags() & QtCore.Qt.WindowStaysOnTopHint),
        )
        self.show()

        self.pin_status = not self.pin_status

    def toggle_bottom(self):
        self.setWindowFlag(
            QtCore.Qt.WindowStaysOnBottomHint,
            not bool(self.windowFlags() & QtCore.Qt.WindowStaysOnBottomHint),
        )
        self.show()

        self.bottom_status = not self.bottom_status


if __name__ == "__main__":
    if not os.path.isfile("default.gif"):
        exit()

    app = QtWidgets.QApplication(sys.argv)

    gif_path = "default.gif"
    gif_display = GIFShower(gif_path)
    gif_display.show()

    sys.exit(app.exec_())
