SecureVeil Browser
SecureVeil Browser is a privacy-focused web browser built with PyQt5, designed to provide users with enhanced security and anonymity features. It integrates Tor for anonymous browsing, includes a tracker blocker, supports private browsing modes, and offers a customizable user interface with bookmark and download management.
Features

Tor Integration: Routes traffic through the Tor network for anonymous browsing, with support for new identity requests and Tor bridges.
Tracker Blocking: Uses predefined blocklists (e.g., EasyList, EasyPrivacy) to block trackers and ads, with real-time tracking statistics.
Private Browsing: Offers strict privacy modes with isolated profiles, disabling JavaScript, cookies, WebGL, and media autoplay as needed.
Customizable Privacy Modes: Choose from Strict, Balanced, or Minimal privacy settings to balance security and functionality.
Bookmark Management: Organize bookmarks with a dedicated manager, including import/export functionality in HTML format.
Download Manager: Advanced download management with pause/resume, sorting, filtering, and folder integration.
Security Dashboard: Displays real-time tracker counts, Tor connection status, and resource usage (CPU, memory).
Sidebar: Quick access to bookmarks and browsing history with search functionality.
Extension Support: Basic support for user scripts loaded from a designated directory.
Customizable UI: Supports Dark and Light themes, customizable new tab backgrounds, and configurable settings like search engines and download paths.
Session Management: Autosaves sessions and supports restoring previous sessions on startup.

Requirements

Python 3.8+
PyQt5
PyQtWebEngine
psutil
requests
PySocks
stem
beautifulsoup4

Install dependencies using:
pip install PyQt5 PyQtWebEngine psutil requests pysocks stem beautifulsoup4

Additionally, ensure the Tor executable is installed and accessible on your system. On Linux, you can install it with:
sudo apt-get install tor

On Windows or macOS, download and install Tor from the official website.
Installation

Clone or download the repository.
Ensure all dependencies are installed (see Requirements).
Place the main.py file in your project directory.
Create an icons folder in the same directory as main.py and populate it with the required icon files (e.g., secureveil.png, back.png, etc.). Alternatively, the browser will log warnings for missing icons and use default placeholders.
Run the browser:

python main.py

Usage

Launch the Browser: Run main.py to start SecureVeil Browser.
Navigation: Use the URL bar to enter URLs or search queries, or use the quick search bar for instant searches.
Tabs: Open new tabs with Ctrl+T, private tabs with Ctrl+Shift+P, and close tabs with Ctrl+W.
Privacy Controls: Access the Privacy Shield menu via the toolbar to toggle JavaScript, cookies, media, and WebGL. Adjust privacy modes (Strict, Balanced, Minimal) in the Security Dashboard or Settings.
Tor: Monitor Tor connection status in the Security Dashboard. Request a new Tor identity using the "New Identity" button.
Bookmarks: Add bookmarks with Ctrl+D, manage them via the Bookmarks menu or Sidebar, and import/export as HTML.
Downloads: View and manage downloads in the Download Manager dock, with options to pause, resume, cancel, or open files.
Settings: Customize search engines, download paths, themes, and more via the Settings dialog (Ctrl+,).
Sidebar: Search and access bookmarks and history from the Sidebar dock.
Security Dashboard: Monitor trackers blocked, resource usage, and Tor status.

Configuration
Settings are stored using QSettings under the organization name SecureVeil and application name Browser. Key configurable options include:

Search Engine: Choose from DuckDuckGo, Startpage, or Brave Search.
Privacy Mode: Select Strict, Balanced, or Minimal.
Theme: Switch between Dark and Light themes.
Download Path: Set the default download directory.
Extension Directory: Specify a folder for loading user scripts.
Tor Bridges: Enable/disable Tor bridges for enhanced anonymity.
HTTPS Enforcement: Force HTTPS for all connections.

Directory Structure
project_directory/
├── main.py               # Main browser application
├── icons/                # Icon files (e.g., secureveil.png, back.png)
├── secureveil.log        # Log file for debugging
└── ~/SecureVeilExtensions/  # Default extension directory (configurable)

Logging
The browser logs events to secureveil.log in the project directory. Log levels include INFO, WARNING, ERROR, and DEBUG, with details on Tor initialization, tracker blocking, and errors.
Known Limitations

Tor Dependency: Requires a working Tor installation and may fail if Tor is not properly configured.
Extension Support: Limited to basic user scripts; no full-fledged extension framework.
Resource Usage: High memory usage in private tabs due to isolated profiles.
Icon Dependency: Missing icons will trigger warnings but won't crash the application.
Platform-Specific Issues: Some features (e.g., Tor process handling) may behave differently on Windows, macOS, or Linux.

Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a feature branch (git checkout -b feature-name).
Commit changes (git commit -m "Add feature").
Push to the branch (git push origin feature-name).
Open a pull request.

Please include tests and update documentation as needed.
License
This project is licensed under the MIT License. See the LICENSE file for details.
Acknowledgments

Built with PyQt5 and PyQtWebEngine.
Uses Tor for anonymous browsing.
Tracker blocking powered by EasyList and EasyPrivacy.
Icon assets (not included) should be sourced from a compatible icon set.

