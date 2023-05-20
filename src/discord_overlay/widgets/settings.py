from PyQt6.QtCore import (
    QPoint,
    Qt,
)

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,

)
from PyQt6.QtGui import (
    QIcon,
    QGuiApplication,
    QShortcut,
    QPixmap,
    QColor,
    QMouseEvent,
)
from ..controller import Controller
from ..libs.css import EXTENDED_COLORS


class SettingsDialog(QDialog):
    def __init__(self, controller: Controller, parent) -> None:
        super().__init__(parent=parent)
        self.controller = controller
        self.setObjectName(self.__class__.__name__)
        self.setWindowTitle("Settings")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setMinimumWidth(200)
        self.setWindowIcon(QIcon("images:icon.png"))
        self.old_pos = self.pos()
        self.init_ui()
        self.center()
        QShortcut("Ctrl+w", self).activated.connect(self.hide)

    def init_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.add_header()
        self.add_content()

    def add_header(self) -> None:
        header_widget = SettingsDialogHeader(
            controller=self.controller,
            parent=self
        )
        self.layout().addWidget(header_widget)

    def add_content(self) -> None:
        # Content
        content_widget = QWidget(parent=self)
        content_widget_layout = QVBoxLayout()
        content_widget.setLayout(content_widget_layout)
        # Content data
        group_box = QGroupBox("General Options", parent=content_widget)
        content_widget_layout.addWidget(group_box)

        self.layout().addWidget(content_widget)

        group_box.setLayout(QGridLayout())
        self.add_only_speakers_checkbox(group_box, parent=content_widget)
        self.add_speaker_border_color_combobox(group_box)
        self.add_user_nickname_font_size(group_box)
        self.add_user_nickname_color(group_box)
        self.add_user_avater_size(group_box)

    def add_user_avater_size(self, group_box: QGroupBox) -> None:
        user_avater_size = QSpinBox(parent=group_box)
        user_avater_size.setToolTip("The size of the user avatar")
        user_avater_size.setRange(10, 120)
        avatar_size = self.controller.config.get("user_avatar_size", type=int, default=28)
        user_avater_size.setValue(avatar_size)

        user_avater_size.valueChanged.connect(self.user_avater_size_callback)
        label = QLabel(text="User avatar size:", parent=group_box)
        group_box.layout().addWidget(label, 6, 0)
        group_box.layout().addWidget(user_avater_size, 6, 1)

    def add_user_nickname_color(self, group_box: QGroupBox) -> None:
        user_nickname_color = QComboBox(parent=group_box)
        user_nickname_color.setToolTip("The border color of the user that speak")
        for color, icon in self._get_color_list_width_icon().items():
            user_nickname_color.addItem(icon, color)

        nickname_color = self.controller.config.get("user_nickname_color", type=str, default="white")
        user_nickname_color.setCurrentText(nickname_color)
        user_nickname_color.currentTextChanged.connect(self.user_nickname_color_callback)
        label = QLabel(text="User nickname color:", parent=group_box)
        group_box.layout().addWidget(label, 4, 0)
        group_box.layout().addWidget(user_nickname_color, 4, 1)

    def add_user_nickname_font_size(self, group_box: QGroupBox) -> None:
        user_nickname_font_size = QSpinBox(parent=group_box)
        user_nickname_font_size.setToolTip("The fontSize of the user nickname")
        user_nickname_font_size.setRange(10, 30)
        nickname_fontsize = self.controller.config.get("user_nickname_fontsize", type=int, default=12)
        user_nickname_font_size.setValue(nickname_fontsize)
        user_nickname_font_size.valueChanged.connect(
            self.user_nickname_font_size_callback
        )
        label = QLabel(text="User nickname fontSize:", parent=group_box)
        group_box.layout().addWidget(label, 3, 0)
        group_box.layout().addWidget(user_nickname_font_size, 3, 1)

    def _get_color_list_width_icon(self) -> dict:
        colors = {}

        for color in EXTENDED_COLORS:
            pixmap = QPixmap(15, 15)
            pixmap.fill(QColor(color))
            icon = QIcon(pixmap)
            colors[color] = icon
        return colors

    def add_speaker_border_color_combobox(self, group_box: QGroupBox) -> None:
        speaker_border_color_combobox = QComboBox(parent=group_box)
        speaker_border_color_combobox.setToolTip("The border color of the user that speak")
        for color, icon in self._get_color_list_width_icon().items():
            speaker_border_color_combobox.addItem(icon, color)

        border_color = self.controller.config.get("speaker_border_color", type=str, default="green")
        speaker_border_color_combobox.setCurrentText(border_color)
        speaker_border_color_combobox.currentTextChanged.connect(
            self.speaker_border_color_combobox_callback
        )
        label = QLabel(text="Speaker border color:", parent=group_box)
        group_box.layout().addWidget(label, 1, 0)
        group_box.layout().addWidget(speaker_border_color_combobox, 1, 1)

    def add_only_speakers_checkbox(self, group_box: QGroupBox, parent=None) -> None:
        only_speakers_checkbox = QCheckBox(
            text="Show only Speakers",
            parent=parent
        )
        only_speakers_checkbox.setToolTip("Will only show user when they speak")
        show_only_speakers = self.controller.config.get("show_only_speakers", type=bool, default=False)
        only_speakers_checkbox.setChecked(show_only_speakers)
        only_speakers_checkbox.stateChanged.connect(
            self.show_only_speakers_callback
        )
        group_box.layout().addWidget(only_speakers_checkbox, 0, 0)

    def user_nickname_font_size_callback(self, value: int) -> None:
        self.controller.config.set("user_nickname_fontsize", value)
        self.controller.settings_changed_signal.emit("user_nickname_fontsize")

    def user_avater_size_callback(self, value: int) -> None:
        self.controller.config.set("user_avatar_size", value)
        self.controller.settings_changed_signal.emit("user_avatar_size")

    def show_only_speakers_callback(self, checked: bool) -> None:
        if checked == 0:
            is_checked = False
        else:
            is_checked = True
        self.controller.config.set("show_only_speakers", is_checked)
        self.controller.settings_changed_signal.emit("show_only_speakers")

    def user_nickname_color_callback(self, text: str) -> None:
        self.controller.config.set("user_nickname_color", text)
        self.controller.settings_changed_signal.emit("user_nickname_color")

    def speaker_border_color_combobox_callback(self, text: str) -> None:
        self.controller.config.set("speaker_border_color", text)
        self.controller.settings_changed_signal.emit("speaker_border_color")

    def center(self) -> None:
        qrect = self.frameGeometry()
        cpoint = QGuiApplication.primaryScreen().availableGeometry().center()
        qrect.moveCenter(cpoint)
        qpoint = QPoint()
        qpoint.setX(int(qrect.topLeft().x() - qrect.height() / 2))
        qpoint.setY(int(qrect.topLeft().y() - qrect.width() / 2))
        self.move(qpoint)


class SettingsDialogHeader(QWidget):
    def __init__(self, controller: Controller, parent) -> None:
        super().__init__(parent=parent)
        self.controller = controller
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setObjectName(self.__class__.__name__)
        self.setStyleSheet("""
            #SettingsDialogHeader {
                background: #3c3c3c;
            }

            #SettingsDialogHeader QLabel{
                color: white;
            }


            #SettingsDialogHeaderCloseButton{
                border-image: url(images:close.png);
            }

            #SettingsDialogHeaderCloseButton:hover {
                border-image: url(images:close_hover.png);
            }
        """)
        self.setFixedHeight(22)
        self.init_ui()

    def init_ui(self) -> None:
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)

        icon = QLabel()
        icon.setPixmap(QIcon("images:icon.png").pixmap(16, 16))
        layout.addWidget(icon)

        title = QLabel(f"{self.controller.config.applicationName()} - Settings")
        layout.addWidget(title, 1, Qt.AlignmentFlag.AlignLeft)

        close = SettingsDialogHeaderCloseButton(
            controller=self.controller,
            parent=self
        )
        layout.addWidget(close, 1, Qt.AlignmentFlag.AlignRight)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.parent().old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        delta = QPoint(event.globalPosition().toPoint() - self.parent().old_pos)
        pos_x = self.parent().x() + delta.x()
        pos_y = self.parent().y() + delta.y()
        self.parent().move(pos_x, pos_y)
        self.parent().old_pos = event.globalPosition().toPoint()


class SettingsDialogHeaderCloseButton(QToolButton):
    def __init__(self, controller: Controller, parent) -> None:
        super().__init__(parent=parent)
        self.controller = controller
        self.setObjectName("SettingsDialogHeaderCloseButton")
        self.setContentsMargins(0, 0, 0, 0)
        self.clicked.connect(
            self.controller.settings_dialog_visibility_changed.emit
        )

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """ Override QToolButton.mouseMoveEvent so we can click on the button
        """
        pass
