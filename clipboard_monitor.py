
import hashlib

from PySide6.QtCore import QObject, QTimer, Signal, QByteArray, QBuffer, QIODevice
from PySide6.QtGui import QGuiApplication


class ClipboardMonitor(QObject):
    new_item = Signal(str, object, str)

    def __init__(self):
        super().__init__()

        self.clipboard = QGuiApplication.clipboard()
        self.previous = ""

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start(500)

    def check_clipboard(self):
        image = self.clipboard.image()

        # Check for an image first
        if not image.isNull():
            image = image.copy()

            buffer_data = QByteArray()
            buffer = QBuffer(buffer_data)
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            image.save(buffer, "PNG")
            buffer.close()

            fingerprint = hashlib.sha256(
                bytes(buffer_data)
            ).hexdigest()

            if fingerprint != self.previous_fingerprint:
                self.previous_fingerprint = fingerprint
                self.new_item.emit("image", image, fingerprint)

            return

        current = self.clipboard.text()

        if not current.strip():
            self.previous_fingerprint = None
            return

        fingerprint = hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

        if fingerprint != self.previous_fingerprint:
            self.previous_fingerprint = fingerprint
            self.new_item.emit("text", text, fingerprint)