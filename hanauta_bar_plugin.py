#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon

SERVICE_KEY = "christian_widget"
SETTINGS_FILE = (
    Path.home()
    / ".local"
    / "state"
    / "hanauta"
    / "notification-center"
    / "settings.json"
)


def _theme_choice() -> str:
    try:
        payload = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return "dark"
    appearance = payload.get("appearance", {}) if isinstance(payload, dict) else {}
    appearance = appearance if isinstance(appearance, dict) else {}
    if bool(appearance.get("use_matugen_palette", False)):
        return "wallpaper_aware"
    choice = str(appearance.get("theme_choice", "")).strip().lower()
    if choice == "wallpaper-aware":
        return "wallpaper_aware"
    if choice:
        return choice
    fallback = str(appearance.get("theme_mode", "dark")).strip().lower()
    return fallback if fallback else "dark"


def _pick_bar_icon(plugin_dir: Path) -> Path | None:
    theme = _theme_choice()
    use_color = theme in {"dark", "light", "custom"}
    candidates = (
        [
            plugin_dir / "assets" / "icon_color.svg",
            plugin_dir / "icon_color.svg",
            plugin_dir / "assets" / "icon.svg",
            plugin_dir / "icon.svg",
        ]
        if use_color
        else [
            plugin_dir / "assets" / "icon.svg",
            plugin_dir / "icon.svg",
            plugin_dir / "assets" / "icon_color.svg",
            plugin_dir / "icon_color.svg",
        ]
    )
    for path in candidates:
        if path.exists():
            return path
    return None


def _service_state(load_service_settings):
    services = load_service_settings()
    current = services.get(SERVICE_KEY, {}) if isinstance(services, dict) else {}
    return current if isinstance(current, dict) else {}


def register_hanauta_bar_plugin(bar, api: dict[str, object]) -> None:
    button = getattr(bar, "christian_button", None)
    if button is None:
        return

    plugin_dir = Path(str(api.get("plugin_dir", ""))).expanduser()
    load_service_settings = api["load_service_settings"]
    register_hook = api["register_hook"]

    def _apply_icon() -> None:
        path = _pick_bar_icon(plugin_dir)
        if path is None:
            return
        icon = QIcon(str(path))
        if icon.isNull():
            return
        button.setProperty("iconKey", "christian_widget")
        button.setProperty("nerdIcon", False)
        button.setIcon(icon)
        button.setIconSize(QSize(18, 18))
        button.setText("")

    def _sync_visibility() -> None:
        current = _service_state(load_service_settings)
        enabled = bool(current.get("enabled", True))
        show_in_bar = bool(current.get("show_in_bar", False))
        button.setVisible(enabled and show_in_bar)

    register_hook("icons", _apply_icon)
    register_hook("settings_reloaded", _sync_visibility)
    register_hook("settings_reloaded", _apply_icon)

    _sync_visibility()
    _apply_icon()
