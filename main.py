import sys
import os
import random
import json
import time
import logging
import asyncio
import threading
from queue import Queue
from uuid import uuid4
import psutil
import requests
import socks
import stem
import stem.control
from stem.control import Controller
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QToolBar,
    QLineEdit, QPushButton, QStatusBar, QAction, QMenu,
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QComboBox,
    QProgressBar, QDialog, QStackedWidget, QCheckBox,
    QFrame, QMenuBar, QDockWidget, QFormLayout, QSpinBox,
    QToolButton, QListWidget, QListWidgetItem, QFileDialog,
    QTabBar, QDialogButtonBox, QGroupBox, QRadioButton,
    QToolTip, QTreeWidget, QTreeWidgetItem, QInputDialog,
    QStyleFactory, QStyle, QActionGroup
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView, QWebEnginePage, QWebEngineProfile,
    QWebEngineDownloadItem, QWebEngineScript
)
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import (
    Qt, QUrl, pyqtSignal, QSize, QTimer, QSettings,
    QDateTime, QRect, QPropertyAnimation, QThread
)
from PyQt5.QtGui import (
    QIcon, QFont, QPalette, QColor, QPixmap, QPainter, QImage, QDesktopServices
)
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='secureveil.log'
)
logger = logging.getLogger('SecureVeil')

# Icon Path Setup
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ICONS_PATH = os.path.join(BASE_PATH, 'icons')

def load_icon(icon_name):
    """Load an icon from the icons folder, with fallback if missing."""
    icon_path = os.path.join(ICONS_PATH, f"{icon_name}.png")
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    logger.warning(f"Icon not found: {icon_path}")
    return QIcon()

# Constants
DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

SEARCH_ENGINES = {
    "DuckDuckGo": "https://duckduckgo.com/?q={}",
    "Startpage": "https://www.startpage.com/do/search?q={}",
    "Brave Search": "https://search.brave.com/search?q={}"
}

TOR_PATH = "tor"
TOR_PORT = 9050
TOR_CONTROL_PORT = 9051
TOR_PASSWORD = "secureveil"

BLOCKING_LISTS = [
    "https://easylist.to/easylist/easylist.txt",
    "https://easylist.to/easylist/easyprivacy.txt"
]

THEMES = {
    "Dark": """
        QMainWindow, QDialog, QDockWidget {
            background-color: #1e1e2e;
            color: #ffffff;
            font-family: 'Segoe UI', Arial;
            font-size: 14px;
        }
        QTabWidget::pane {
            border: 1px solid #313244;
            background-color: #313244;
        }
        QTabBar::tab {
            background-color: #313244;
            color: #ffffff;
            padding: 8px 16px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            font-size: 12px;
        }
        QTabBar::tab:selected {
            background-color: #45475a;
            color: #ffffff;
        }
        QTabBar::tab:hover {
            background-color: #585b70;
        }
        QTabBar::tab[private="true"] {
            border-left: 3px solid #f38ba8;
        }
        QLineEdit {
            background-color: #27272a;
            color: #ffffff;
            border-radius: 8px;
            padding: 6px 10px;
            border: none;
            font-size: 12px;
        }
        QPushButton, QToolButton {
            background-color: #44475a;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 6px 10px;
            min-width: 36px;
            min-height: 36px;
            font-size: 12px;
        }
        QPushButton:hover, QToolButton:hover {
            background-color: #585b70;
        }
        QProgressBar {
            border: none;
            border-radius: 4px;
            background-color: #44475a;
            text-align: center;
            font-size: 12px;
        }
        QProgressBar::chunk {
            background-color: #a6e3a1;
            border-radius: 4px;
        }
        QStatusBar {
            background-color: #27272a;
            color: #ffffff;
            font-size: 12px;
            min-height: 30px;
            padding: 4px;
        }
        QComboBox {
            background-color: #27272a;
            color: #ffffff;
            border-radius: 4px;
            padding: 6px;
            font-size: 12px;
        }
        QTreeWidget, QListWidget {
            background-color: #27272a;
            color: #ffffff;
            border: none;
            font-size: 12px;
        }
        QFrame#sidebarWidget, QFrame#securityWidget, QFrame#downloadWidget {
            background-color: #1e1e2e;
            border-radius: 8px;
            border: 1px solid #313244;
        }
        QLabel#statsLabel {
            font-size: 14px;
            font-weight: bold;
            color: #a6e3a1;
        }
        QMenuBar {
            background-color: #27272a;
            color: #ffffff;
            font-size: 12px;
        }
        QToolBar::separator {
            background-color: #44475a;
            width: 1px;
            margin: 4px;
        }
    """,
    "Light": """
        QMainWindow, QDialog, QDockWidget {
            background-color: #f5f5f5;
            color: #000000;
            font-family: 'Segoe UI', Arial;
            font-size: 14px;
        }
        QTabWidget::pane {
            border: 1px solid #d0d0d0;
            background-color: #e0e0e0;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            color: #000000;
            padding: 8px 16px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            font-size: 12px;
        }
        QTabBar::tab-selected {
            background-color: #ffffff;
            color: #000000;
        }
        QTabBar::tab:hover {
            background-color: #c0c0c0;
        }
        QTabBar::tab[private="true"] {
            border-left: 3px solid #e91e63;
        }
        QLineEdit {
            background-color: #ffffff;
            color: #000000;
            border-radius: 8px;
            padding: 6px 10px;
            border: 1px solid #d0d0d0;
            font-size: 12px;
        }
        QPushButton, QToolButton {
            background-color: #d0d0d0;
            color: #000000;
            border: none;
            border-radius: 8px;
            padding: 6px 10px;
            min-width: 36px;
            min-height: 36px;
            font-size: 12px;
        }
        QPushButton:hover, QToolButton:hover {
            background-color: #c0c0c0;
        }
        QProgressBar {
            border: none;
            border-radius: 4px;
            background-color: #d0d0d0;
            text-align: center;
            font-size: 12px;
        }
        QProgressBar::chunk {
            background-color: #4caf50;
            border-radius: 4px;
        }
        QStatusBar {
            background-color: #e0e0e0;
            color: #000000;
            font-size: 12px;
            min-height: 30px;
            padding: 4px;
        }
        QComboBox {
            background-color: #ffffff;
            color: #000000;
            border-radius: 4px;
            padding: 6px;
            font-size: 12px;
            border: 1px solid #d0d0d0;
        }
        QTreeWidget, QListWidget {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
            font-size: 12px;
        }
        QFrame#sidebarWidget, QFrame#securityWidget, QFrame#downloadWidget {
            background-color: #f5f5f5;
            border-radius: 8px;
            border: 1px solid #d0d0d0;
        }
        QLabel#statsLabel {
            font-size: 14px;
            font-weight: bold;
            color: #4caf50;
        }
        QMenuBar {
            background-color: #e0e0e0;
            color: #000000;
            font-size: 12px;
        }
        QToolBar::separator {
            background-color: #d0d0d0;
            width: 1px;
            margin: 4px;
        }
    """
}

PRIVACY_MODES = {
    "Strict": {
        "javascript": False,
        "cookies": "Block All",
        "media": False,
        "webgl": False
    },
    "Balanced": {
        "javascript": True,
        "cookies": "Session Only",
        "media": False,
        "webgl": False
    },
    "Minimal": {
        "javascript": True,
        "cookies": "Allow All",
        "media": True,
        "webgl": True
    }
}

class TrackerBlocker(QWebEngineUrlRequestInterceptor):
    """Optimized tracker blocker"""
    block_rules = set()
    tracker_count = 0
    tracker_count_signal = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rule_queue = Queue()
        threading.Thread(target=self.load_block_rules_async, daemon=True).start()

    def load_block_rules_async(self):
        try:
            for block_list_url in BLOCKING_LISTS:
                try:
                    response = requests.get(block_list_url, timeout=5)
                    if response.status_code == 200:
                        for line in response.text.splitlines():
                            if line and not line.startswith(('#', '!')) and '.' in line:
                                if "0.0.0.0 " in line:
                                    domain = line.split("0.0.0.0 ")[1].strip()
                                    self.rule_queue.put(domain)
                                elif "||" in line:
                                    domain = line.split("||")[1].split("^")[0]
                                    self.rule_queue.put(domain)
                except Exception as e:
                    logger.error(f"Error loading block list {block_list_url}: {e}")
            while not self.rule_queue.empty():
                self.block_rules.add(self.rule_queue.get())
            logger.info(f"Loaded {len(self.block_rules)} blocking rules")
        except Exception as e:
            logger.error(f"Error in async rule loading: {e}")

    def interceptRequest(self, info):
        url = info.requestUrl().host()
        if any(rule in url for rule in self.block_rules):
            self.tracker_count += 1
            self.tracker_count_signal.emit(self.tracker_count)
            info.block(True)
            logger.debug(f"Blocked tracker: {url}")

class TorManager:
    """Manages Tor connection"""
    def __init__(self):
        self.tor_process = None
        self.controller = None
        self.tor_initialized = False
        self.error_count = 0
        self.max_retries = 3
        self.loop = None
        self.thread = None

    def start_tor(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        future = asyncio.run_coroutine_threadsafe(self.start_tor_async(), self.loop)
        return future.result(timeout=30)

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def start_tor_async(self):
        try:
            tor_config = {
                'SocksPort': str(TOR_PORT),
                'ControlPort': str(TOR_CONTROL_PORT),
                'HashedControlPassword': Controller.hash_password(TOR_PASSWORD)
            }
            if QSettings("SecureVeil", "Browser").value("tor_bridges", False, bool):
                tor_config['UseBridges'] = '1'
            self.tor_process = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: stem.process.launch_tor_with_config(
                    config=tor_config,
                    init_msg_handler=self._log_tor_bootstrap,
                    take_ownership=True
                )
            )
            self.controller = Controller.from_port(port=TOR_CONTROL_PORT)
            self.controller.authenticate(password=TOR_PASSWORD)
            self.tor_initialized = True
            logger.info("Tor started successfully")
            return True
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error starting Tor (attempt {self.error_count}): {e}")
            if self.error_count < self.max_retries:
                await asyncio.sleep(2)
                return await self.start_tor_async()
            return False

    def _log_tor_bootstrap(self, line):
        if "Bootstrapped " in line:
            logger.info(line)

    def new_identity(self):
        try:
            if self.controller and self.controller.is_alive():
                self.controller.signal(stem.Signal.NEWNYM)
                logger.info("New Tor identity requested")
                return True
            return False
        except Exception as e:
            logger.error(f"Error requesting new identity: {e}")
            return False

    def stop_tor(self):
        try:
            if self.controller:
                self.controller.close()
            if self.tor_process:
                self.tor_process.terminate()
                self.tor_process.wait()
            if self.loop and self.loop.is_running():
                self.loop.call_soon_threadsafe(self._shutdown_loop)
            self.tor_initialized = False
            logger.info("Tor stopped")
        except Exception as e:
            logger.error(f"Error stopping Tor: {e}")

    def _shutdown_loop(self):
        tasks = [task for task in asyncio.all_tasks(self.loop) if task is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        self.loop.stop()
        self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        self.loop.run_until_complete(self.loop.shutdown_default_executor())
        self.loop.close()

class SecureWebPage(QWebEnginePage):
    """Custom webpage with privacy controls"""
    def __init__(self, profile, parent=None, is_private=False):
        super().__init__(profile, parent)
        self.is_private = is_private
        self.setFeaturePermission = self._set_feature_permission

    def _set_feature_permission(self, url, feature, permission):
        if self.is_private and feature in [
            QWebEnginePage.Geolocation,
            QWebEnginePage.MediaAudioCapture,
            QWebEnginePage.MediaVideoCapture
        ]:
            self.setFeaturePermission(url, feature, QWebEnginePage.PermissionDeniedByUser)
        else:
            super().setFeaturePermission(url, feature, permission)

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        if url.scheme() == "file":
            logger.warning(f"Blocked access to file URL: {url.toString()}")
            return False
        if url.scheme() == "data" and url.toString().startswith("data:text/html") and url.fragment() == "about:home":
            return True
        if url.scheme() == "data":
            logger.warning(f"Blocked access to data URL: {url.toString()}")
            return False
        if QSettings("SecureVeil", "Browser").value("https_enforce", True, bool) and url.scheme() == "http":
            url.setScheme("https")
            self.setUrl(url)
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)

class SecureWebView(QWebEngineView):
    """Enhanced web view with privacy features"""
    urlChanged = pyqtSignal(QUrl)
    faviconChanged = pyqtSignal(QIcon)

    def __init__(self, profile, parent=None, is_private=False):
        super().__init__(parent)
        self.custom_page = SecureWebPage(profile, self, is_private)
        self.setPage(self.custom_page)
        self.loadStarted.connect(self.on_load_started)
        self.loadFinished.connect(self.on_load_finished)
        self.urlChanged.connect(self.on_url_changed)
        self.iconChanged.connect(self.on_favicon_changed)
        self.apply_privacy_settings(is_private)
        self.tab_index = -1
        self.tracker_count = 0
        self.privacy_settings = PRIVACY_MODES["Balanced"].copy()

    def apply_privacy_settings(self, is_private):
        settings = self.page().settings()
        privacy_mode = QSettings("SecureVeil", "Browser").value("privacy_mode", "Balanced", str)
        config = PRIVACY_MODES[privacy_mode].copy()
        if is_private:
            config = PRIVACY_MODES["Strict"].copy()
        self.privacy_settings = config
        settings.setAttribute(settings.JavascriptEnabled, config["javascript"])
        settings.setAttribute(settings.LocalStorageEnabled, config["cookies"] != "Block All")
        settings.setAttribute(settings.WebGLEnabled, config["webgl"])
        settings.setAttribute(settings.PluginsEnabled, False)

    def update_privacy_settings(self, config):
        settings = self.page().settings()
        self.privacy_settings.update(config)
        settings.setAttribute(settings.JavascriptEnabled, self.privacy_settings["javascript"])
        settings.setAttribute(settings.LocalStorageEnabled, self.privacy_settings["cookies"] != "Block All")
        settings.setAttribute(settings.WebGLEnabled, self.privacy_settings["webgl"])

    def handle_download(self, download):
        download_path = QSettings("SecureVeil", "Browser").value("download_path", os.path.expanduser("~/Downloads"), str)
        suggested_path = os.path.join(download_path, download.suggestedFileName())
        path, _ = QFileDialog.getSaveFileName(self, "Save File", suggested_path)
        if path:
            download.setPath(path)
            download.accept()
            download.stateChanged.connect(lambda state: self.parent().update_download_status(download, state))

    def on_load_started(self):
        logger.debug(f"Started loading: {self.url().toString()}")

    def on_load_finished(self, ok):
        if ok:
            logger.debug(f"Finished loading: {self.url().toString()}")

    def on_url_changed(self, url):
        self.urlChanged.emit(url)

    def on_favicon_changed(self, icon):
        self.faviconChanged.emit(icon)

    def createWindow(self, window_type):
        if window_type == QWebEnginePage.WebBrowserTab:
            return self.parent().create_new_tab(is_private=self.custom_page.is_private)
        return None

    def get_preview(self):
        """Generate a lightweight tab preview"""
        pixmap = QPixmap(200, 150)
        pixmap.fill(Qt.transparent)
        self.render(pixmap)
        return pixmap.scaled(100, 75, Qt.KeepAspectRatio, Qt.SmoothTransformation)

class DownloadManager(QDockWidget):
    """Dockable download manager with enhanced features"""
    status_message = pyqtSignal(str, int)

    def __init__(self, parent=None):
        super().__init__("Downloads", parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.downloads = {}
        self.init36()
        self.speed_timer = QTimer()
        self.speed_timer.timeout.connect(self.update_download_speeds)
        self.speed_timer.start(1000)

    def init36(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        header_label = QLabel("Download Manager")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(header_label)

        filter_layout = QHBoxLayout()
        sort_label = QLabel("Sort by:")
        sort_label.setFont(QFont("Segoe UI", 12))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Size", "Status"])
        self.sort_combo.setFont(QFont("Segoe UI", 12))
        self.sort_combo.currentTextChanged.connect(self.sort_downloads)
        filter_label = QLabel("Filter:")
        filter_label.setFont(QFont("Segoe UI", 12))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "In Progress", "Completed", "Cancelled", "Interrupted"])
        self.filter_combo.setFont(QFont("Segoe UI", 12))
        self.filter_combo.currentTextChanged.connect(self.filter_downloads)
        filter_layout.addWidget(sort_label)
        filter_layout.addWidget(self.sort_combo)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        layout.addLayout(filter_layout)

        self.download_list = QListWidget()
        self.download_list.setFont(QFont("Segoe UI", 12))
        self.download_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.download_list.customContextMenuRequested.connect(self.show_context_menu)
        self.download_list.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(self.download_list)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        clear_btn = QPushButton(load_icon("clear"), "Clear Completed")
        clear_btn.setStyleSheet("font-size: 12px;")
        clear_btn.clicked.connect(self.clear_completed)
        controls_layout.addWidget(clear_btn)

        self.pause_resume_btn = QPushButton(load_icon("pause"), "Pause All")
        self.pause_resume_btn.setStyleSheet("font-size: 12px;")
        self.pause_resume_btn.clicked.connect(self.toggle_pause_resume)
        controls_layout.addWidget(self.pause_resume_btn)

        cancel_btn = QPushButton(load_icon("cancel"), "Cancel Selected")
        cancel_btn.setStyleSheet("font-size: 12px;")
        cancel_btn.clicked.connect(self.cancel_selected)
        controls_layout.addWidget(cancel_btn)

        open_folder_btn = QPushButton(load_icon("folder"), "Open Download Folder")
        open_folder_btn.setStyleSheet("font-size: 12px;")
        open_folder_btn.clicked.connect(self.open_download_folder)
        controls_layout.addWidget(open_folder_btn)

        layout.addLayout(controls_layout)

        widget.setLayout(layout)
        self.setWidget(widget)
        self.setMinimumHeight(250)

    def add_download(self, download):
        if not isinstance(download, QWebEngineDownloadItem):
            logger.error(f"Invalid download object: {type(download)}")
            return

        item = QListWidgetItem()
        item.setIcon(load_icon("download"))
        item.setData(Qt.UserRole, download)

        download_widget = QWidget()
        download_layout = QVBoxLayout()
        download_layout.setContentsMargins(5, 5, 5, 5)

        name_label = QLabel(download.suggestedFileName())
        name_label.setFont(QFont("Segoe UI", 12))
        status_label = QLabel("Starting...")
        status_label.setFont(QFont("Segoe UI", 10))

        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(8)

        download_layout.addWidget(name_label)
        download_layout.addWidget(status_label)
        download_layout.addWidget(progress_bar)
        download_widget.setLayout(download_layout)

        item.setSizeHint(download_widget.sizeHint())
        self.download_list.addItem(item)
        self.download_list.setItemWidget(item, download_widget)

        download_id = id(download)
        self.downloads[download_id] = {
            "item": item,
            "download": download,
            "last_bytes": 0,
            "last_time": time.time(),
            "speed": 0,
            "name_label": name_label,
            "status_label": status_label,
            "progress_bar": progress_bar
        }

        download.stateChanged.connect(lambda state: self.update_download(item, download, state))
        download.receivedBytesChanged.connect(lambda: self.update_download_progress(item, download))

        self.status_message.emit(f"Started download: {download.suggestedFileName()}", 3000)

    def update_download(self, item, download, state):
        download_id = id(download)
        if download_id not in self.downloads:
            return

        download_info = self.downloads[download_id]
        name_label = download_info["name_label"]
        status_label = download_info["status_label"]
        progress_bar = download_info["progress_bar"]

        progress = download.receivedBytes() / download.totalBytes() * 100 if download.totalBytes() > 0 else 0

        if state == QWebEngineDownloadItem.DownloadCompleted:
            item.setIcon(load_icon("complete"))
            status_label.setText(f"Completed - {self.format_size(download.totalBytes())}")
            progress_bar.setValue(100)
            self.status_message.emit(f"Download completed: {download.suggestedFileName()}", 3000)
        elif state == QWebEngineDownloadItem.DownloadInProgress:
            item.setIcon(load_icon("download"))
            speed = self.downloads[download_id]["speed"]
            status_label.setText(f"{progress:.1f}% - {self.format_size(download.receivedBytes())} / {self.format_size(download.totalBytes())} ({self.format_speed(speed)})")
            progress_bar.setValue(int(progress))
        elif state == QWebEngineDownloadItem.DownloadCancelled:
            item.setIcon(load_icon("cancel"))
            status_label.setText("Cancelled")
            progress_bar.setValue(0)
            self.status_message.emit(f"Download cancelled: {download.suggestedFileName()}", 3000)
        elif state == QWebEngineDownloadItem.DownloadInterrupted:
            item.setIcon(load_icon("error"))
            status_label.setText("Interrupted")
            progress_bar.setValue(0)
            self.status_message.emit(f"Download interrupted: {download.suggestedFileName()}", 3000)

        self.sort_downloads()
        self.filter_downloads()

    def update_download_progress(self, item, download):
        download_id = id(download)
        if download_id not in self.downloads:
            return

        download_info = self.downloads[download_id]
        progress = download.receivedBytes() / download.totalBytes() * 100 if download.totalBytes() > 0 else 0
        download_info["progress_bar"].setValue(int(progress))
        speed = download_info["speed"]
        download_info["status_label"].setText(
            f"{progress:.1f}% - {self.format_size(download.receivedBytes())} / {self.format_size(download.totalBytes())} ({self.format_speed(speed)})"
        )

    def update_download_speeds(self):
        current_time = time.time()
        for download_id, info in list(self.downloads.items()):
            download = info["download"]
            if download.state() == QWebEngineDownloadItem.DownloadInProgress:
                received_bytes = download.receivedBytes()
                last_bytes = info["last_bytes"]
                last_time = info["last_time"]
                time_diff = current_time - last_time
                if time_diff > 0:
                    speed = (received_bytes - last_bytes) / time_diff
                    info["speed"] = speed
                info["last_bytes"] = received_bytes
                info["last_time"] = current_time
                self.update_download_progress(info["item"], download)

    def show_context_menu(self, position):
        item = self.download_list.itemAt(position)
        if not item:
            return

        download = item.data(Qt.UserRole)
        if not isinstance(download, QWebEngineDownloadItem):
            return

        menu = QMenu()
        download_id = id(download)
        if download_id in self.downloads:
            download_info = self.downloads[download_id]

            open_action = QAction(load_icon("open"), "Open File", self)
            open_action.triggered.connect(lambda: self.open_file(download))
            open_action.setEnabled(download.state() == QWebEngineDownloadItem.DownloadCompleted)
            menu.addAction(open_action)

            folder_action = QAction(load_icon("folder"), "Show in Folder", self)
            folder_action.triggered.connect(lambda: self.show_in_folder(download))
            folder_action.setEnabled(download.state() == QWebEngineDownloadItem.DownloadCompleted)
            menu.addAction(folder_action)

            cancel_action = QAction(load_icon("cancel"), "Cancel Download", self)
            cancel_action.triggered.connect(lambda: self.cancel_download(download))
            cancel_action.setEnabled(download.state() == QWebEngineDownloadItem.DownloadInProgress)
            menu.addAction(cancel_action)

            pause_resume_action = QAction(
                load_icon("resume" if download.isPaused() else "pause"),
                "Resume" if download.isPaused() else "Pause",
                self
            )
            pause_resume_action.triggered.connect(lambda: self.toggle_download_pause(download))
            pause_resume_action.setEnabled(download.state() == QWebEngineDownloadItem.DownloadInProgress)
            menu.addAction(pause_resume_action)

            menu.exec_(self.download_list.mapToGlobal(position))

    def open_file(self, download):
        if download.state() == QWebEngineDownloadItem.DownloadCompleted:
            QDesktopServices.openUrl(QUrl.fromLocalFile(download.path()))
            self.status_message.emit(f"Opening {download.path()}", 3000)

    def show_in_folder(self, download):
        if download.state() == QWebEngineDownloadItem.DownloadCompleted:
            folder = os.path.dirname(download.path())
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
            self.status_message.emit(f"Showing {download.path()} in folder", 3000)

    def cancel_download(self, download):
        if download.state() == QWebEngineDownloadItem.DownloadInProgress:
            download.cancel()
            self.status_message.emit(f"Cancelled {download.suggestedFileName()}", 3000)

    def toggle_download_pause(self, download):
        if download.state() == QWebEngineDownloadItem.DownloadInProgress:
            if download.isPaused():
                download.resume()
                self.status_message.emit(f"Resumed {download.suggestedFileName()}", 3000)
            else:
                download.pause()
                self.status_message.emit(f"Paused {download.suggestedFileName()}", 3000)
            self.update_download(self.downloads[id(download)]["item"], download, download.state())

    def toggle_pause_resume(self):
        is_paused = self.pause_resume_btn.text() == "Pause All"
        for download_id, info in self.downloads.items():
            download = info["download"]
            if download.state() == QWebEngineDownloadItem.DownloadInProgress:
                if is_paused:
                    download.pause()
                else:
                    download.resume()
                self.update_download(info["item"], download, download.state())
        self.pause_resume_btn.setText("Resume All" if is_paused else "Pause All")
        self.pause_resume_btn.setIcon(load_icon("resume" if is_paused else "pause"))
        self.status_message.emit(f"{'Paused' if is_paused else 'Resumed'} all downloads", 3000)

    def cancel_selected(self):
        selected_items = self.download_list.selectedItems()
        for item in selected_items:
            download = item.data(Qt.UserRole)
            if download.state() == QWebEngineDownloadItem.DownloadInProgress:
                download.cancel()
                self.status_message.emit(f"Cancelled {download.suggestedFileName()}", 3000)

    def open_download_folder(self):
        download_path = QSettings("SecureVeil", "Browser").value("download_path", os.path.expanduser("~/Downloads"), str)
        if os.path.exists(download_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(download_path))
            self.status_message.emit(f"Opened download folder: {download_path}", 3000)
        else:
            self.status_message.emit(f"Download folder not found: {download_path}", 3000)

    def clear_completed(self):
        for i in range(self.download_list.count() - 1, -1, -1):
            item = self.download_list.item(i)
            download = item.data(Qt.UserRole)
            if download.state() == QWebEngineDownloadItem.DownloadCompleted:
                download_id = id(download)
                self.download_list.takeItem(i)
                if download_id in self.downloads:
                    del self.downloads[download_id]
        self.status_message.emit("Cleared completed downloads", 3000)

    def sort_downloads(self):
        sort_by = self.sort_combo.currentText()
        items = []
        for i in range(self.download_list.count()):
            item = self.download_list.item(i)
            download = item.data(Qt.UserRole)
            items.append((item, download))

        if sort_by == "Name":
            items.sort(key=lambda x: x[1].suggestedFileName().lower())
        elif sort_by == "Size":
            items.sort(key=lambda x: x[1].totalBytes(), reverse=True)
        elif sort_by == "Status":
            items.sort(key=lambda x: x[1].state())

        self.download_list.clear()
        for item, _ in items:
            self.download_list.addItem(item)
            self.download_list.setItemWidget(item, item.widget())

    def filter_downloads(self):
        filter_by = self.filter_combo.currentText()
        for i in range(self.download_list.count()):
            item = self.download_list.item(i)
            download = item.data(Qt.UserRole)
            state = download.state()
            should_show = True

            if filter_by == "In Progress" and state != QWebEngineDownloadItem.DownloadInProgress:
                should_show = False
            elif filter_by == "Completed" and state != QWebEngineDownloadItem.DownloadCompleted:
                should_show = False
            elif filter_by == "Cancelled" and state != QWebEngineDownloadItem.DownloadCancelled:
                should_show = False
            elif filter_by == "Interrupted" and state != QWebEngineDownloadItem.DownloadInterrupted:
                should_show = False
            item.setHidden(not should_show)

    def format_size(self, bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
        return f"{bytes:.1f} TB"

    def format_speed(self, bytes_per_sec):
        return self.format_size(bytes_per_sec) + "/s"

class BookmarkManager(QDialog):
    """Bookmark organizer dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bookmark Manager")
        self.setWindowIcon(load_icon("bookmarks"))
        self.init36()

    def init36(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        self.bookmark_tree = QTreeWidget()
        self.bookmark_tree.setHeaderLabels(["Title", "URL"])
        self.bookmark_tree.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self.bookmark_tree)

        controls_layout = QHBoxLayout()
        add_btn = QPushButton(load_icon("bookmark-add"), "Add Bookmark")
        add_btn.clicked.connect(self.add_bookmark)
        controls_layout.addWidget(add_btn)
        add_folder_btn = QPushButton(load_icon("folder"), "Add Folder")
        add_folder_btn.clicked.connect(self.add_folder)
        controls_layout.addWidget(add_folder_btn)
        delete_btn = QPushButton(load_icon("delete"), "Delete")
        delete_btn.clicked.connect(self.delete_item)
        controls_layout.addWidget(delete_btn)
        export_btn = QPushButton(load_icon("export"), "Export (HTML)")
        export_btn.clicked.connect(self.export_bookmarks_html)
        controls_layout.addWidget(export_btn)
        import_btn = QPushButton(load_icon("import"), "Import (HTML)")
        import_btn.clicked.connect(self.import_bookmarks_html)
        controls_layout.addWidget(import_btn)
        layout.addLayout(controls_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self.load_bookmarks()

    def load_bookmarks(self):
        self.bookmark_tree.clear()
        bookmarks = QSettings("SecureVeil", "Browser").value("bookmarks", [], list)
        root = self.bookmark_tree.invisibleRootItem()
        for bookmark in bookmarks:
            item = QTreeWidgetItem([bookmark["title"], bookmark["url"]])
            item.setIcon(0, load_icon("bookmark"))
            item.setData(0, Qt.UserRole, bookmark)
            root.addChild(item)

    def add_bookmark(self):
        title, ok1 = QInputDialog.getText(self, "Add Bookmark", "Title:")
        url, ok2 = QInputDialog.getText(self, "Add Bookmark", "URL:")
        if ok1 and ok2 and title and url:
            bookmarks = QSettings("SecureVeil", "Browser").value("bookmarks", [], list)
            bookmarks.append({"title": title, "url": url})
            QSettings("SecureVeil", "Browser").setValue("bookmarks", bookmarks)
            self.load_bookmarks()

    def add_folder(self):
        name, ok = QInputDialog.getText(self, "Add Folder", "Folder Name:")
        if ok and name:
            item = QTreeWidgetItem([name, ""])
            item.setIcon(0, load_icon("folder"))
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.bookmark_tree.invisibleRootItem().addChild(item)

    def delete_item(self):
        selected = self.bookmark_tree.currentItem()
        if selected:
            bookmarks = QSettings("SecureVeil", "Browser").value("bookmarks", [], list)
            bookmark = selected.data(0, Qt.UserRole)
            if bookmark:
                bookmarks.remove(bookmark)
                QSettings("SecureVeil", "Browser").setValue("bookmarks", bookmarks)
            self.load_bookmarks()

    def export_bookmarks_html(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Bookmarks", "bookmarks.html", "HTML (*.html)")
        if path:
            bookmarks = QSettings("SecureVeil", "Browser").value("bookmarks", [], list)
            html = "<!DOCTYPE NETSCAPE-Bookmark-file-1>\n"
            html += "<META HTTP-EQUIV='Content-Type' CONTENT='text/html; charset=UTF-8'>\n"
            html += "<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks</H1>\n<DL><p>\n"
            for bookmark in bookmarks:
                html += f"<DT><A HREF='{bookmark['url']}'>{bookmark['title']}</A>\n"
            html += "</DL><p>\n"
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            self.parent().status_bar.showMessage("Bookmarks exported as HTML", 3000)

    def import_bookmarks_html(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Bookmarks", "", "HTML (*.html)")
        if path:
            from bs4 import BeautifulSoup
            with open(path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
            bookmarks = []
            for a in soup.find_all('a'):
                title = a.text
                url = a.get('href')
                if title and url:
                    bookmarks.append({"title": title, "url": url})
            existing = QSettings("SecureVeil", "Browser").value("bookmarks", [], list)
            existing.extend(bookmarks)
            QSettings("SecureVeil", "Browser").setValue("bookmarks", existing)
            self.load_bookmarks()
            self.parent().status_bar.showMessage("Bookmarks imported from HTML", 3000)

class SecurityDashboard(QFrame):
    """Enhanced security dashboard with resource monitor"""
    new_identity_requested = pyqtSignal()
    privacy_mode_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("securityWidget")
        self.tracker_count = 0
        self.process = psutil.Process()
        self.init36()

    def init36(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel("Privacy Dashboard")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title_label)

        mode_group = QGroupBox("Privacy Mode")
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(10)
        self.strict_mode = QRadioButton("Strict")
        self.strict_mode.setIcon(load_icon("strict"))
        self.balanced_mode = QRadioButton("Balanced")
        self.balanced_mode.setIcon(load_icon("balanced"))
        self.minimal_mode = QRadioButton("Minimal")
        self.minimal_mode.setIcon(load_icon("minimal"))
        self.balanced_mode.setChecked(True)
        mode_layout.addWidget(self.strict_mode)
        mode_layout.addWidget(self.balanced_mode)
        mode_layout.addWidget(self.minimal_mode)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        self.strict_mode.toggled.connect(lambda: self.privacy_mode_changed.emit("Strict"))
        self.balanced_mode.toggled.connect(lambda: self.privacy_mode_changed.emit("Balanced"))
        self.minimal_mode.toggled.connect(lambda: self.privacy_mode_changed.emit("Minimal"))

        route_frame = QFrame()
        route_frame.setStyleSheet("background-color: #313244; border-radius: 8px; padding: 10px;")
        route_layout = QVBoxLayout(route_frame)
        route_label = QLabel("Tor Connection")
        route_label.setAlignment(Qt.AlignCenter)
        route_label.setFont(QFont("Segoe UI", 14))
        route_layout.addWidget(route_label)
        self.route_status = QLabel("Initializing...")
        self.route_status.setAlignment(Qt.AlignCenter)
        self.route_status.setFont(QFont("Segoe UI", 12))
        route_layout.addWidget(self.route_status)
        layout.addWidget(route_frame)

        stats_frame = QFrame()
        stats_frame.setStyleSheet("background-color: #313244; border-radius: 8px; padding: 10px;")
        stats_layout = QVBoxLayout(stats_frame)
        stats_title = QLabel("Trackers Blocked")
        stats_title.setAlignment(Qt.AlignCenter)
        stats_title.setFont(QFont("Segoe UI", 14))
        stats_layout.addWidget(stats_title)
        self.stats_value = QLabel("0")
        self.stats_value.setObjectName("statsLabel")
        self.stats_value.setAlignment(Qt.AlignCenter)
        self.stats_value.setFont(QFont("Segoe UI", 12))
        stats_layout.addWidget(self.stats_value)
        layout.addWidget(stats_frame)

        resource_frame = QFrame()
        resource_frame.setStyleSheet("background-color: #313244; border-radius: 8px; padding: 10px;")
        resource_layout = QVBoxLayout(resource_frame)
        resource_label = QLabel("Resource Usage")
        resource_label.setAlignment(Qt.AlignCenter)
        resource_label.setFont(QFont("Segoe UI", 14))
        resource_layout.addWidget(resource_label)
        self.memory_label = QLabel("Memory: 0 MB")
        self.memory_label.setAlignment(Qt.AlignCenter)
        self.memory_label.setFont(QFont("Segoe UI", 12))
        resource_layout.addWidget(self.memory_label)
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_label.setAlignment(Qt.AlignCenter)
        self.cpu_label.setFont(QFont("Segoe UI", 12))
        resource_layout.addWidget(self.cpu_label)
        layout.addWidget(resource_frame)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        self.new_identity_btn = QPushButton(load_icon("identity"), "New Identity")
        self.new_identity_btn.setStyleSheet("background-color: #f38ba8; font-size: 12px;")
        self.new_identity_btn.clicked.connect(self.request_new_identity)
        controls_layout.addWidget(self.new_identity_btn)

        self.reset_btn = QPushButton(load_icon("reset"), "Reset")
        self.reset_btn.setStyleSheet("font-size: 12px;")
        self.reset_btn.clicked.connect(self.reset_stats)
        controls_layout.addWidget(self.reset_btn)
        layout.addLayout(controls_layout)

        layout.addStretch()
        self.setLayout(layout)
        self.setMinimumWidth(300)

        self.resource_timer = QTimer()
        self.resource_timer.timeout.connect(self.update_resources)
        self.resource_timer.start(5000)

    def update_tracker_count(self, count):
        self.tracker_count = count
        self.stats_value.setText(str(count))

    def update_route_status(self, status):
        self.route_status.setText(status)

    def request_new_identity(self):
        self.new_identity_requested.emit()

    def reset_stats(self):
        self.tracker_count = 0
        self.stats_value.setText("0")

    def update_resources(self):
        try:
            memory = self.process.memory_info().rss / 1024 / 1024
            cpu = self.process.cpu_percent(interval=0.1)
            self.memory_label.setText(f"Memory: {memory:.1f} MB")
            self.cpu_label.setText(f"CPU: {cpu:.1f}%")
        except Exception as e:
            logger.error(f"Error updating resources: {e}")

class Sidebar(QDockWidget):
    """Collapsible sidebar with search"""
    def __init__(self, parent=None):
        super().__init__("Sidebar", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.init36()

    def init36(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search bookmarks/history...")
        self.search_bar.setFont(QFont("Segoe UI", 12))
        self.search_bar.textChanged.connect(self.filter_items)
        layout.addWidget(self.search_bar)

        self.tab_widget = QTabWidget()
        self.bookmarks_list = QListWidget()
        self.history_list = QListWidget()
        self.tab_widget.addTab(self.bookmarks_list, load_icon("bookmarks"), "Bookmarks")
        self.tab_widget.addTab(self.history_list, load_icon("history"), "History")
        layout.addWidget(self.tab_widget)

        bookmark_controls = QHBoxLayout()
        bookmark_controls.setSpacing(10)
        add_bookmark_btn = QToolButton()
        add_bookmark_btn.setIcon(load_icon("bookmark-add"))
        add_bookmark_btn.setToolTip("Add Bookmark")
        add_bookmark_btn.clicked.connect(self.parent().add_bookmark)
        bookmark_controls.addWidget(add_bookmark_btn)
        export_bookmark_btn = QToolButton()
        export_bookmark_btn.setIcon(load_icon("export"))
        export_bookmark_btn.setToolTip("Export Bookmarks")
        export_bookmark_btn.clicked.connect(self.export_bookmarks_html)
        bookmark_controls.addWidget(export_bookmark_btn)
        manage_bookmarks_btn = QToolButton()
        manage_bookmarks_btn.setIcon(load_icon("bookmarks"))
        manage_bookmarks_btn.setToolTip("Manage Bookmarks")
        manage_bookmarks_btn.clicked.connect(self.parent().open_bookmark_manager)
        bookmark_controls.addWidget(manage_bookmarks_btn)
        layout.addLayout(bookmark_controls)

        history_controls = QHBoxLayout()
        history_controls.setSpacing(10)
        clear_history_btn = QToolButton()
        clear_history_btn.setIcon(load_icon("clear"))
        clear_history_btn.setToolTip("Clear History")
        clear_history_btn.clicked.connect(self.clear_history)
        history_controls.addWidget(clear_history_btn)
        layout.addLayout(history_controls)

        layout.addStretch()
        widget.setLayout(layout)
        self.setWidget(widget)
        self.setMinimumWidth(250)
        self.load_bookmarks()
        self.load_history()

    def load_bookmarks(self):
        self.bookmarks_list.clear()
        bookmarks = QSettings("SecureVeil", "Browser").value("bookmarks", [], list)
        for bookmark in bookmarks:
            item = QListWidgetItem(load_icon("bookmark"), f"{bookmark['title']} ({bookmark['url']})")
            item.setData(Qt.UserRole, bookmark['url'])
            self.bookmarks_list.addItem(item)
        self.bookmarks_list.itemClicked.connect(self.open_bookmark)

    def load_history(self):
        self.history_list.clear()
        history = QSettings("SecureVeil", "Browser").value("history", [], list)
        for entry in history:
            item = QListWidgetItem(load_icon("history"), f"{entry['title']} ({entry['url']}) - {entry['time']}")
            item.setData(Qt.UserRole, entry['url'])
            self.history_list.addItem(item)
        self.history_list.itemClicked.connect(self.open_bookmark)

    def filter_items(self):
        query = self.search_bar.text().lower()
        for i in range(self.bookmarks_list.count()):
            item = self.bookmarks_list.item(i)
            item.setHidden(query not in item.text().lower())
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            item.setHidden(query not in item.text().lower())

    def open_bookmark(self, item):
        url = item.data(Qt.UserRole)
        self.parent().add_new_tab(QUrl(url))

    def export_bookmarks_html(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Bookmarks", "bookmarks.html", "HTML (*.html)")
        if path:
            bookmarks = QSettings("SecureVeil", "Browser").value("bookmarks", [], list)
            html = "<!DOCTYPE NETSCAPE-Bookmark-file-1>\n"
            html += "<META HTTP-EQUIV='Content-Type' CONTENT='text/html; charset=UTF-8'>\n"
            html += "<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks</H1>\n<DL><p>\n"
            for bookmark in bookmarks:
                html += f"<DT><A HREF='{bookmark['url']}'>{bookmark['title']}</A>\n"
            html += "</DL><p>\n"
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            self.parent().status_bar.showMessage("Bookmarks exported as HTML", 3000)

    def clear_history(self):
        QSettings("SecureVeil", "Browser").setValue("history", [])
        self.load_history()
        self.parent().status_bar.showMessage("History cleared", 3000)

class ExtensionManager:
    """Basic extension support for user scripts"""
    def __init__(self, profile):
        self.profile = profile
        self.scripts = []
        self.load_scripts()

    def load_scripts(self):
        script_dir = QSettings("SecureVeil", "Browser").value("extension_dir", os.path.expanduser("~/SecureVeilExtensions"), str)
        if not os.path.exists(script_dir):
            os.makedirs(script_dir)
        for filename in os.listdir(script_dir):
            if filename.endswith(".js"):
                with open(os.path.join(script_dir, filename), 'r', encoding='utf-8') as f:
                    script_content = f.read()
                script = QWebEngineScript()
                script.setName(filename)
                script.setSourceCode(script_content)
                script.setInjectionPoint(QWebEngineScript.DocumentReady)
                script.setWorldId(QWebEngineScript.MainWorld)
                script.setRunsOnSubFrames(True)
                self.profile.scripts().insert(script)
                self.scripts.append(script)
                logger.info(f"Loaded extension: {filename}")

    def unload_scripts(self):
        for script in self.scripts:
            self.profile.scripts().remove(script)
        self.scripts.clear()

class SettingsDialog(QDialog):
    """Comprehensive settings dialog with shortcuts and extensions"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setWindowIcon(load_icon("settings"))
        self.init36()

    def init36(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        self.tab_widget = QTabWidget()

        general_widget = QWidget()
        general_layout = QFormLayout()
        general_layout.setSpacing(10)
        self.search_engine = QComboBox()
        self.search_engine.addItems(SEARCH_ENGINES.keys())
        general_layout.addRow("Search Engine:", self.search_engine)
        self.startup_behavior = QComboBox()
        self.startup_behavior.addItems(["Open Home Page", "Restore Last Session"])
        general_layout.addRow("Startup:", self.startup_behavior)
        self.download_path = QLineEdit()
        browse_btn = QPushButton(load_icon("folder"), "Browse")
        browse_btn.clicked.connect(self.browse_download_path)
        download_layout = QHBoxLayout()
        download_layout.addWidget(self.download_path)
        download_layout.addWidget(browse_btn)
        general_layout.addRow("Download Path:", download_layout)
        self.extension_dir = QLineEdit()
        browse_ext_btn = QPushButton(load_icon("folder"), "Browse")
        browse_ext_btn.clicked.connect(self.browse_extension_dir)
        ext_layout = QHBoxLayout()
        ext_layout.addWidget(self.extension_dir)
        ext_layout.addWidget(browse_ext_btn)
        general_layout.addRow("Extension Directory:", ext_layout)
        general_widget.setLayout(general_layout)
        self.tab_widget.addTab(general_widget, load_icon("general"), "General")

        privacy_widget = QWidget()
        privacy_layout = QFormLayout()
        privacy_layout.setSpacing(10)
        self.privacy_mode = QComboBox()
        self.privacy_mode.addItems(PRIVACY_MODES.keys())
        privacy_layout.addRow("Privacy Mode:", self.privacy_mode)
        self.tor_bridges = QCheckBox("Use Tor Bridges")
        privacy_layout.addRow("Tor Bridges:", self.tor_bridges)
        self.https_enforce = QCheckBox("Enforce HTTPS")
        self.https_enforce.setChecked(True)
        privacy_layout.addRow("HTTPS Enforcement:", self.https_enforce)
        privacy_widget.setLayout(privacy_layout)
        self.tab_widget.addTab(privacy_widget, load_icon("privacy"), "Privacy")

        appearance_widget = QWidget()
        appearance_layout = QFormLayout()
        appearance_layout.setSpacing(10)
        self.theme = QComboBox()
        self.theme.addItems(THEMES.keys())
        appearance_layout.addRow("Theme:", self.theme)
        self.new_tab_background = QLineEdit()
        browse_bg_btn = QPushButton(load_icon("image"), "Browse")
        browse_bg_btn.clicked.connect(self.browse_new_tab_background)
        bg_layout = QHBoxLayout()
        bg_layout.addWidget(self.new_tab_background)
        bg_layout.addWidget(browse_bg_btn)
        appearance_layout.addRow("New Tab Background:", bg_layout)
        appearance_widget.setLayout(appearance_layout)
        self.tab_widget.addTab(appearance_widget, load_icon("appearance"), "Appearance")

        shortcuts_widget = QWidget()
        shortcuts_layout = QVBoxLayout()
        shortcuts_layout.setSpacing(10)
        shortcuts_label = QLabel("Keyboard Shortcuts:")
        shortcuts_label.setFont(QFont("Segoe UI", 14))
        shortcuts_layout.addWidget(shortcuts_label)
        shortcuts_list = QListWidget()
        shortcuts = [
            ("Ctrl+T", "New Tab"),
            ("Ctrl+Shift+P", "New Private Tab"),
            ("Ctrl+W", "Close Tab"),
            ("Ctrl+Tab", "Next Tab"),
            ("Ctrl+Shift+Tab", "Previous Tab"),
            ("Ctrl+F", "Focus Search Bar"),
            ("Ctrl+L", "Focus URL Bar")
        ]
        for key, desc in shortcuts:
            item = QListWidgetItem(load_icon("keyboard"), f"{key}: {desc}")
            shortcuts_list.addItem(item)
        shortcuts_layout.addWidget(shortcuts_list)
        shortcuts_widget.setLayout(shortcuts_layout)
        self.tab_widget.addTab(shortcuts_widget, load_icon("keyboard"), "Shortcuts")

        layout.addWidget(self.tab_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self.load_settings()

    def browse_download_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Download Directory", self.download_path.text())
        if path:
            self.download_path.setText(path)

    def browse_extension_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Select Extension Directory", self.extension_dir.text())
        if path:
            self.extension_dir.setText(path)

    def browse_new_tab_background(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Background Image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.new_tab_background.setText(path)

    def load_settings(self):
        settings = QSettings("SecureVeil", "Browser")
        self.search_engine.setCurrentText(settings.value("search_engine", "DuckDuckGo", str))
        self.startup_behavior.setCurrentText(settings.value("startup_behavior", "Open Home Page", str))
        self.download_path.setText(settings.value("download_path", os.path.expanduser("~/Downloads"), str))
        self.extension_dir.setText(settings.value("extension_dir", os.path.expanduser("~/SecureVeilExtensions"), str))
        self.privacy_mode.setCurrentText(settings.value("privacy_mode", "Balanced", str))
        self.tor_bridges.setChecked(settings.value("tor_bridges", False, bool))
        self.https_enforce.setChecked(settings.value("https_enforce", True, bool))
        self.theme.setCurrentText(settings.value("theme", "Dark", str))
        self.new_tab_background.setText(settings.value("new_tab_background", "", str))

    def save_settings(self):
        settings = QSettings("SecureVeil", "Browser")
        settings.setValue("search_engine", self.search_engine.currentText())
        settings.setValue("startup_behavior", self.startup_behavior.currentText())
        settings.setValue("download_path", self.download_path.text())
        settings.setValue("extension_dir", self.extension_dir.text())
        settings.setValue("privacy_mode", self.privacy_mode.currentText())
        settings.setValue("tor_bridges", self.tor_bridges.isChecked())
        settings.setValue("https_enforce", self.https_enforce.isChecked())
        settings.setValue("theme", self.theme.currentText())
        settings.setValue("new_tab_background", self.new_tab_background.text())

class CustomTabBar(QTabBar):
    """Tab bar with preview and favicon support"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setExpanding(False)
        self.tab_previews = {}
        self.tab_favicons = {}
        self.setFont(QFont("Segoe UI", 12))

    def mouseMoveEvent(self, event):
        index = self.tabAt(event.pos())
        if index >= 0 and index in self.tab_previews:
            pixmap = self.tab_previews[index]
            QToolTip.showText(event.globalPos(), "", self)
            tooltip = QWidget()
            label = QLabel(tooltip)
            label.setPixmap(pixmap)
            tooltip.move(event.globalPos())
            tooltip.show()
            QTimer.singleShot(1000, tooltip.hide)
        super().mouseMoveEvent(event)

    def update_preview(self, index, pixmap):
        self.tab_previews[index] = pixmap

    def update_favicon(self, index, icon):
        self.tab_favicons[index] = icon
        self.setTabIcon(index, icon)

class SecureVeilBrowser(QMainWindow):
    """Main browser window"""
    def __init__(self):
        super().__init__()
        self.tor_manager = TorManager()
        # Create a temporary directory for profiles
        self.temp_dir = tempfile.TemporaryDirectory(prefix="secureveil_")
        # Set default profile with valid name and cache path
        cache_path = os.path.join(self.temp_dir.name, "default_cache")
        os.makedirs(cache_path, exist_ok=True)
        self.default_profile = QWebEngineProfile("default")
        self.default_profile.setCachePath(cache_path)
        self.default_profile.setPersistentStoragePath(cache_path)
        self.private_profiles = {}
        self.tracker_blocker = TrackerBlocker()
        self.default_profile.setUrlRequestInterceptor(self.tracker_blocker)
        self.tracker_blocker.tracker_count_signal.connect(self.update_tracker_count)
        self.extension_manager = ExtensionManager(self.default_profile)
        self.tracker_count = 0
        self.tab_count = 0
        self.settings = QSettings("SecureVeil", "Browser")
        self.downloads = {}
        self.top_sites = self.load_top_sites()
        self.init36()
        self.default_profile.downloadRequested.connect(self.handle_profile_download)
        self.tor_manager.start_tor()
        self.security_dashboard.new_identity_requested.connect(self.request_new_identity)

    def load_top_sites(self):
        return [
            {"title": "Example", "url": "https://example.com"},
            {"title": "Privacy Tools", "url": "https://privacytools.io"}
        ]

    def init36(self):
        self.setWindowTitle("SecureVeil Browser")
        self.setWindowIcon(load_icon("secureveil"))
        self.setMinimumSize(1280, 720)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.menu_bar = QMenuBar()
        file_menu = self.menu_bar.addMenu("File")
        new_tab_action = QAction(load_icon("new-tab"), "New Tab", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(lambda: self.add_new_tab())
        file_menu.addAction(new_tab_action)
        new_private_tab_action = QAction(load_icon("private"), "New Private Tab", self)
        new_private_tab_action.setShortcut("Ctrl+Shift+P")
        new_private_tab_action.triggered.connect(lambda: self.add_new_tab(is_private=True))
        file_menu.addAction(new_private_tab_action)
        file_menu.addSeparator()
        close_tab_action = QAction(load_icon("close"), "Close Tab", self)
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.triggered.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        file_menu.addAction(close_tab_action)
        file_menu.addSeparator()
        exit_action = QAction(load_icon("exit"), "Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = self.menu_bar.addMenu("Edit")
        settings_action = QAction(load_icon("settings"), "Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)
        edit_menu.addAction(settings_action)

        bookmarks_menu = self.menu_bar.addMenu("Bookmarks")
        add_bookmark_action = QAction(load_icon("bookmark-add"), "Add Bookmark", self)
        add_bookmark_action.setShortcut("Ctrl+D")
        add_bookmark_action.triggered.connect(self.add_bookmark)
        bookmarks_menu.addAction(add_bookmark_action)
        manage_bookmarks_action = QAction(load_icon("bookmarks"), "Manage Bookmarks", self)
        manage_bookmarks_action.triggered.connect(self.open_bookmark_manager)
        bookmarks_menu.addAction(manage_bookmarks_action)
        import_bookmarks_action = QAction(load_icon("import"), "Import Bookmarks", self)
        import_bookmarks_action.triggered.connect(self.import_bookmarks_html)
        bookmarks_menu.addAction(import_bookmarks_action)

        self.layout.addWidget(self.menu_bar)

        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        self.layout.addWidget(self.toolbar)

        back_btn = QAction(load_icon("back"), "Back", self)
        back_btn.setShortcut("Alt+Left")
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        self.toolbar.addAction(back_btn)

        forward_btn = QAction(load_icon("forward"), "Forward", self)
        forward_btn.setShortcut("Alt+Right")
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        self.toolbar.addAction(forward_btn)

        reload_btn = QAction(load_icon("reload"), "Reload", self)
        reload_btn.setShortcut("F5")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        self.toolbar.addAction(reload_btn)

        home_btn = QAction(load_icon("home"), "Home", self)
        home_btn.setShortcut("Alt+Home")
        home_btn.triggered.connect(self.navigate_home)
        self.toolbar.addAction(home_btn)

        self.toolbar.addSeparator()

        self.shield_btn = QAction(load_icon("shield"), "Privacy Shield", self)
        self.shield_menu = QMenu()
        self.shield_btn.setMenu(self.shield_menu)
        self.toolbar.addAction(self.shield_btn)

        self.toolbar.addSeparator()

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search query...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setFixedHeight(36)
        self.toolbar.addWidget(self.url_bar)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Quick search...")
        self.search_bar.setFixedWidth(200)
        self.search_bar.returnPressed.connect(self.quick_search)
        self.toolbar.addWidget(self.search_bar)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.tab_bar = CustomTabBar()
        self.tabs.setTabBar(self.tab_bar)
        self.layout.addWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.status_bar.setFixedHeight(30)
        self.layout.addWidget(self.status_bar)

        self.tracker_status = QLabel("Trackers Blocked: 0")
        self.tracker_status.setFont(QFont("Segoe UI", 12))
        self.status_bar.addPermanentWidget(self.tracker_status)

        self.tor_status = QLabel("Tor: Disconnected")
        self.tor_status.setFont(QFont("Segoe UI", 12))
        self.status_bar.addPermanentWidget(self.tor_status)

        self.download_status = QLabel("Downloads: 0 active")
        self.download_status.setFont(QFont("Segoe UI", 12))
        self.status_bar.addPermanentWidget(self.download_status)

        self.sidebar = Sidebar(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sidebar)

        self.security_dashboard = SecurityDashboard(self)
        security_dock = QDockWidget("Security Dashboard", self)
        security_dock.setWidget(self.security_dashboard)
        self.addDockWidget(Qt.RightDockWidgetArea, security_dock)

        self.download_manager = DownloadManager(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.download_manager)
        self.download_manager.status_message.connect(lambda msg, timeout: self.status_bar.showMessage(msg, timeout))

        self.add_new_tab()
        self.tab_count = 1

        self.apply_theme()

        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave_session)
        self.autosave_timer.start(300000)

        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self.update_tab_previews)
        self.preview_timer.start(60000)

        QTimer.singleShot(1000, self.update_tor_status)

        if self.settings.value("startup_behavior", "Open Home Page", str) == "Restore Last Session":
            QTimer.singleShot(0, self.restore_session)

    def apply_theme(self):
        theme = self.settings.value("theme", "Dark", str)
        self.setStyleSheet(THEMES.get(theme, THEMES["Dark"]))
        palette = QPalette()
        if theme == "Dark":
            palette.setColor(QPalette.WindowText, QColor("#ffffff"))
            palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
            palette.setColor(QPalette.Text, QColor("#ffffff"))
            palette.setColor(QPalette.Base, QColor("#27272a"))
        else:
            palette.setColor(QPalette.WindowText, QColor("#000000"))
            palette.setColor(QPalette.ButtonText, QColor("#000000"))
            palette.setColor(QPalette.Text, QColor("#000000"))
            palette.setColor(QPalette.Base, QColor("#ffffff"))
        self.setPalette(palette)
        self.status_bar.setStyleSheet(f"background-color: {'#27272a' if theme == 'Dark' else '#e0e0e0'}; color: {'#ffffff' if theme == 'Dark' else '#000000'};")
        for i in range(self.tabs.count()):
            self.tab_bar.setTabData(i, {"private": self.tabs.widget(i).custom_page.is_private})

    def add_new_tab(self, url=None, is_private=False):
        profile = self.get_profile(is_private)
        browser = SecureWebView(profile, self, is_private)
        browser.urlChanged.connect(self.update_url_bar)
        browser.faviconChanged.connect(lambda icon: self.tab_bar.update_favicon(self.tabs.indexOf(browser), icon))
        browser.loadFinished.connect(lambda ok: self.tab_bar.update_preview(self.tabs.indexOf(browser), browser.get_preview()))
        index = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(index)
        self.tab_count += 1
        browser.tab_index = index
        self.tab_bar.setTabData(index, {"private": is_private})
        if url:
            browser.load(url)
        else:
            browser.load(QUrl("about:blank"))
        self.status_bar.showMessage(f"New {'private' if is_private else 'regular'} tab opened", 3000)
        return browser

    def create_new_tab(self, is_private=False):
        return self.add_new_tab(is_private=is_private)

    def get_profile(self, is_private):
        if not is_private:
            return self.default_profile
        profile_id = str(uuid4())
        cache_path = os.path.join(self.temp_dir.name, f"private_{profile_id}")
        os.makedirs(cache_path, exist_ok=True)
        profile = QWebEngineProfile(f"private-{profile_id}")
        profile.setCachePath(cache_path)
        profile.setPersistentStoragePath("")  # Disable persistent storage
        profile.setHttpUserAgent(random.choice(DEFAULT_USER_AGENTS))
        profile.setUrlRequestInterceptor(self.tracker_blocker)
        self.private_profiles[profile_id] = profile
        logger.info(f"Created private profile: {profile_id}")
        return profile

    def handle_profile_download(self, download, browser=None):
        if browser is None:
            browser = self.tabs.currentWidget()
        if browser:
            browser.handle_download(download)
        self.download_manager.add_download(download)

    def navigate_to_url(self):
        url_text = self.url_bar.text().strip()
        if not url_text:
            return
        if not (url_text.startswith("http://") or url_text.startswith("https://")):
            if "." in url_text and not " " in url_text:
                url_text = "https://" + url_text
            else:
                search_engine = self.settings.value("search_engine", "DuckDuckGo", str)
                search_url = SEARCH_ENGINES.get(search_engine, SEARCH_ENGINES["DuckDuckGo"])
                url_text = search_url.format(url_text.replace(" ", "+"))
        url = QUrl(url_text)
        if url.isValid():
            current_tab = self.tabs.currentWidget()
            if current_tab:
                current_tab.load(url)
                self.add_to_history(url.toString(), current_tab.title() or url_text)
        else:
            self.status_bar.showMessage("Invalid URL", 3000)

    def quick_search(self):
        query = self.search_bar.text().strip()
        if query:
            search_engine = self.settings.value("search_engine", "DuckDuckGo", str)
            search_url = SEARCH_ENGINES.get(search_engine, SEARCH_ENGINES["DuckDuckGo"])
            url = QUrl(search_url.format(query.replace(" ", "+")))
            current_tab = self.tabs.currentWidget()
            if current_tab:
                current_tab.load(url)
                self.add_to_history(url.toString(), query)
        else:
            self.status_bar.showMessage("Enter a search query", 3000)

    def navigate_home(self):
        home_url = QUrl("about:blank")  # Could be customized via settings
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.load(home_url)
            self.add_to_history(home_url.toString(), "Home")

    def update_url_bar(self, url):
        self.url_bar.setText(url.toString())
        current_tab = self.tabs.currentWidget()
        if current_tab:
            self.tabs.setTabText(self.tabs.currentIndex(), current_tab.title() or "New Tab")

    def update_shield_menu(self):
        """Update the privacy shield menu with current settings"""
        self.shield_menu.clear()
        current_tab = self.tabs.currentWidget()
        if not current_tab:
            return

        privacy_settings = current_tab.privacy_settings

        # JavaScript toggle
        js_action = QAction(f"JavaScript: {'Enabled' if privacy_settings['javascript'] else 'Disabled'}", self)
        js_action.setCheckable(True)
        js_action.setChecked(privacy_settings['javascript'])
        js_action.toggled.connect(lambda checked: current_tab.update_privacy_settings({"javascript": checked}))
        self.shield_menu.addAction(js_action)

        # Cookies toggle
        cookies_action = QAction(f"Cookies: {privacy_settings['cookies']}", self)
        cookies_action.setCheckable(True)
        cookies_action.setChecked(privacy_settings['cookies'] != "Block All")
        cookies_action.toggled.connect(
            lambda checked: current_tab.update_privacy_settings({"cookies": "Session Only" if checked else "Block All"})
        )
        self.shield_menu.addAction(cookies_action)

        # Media toggle
        media_action = QAction(f"Media Autoplay: {'Enabled' if privacy_settings['media'] else 'Disabled'}", self)
        media_action.setCheckable(True)
        media_action.setChecked(privacy_settings['media'])
        media_action.toggled.connect(lambda checked: current_tab.update_privacy_settings({"media": checked}))
        self.shield_menu.addAction(media_action)

        # WebGL toggle
        webgl_action = QAction(f"WebGL: {'Enabled' if privacy_settings['webgl'] else 'Disabled'}", self)
        webgl_action.setCheckable(True)
        webgl_action.setChecked(privacy_settings['webgl'])
        webgl_action.toggled.connect(lambda checked: current_tab.update_privacy_settings({"webgl": checked}))
        self.shield_menu.addAction(webgl_action)

        # Separator
        self.shield_menu.addSeparator()

        # Privacy mode info
        privacy_mode = self.settings.value("privacy_mode", "Balanced", str)
        if current_tab.custom_page.is_private:
            privacy_mode = "Strict (Private Mode)"
        mode_action = QAction(f"Privacy Mode: {privacy_mode}", self)
        mode_action.setEnabled(False)
        self.shield_menu.addAction(mode_action)

        # Tracker count
        tracker_action = QAction(f"Trackers Blocked: {self.tracker_count}", self)
        tracker_action.setEnabled(False)
        self.shield_menu.addAction(tracker_action)

    def update_tracker_count(self, count):
        """Update the tracker count in the UI"""
        self.tracker_count = count
        self.tracker_status.setText(f"Trackers Blocked: {count}")
        self.security_dashboard.update_tracker_count(count)
        self.update_shield_menu()

    def update_tor_status(self):
        """Update the Tor connection status"""
        status = "Tor: Connected" if self.tor_manager.tor_initialized else "Tor: Disconnected"
        self.tor_status.setText(status)
        self.security_dashboard.update_route_status(status)
        if not self.tor_manager.tor_initialized:
            QTimer.singleShot(5000, self.update_tor_status)

    def tab_changed(self, index):
        """Handle tab change events"""
        if index >= 0:
            browser = self.tabs.widget(index)
            self.update_url_bar(browser.url())
            self.update_shield_menu()
            self.tabs.setTabText(index, browser.title() or "New Tab")
            self.tab_bar.update_preview(index, browser.get_preview())

    def close_tab(self, index):
        """Close a tab at the given index"""
        if self.tab_count > 1:
            browser = self.tabs.widget(index)
            if browser.custom_page.is_private:
                profile_id = browser.page().profile().cachePath().split("private_")[-1]
                if profile_id in self.private_profiles:
                    browser.page().deleteLater()  # Ensure page is deleted
                    self.private_profiles[profile_id].deleteLater()
                    del self.private_profiles[profile_id]
            self.tabs.removeTab(index)
            self.tab_count -= 1
            self.status_bar.showMessage("Tab closed", 3000)
            self.tab_bar.tab_previews.pop(index, None)
            self.tab_bar.tab_favicons.pop(index, None)
            for i in range(self.tabs.count()):
                self.tabs.widget(i).tab_index = i
                self.tab_bar.setTabData(i, {"private": self.tabs.widget(i).custom_page.is_private})

    def add_to_history(self, url, title):
        """Add a URL to the browsing history"""
        history = self.settings.value("history", [], list)
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        history.append({"url": url, "title": title, "time": timestamp})
        self.settings.setValue("history", history[:1000])  # Limit history to 1000 entries
        self.sidebar.load_history()

    def add_bookmark(self):
        """Add the current page to bookmarks"""
        current_tab = self.tabs.currentWidget()
        if current_tab:
            url = current_tab.url().toString()
            title = current_tab.title() or url
            bookmarks = self.settings.value("bookmarks", [], list)
            bookmarks.append({"title": title, "url": url})
            self.settings.setValue("bookmarks", bookmarks)
            self.sidebar.load_bookmarks()
            self.status_bar.showMessage(f"Bookmarked: {title}", 3000)

    def open_bookmark_manager(self):
        """Open the bookmark manager dialog"""
        dialog = BookmarkManager(self)
        if dialog.exec_():
            self.sidebar.load_bookmarks()
            self.status_bar.showMessage("Bookmarks updated", 3000)

    def import_bookmarks_html(self):
        """Import bookmarks from an HTML file"""
        dialog = BookmarkManager(self)
        dialog.import_bookmarks_html()
        self.sidebar.load_bookmarks()

    def open_settings(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec_():
            dialog.save_settings()
            self.apply_theme()
            self.extension_manager.unload_scripts()
            self.extension_manager.load_scripts()
            for i in range(self.tabs.count()):
                browser = self.tabs.widget(i)
                if not browser.custom_page.is_private:
                    browser.apply_privacy_settings(is_private=False)
            self.status_bar.showMessage("Settings saved", 3000)

    def request_new_identity(self):
        """Request a new Tor identity"""
        if self.tor_manager.new_identity():
            self.status_bar.showMessage("New Tor identity acquired", 3000)
            for i in range(self.tabs.count()):
                browser = self.tabs.widget(i)
                if not browser.custom_page.is_private:
                    browser.reload()
        else:
            self.status_bar.showMessage("Failed to acquire new Tor identity", 3000)

    def autosave_session(self):
        """Autosave the current session"""
        session = []
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            session.append({
                "url": browser.url().toString(),
                "title": browser.title(),
                "is_private": browser.custom_page.is_private
            })
        self.settings.setValue("session", session)
        logger.info("Session autosaved")

    def restore_session(self):
        """Restore the previous session"""
        session = self.settings.value("session", [], list)
        if session:
            self.tabs.clear()
            self.tab_count = 0
            for tab in session:
                self.add_new_tab(QUrl(tab["url"]), is_private=tab["is_private"])
                self.tabs.setTabText(self.tab_count - 1, tab["title"] or "New Tab")
            self.status_bar.showMessage("Session restored", 3000)

    def update_tab_previews(self):
        """Update previews for all tabs"""
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            self.tab_bar.update_preview(i, browser.get_preview())

    def update_download_status(self, download, state):
        """Update download status in the UI"""
        active_downloads = sum(1 for d in self.downloads.values() if d["download"].state() == QWebEngineDownloadItem.DownloadInProgress)
        self.download_status.setText(f"Downloads: {active_downloads} active")

    def closeEvent(self, event):
        """Handle window close event"""
        self.autosave_session()
        self.tor_manager.stop_tor()
        self.extension_manager.unload_scripts()
        # Clean up all tabs and profiles
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            browser.page().deleteLater()  # Ensure page is deleted
            if browser.custom_page.is_private:
                profile_id = browser.page().profile().cachePath().split("private_")[-1]
                if profile_id in self.private_profiles:
                    self.private_profiles[profile_id].deleteLater()
                    del self.private_profiles[profile_id]
        self.default_profile.deleteLater()
        self.temp_dir.cleanup()  # Clean up temporary directory
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    browser = SecureVeilBrowser()
    browser.show()
    sys.exit(app.exec_())