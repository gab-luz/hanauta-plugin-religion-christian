#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

PLUGIN_ROOT = Path(__file__).resolve().parent
SERVICE_KEY = "christian_widget"
CHRISTIAN_APP = PLUGIN_ROOT / "christian_widget.py"


def _open_christian(window, api: dict[str, object]) -> None:
    entry_command = api.get("entry_command")
    run_bg = api.get("run_bg")
    command: list[str] = []
    if callable(entry_command):
        try:
            command = list(entry_command(CHRISTIAN_APP))
        except Exception:
            command = []
    if not command:
        command = ["python3", str(CHRISTIAN_APP)]
    if callable(run_bg):
        try:
            run_bg(command)
        except Exception:
            pass
    status = getattr(window, "christian_plugin_status", None)
    if isinstance(status, QLabel):
        status.setText("Christian widget launched.")


def build_christian_service_section(window, api: dict[str, object]) -> QWidget:
    SettingsRow = api["SettingsRow"]
    SwitchButton = api["SwitchButton"]
    ExpandableServiceSection = api["ExpandableServiceSection"]
    material_icon = api["material_icon"]
    icon_path = str(api.get("plugin_icon_path", "")).strip()

    service = window.settings_state.setdefault("services", {}).setdefault(
        SERVICE_KEY,
        {
            "enabled": True,
            "show_in_notification_center": True,
            "show_in_bar": True,
        },
    )

    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(10)

    display_switch = SwitchButton(bool(service.get("show_in_notification_center", True)))
    display_switch.toggledValue.connect(
        lambda enabled: window._set_service_notification_visibility(SERVICE_KEY, enabled)
    )
    window.service_display_switches[SERVICE_KEY] = display_switch
    layout.addWidget(
        SettingsRow(
            material_icon("widgets"),
            "Show in notification center",
            "Display Christian plugin controls in notification center.",
            window.icon_font,
            window.ui_font,
            display_switch,
        )
    )

    bar_switch = SwitchButton(bool(service.get("show_in_bar", True)))
    bar_switch.toggledValue.connect(
        lambda enabled: window._set_service_bar_visibility(SERVICE_KEY, enabled)
    )
    layout.addWidget(
        SettingsRow(
            material_icon("church"),
            "Show on bar",
            "Show Christian launcher on the top bar.",
            window.icon_font,
            window.ui_font,
            bar_switch,
        )
    )

    open_button = QPushButton("Open Christian widget")
    open_button.setObjectName("primaryButton")
    open_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    open_button.clicked.connect(lambda: _open_christian(window, api))
    layout.addWidget(
        SettingsRow(
            material_icon("open_in_new"),
            "Open Christian app",
            "Launch standalone Christian widget.",
            window.icon_font,
            window.ui_font,
            open_button,
        )
    )

    window.christian_plugin_status = QLabel("Christian plugin ready.")
    window.christian_plugin_status.setWordWrap(True)
    window.christian_plugin_status.setStyleSheet("color: rgba(246,235,247,0.72);")
    layout.addWidget(window.christian_plugin_status)

    section = ExpandableServiceSection(
        SERVICE_KEY,
        "Christian",
        "Standalone Christian widget plugin for Hanauta.",
        "?",
        window.icon_font,
        window.ui_font,
        content,
        window._service_enabled(SERVICE_KEY),
        lambda enabled: window._set_service_enabled(SERVICE_KEY, enabled),
        icon_path=icon_path,
    )
    window.service_sections[SERVICE_KEY] = section
    return section


def register_hanauta_plugin() -> dict[str, object]:
    return {
        "id": SERVICE_KEY,
        "name": "Christian",
        "service_sections": [
            {
                "key": SERVICE_KEY,
                "builder": build_christian_service_section,
                "supports_show_on_bar": True,
            }
        ],
    }
