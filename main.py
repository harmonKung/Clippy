
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
)

from PySide6.QtCore import QStandardPaths, Qt
from PySide6.QtGui import QImage, QPixmap, QIcon

from clipboard_monitor import ClipboardMonitor
from database import ClipboardDatabase


class ClipboardManager(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ClipVault")
        self.resize(750, 550)

        data_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )

        self.db = ClipboardDatabase(data_dir)
        self.saved_fingerprints = set()

        self.setStyleSheet("""
            QMainWindow {
                background-color: #111318;
            }

            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }

            QLineEdit {
                background-color: #20232b;
                color: white;
                border: 1px solid #343945;
                border-radius: 8px;
                padding: 12px;
            }

            QListWidget {
                background-color: #191c23;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px;
            }

            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #30343d;
            }

            QListWidget::item:selected {
                background-color: #343c52;
            }
        """)

        container = QWidget()
        layout = QVBoxLayout(container)

        title = QLabel("ClipVault")
        subtitle = QLabel("Your clipboard history")

        subtitle.setStyleSheet(
            "font-size: 13px; color: #9299a8;"
        )

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search clipboard history...")

        self.history = QListWidget()

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(15)
        layout.addWidget(self.search)
        layout.addWidget(self.history)

        self.setCentralWidget(container)

        self.load_history()

        self.monitor = ClipboardMonitor()
        self.monitor.new_item.connect(self.add_item)

        self.search.textChanged.connect(self.filter_items)
        self.history.itemClicked.connect(self.copy_item)

    def load_history(self):
        for row in self.db.get_history():
            kind, content, image_path, created_at, fingerprint = row

            self.saved_fingerprints.add(fingerprint)

            if kind == "image":
                image = QImage(image_path)

                if image.isNull():
                    continue

                pixmap = QPixmap.fromImage(
                    image.scaled(
                        64, 64,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )

                item = QListWidgetItem(
                    QIcon(pixmap),
                    f"Image snapshot  |  {created_at}"
                )

                item.setData(Qt.ItemDataRole.UserRole,
                             ("image", image_path))

            else:
                item = QListWidgetItem(content)
                item.setData(Qt.ItemDataRole.UserRole,
                             ("text", content))

            self.history.addItem(item)

    def add_item(self, kind, payload, fingerprint):

        if fingerprint in self.saved_fingerprints:
            return

        self.saved_fingerprints.add(fingerprint)

        if kind == "image":
            self.db.add_image(payload, fingerprint)

            pixmap = QPixmap.fromImage(
                payload.scaled(
                    64, 64,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )

            item = QListWidgetItem(
                QIcon(pixmap),
                "Image snapshot"
            )

            image_path = str(
                self.db.image_dir / f"{fingerprint}.png"
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                ("image", image_path)
            )

        else:
            self.db.add_text(payload, fingerprint)

            item = QListWidgetItem(payload)
            item.setData(
                Qt.ItemDataRole.UserRole,
                ("text", payload)
            )

        self.history.insertItem(0, item)

    def filter_items(self, query):
        for i in range(self.history.count()):
            item = self.history.item(i)

            item.setHidden(
                query.lower() not in item.text().lower()
            )

    def copy_item(self, item):
        kind, content = item.data(
            Qt.ItemDataRole.UserRole
        )

        if kind == "text":
            QApplication.clipboard().setText(content)

        elif kind == "image":
            image = QImage(content)

            if not image.isNull():
                QApplication.clipboard().setImage(image)

    def closeEvent(self, event):
        self.db.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setOrganizationName("ClipVault")
    app.setApplicationName("ClipVault")

    window = ClipboardManager()
    window.show()

    sys.exit(app.exec())
