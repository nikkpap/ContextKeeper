# ContextKeeper
Right-Click Menu Backup & Restore Utility for Windows

ContextKeeper is a lightweight Windows utility that allows you to export, merge, and restore all Windows context-menu registry keys into a single .reg file.
It also includes smart admin elevation, flexible save locations, and a modern GUI built with Tkinter.

This tool is ideal for power users, IT technicians, and anyone customizing the Windows context menu who wants a reliable way to back up and restore their configuration.

⭐ Features
🔐 Full Context Menu Backup

Exports all relevant registry paths, including:

HKEY_CLASSES_ROOT\*\shell

HKEY_CLASSES_ROOT\*\shellex

HKEY_CLASSES_ROOT\AllFilesystemObjects

HKEY_CLASSES_ROOT\Directory

HKEY_CLASSES_ROOT\Directory\Background

HKEY_CLASSES_ROOT\Drive

HKEY_CLASSES_ROOT\Folder

All entries are merged automatically into one clean .reg file.

🗃️ Custom Save Location

Choose exactly where you want to save your backup:

Desktop

NAS (e.g., Theia)

External drives

Network folders

Any file system path
via a standard Save As dialog.

🚀 Smart Admin Elevation (UAC Prompt)

If the app is launched without admin rights:

It automatically relaunches itself using pythonw.exe

Requests elevation through ShellExecuteW("runas")

Runs cleanly without showing any console window

🔄 Easy Restoration

Import any existing .reg backup through the GUI:

Uses reg import internally

Shows logs for every operation

Warns if not elevated during restore

📁 Open Last Backup Folder

The app remembers the exact file path of your last backup and can open that folder instantly.

📝 Activity Log

All operations show real-time log output:

Export commands

Success / warnings / errors

Merge operations

Restore events

📦 Installation
Requirements:

Windows 10 or Windows 11

Python 3.10+ (recommended)

No external packages required (pure Tkinter + ctypes)

Clone or download the repository and run:

context_menu_backup.pyw


Running the .pyw extension ensures:

No console window is shown

Clean GUI-only experience

▶️ Usage
1. Create Backup

Click “Create FULL Backup (.reg)”

Choose save location (any folder or drive)

The app exports all registry keys

Generates ContextMenu_ALL.reg (or your chosen name)

2. Restore Backup

Click “Restore from .reg file”

Select any .reg file

Imports back into Windows Registry

Note: Restoration works best when running as Administrator.

3. Open Backup Folder

Opens the folder of the last created backup

Falls back to Desktop or default backup folder if needed

🛡️ Why Use ContextKeeper?

Because Windows context menus are complicated, scattered across many registry locations, and easy to break when installing/uninstalling apps.

ContextKeeper solves that by giving you:

A safe snapshot of all context menu items

Easy one-click restore

Full control of your right-click configuration

Your right-click menu deserves protection. ContextKeeper does exactly that.

📜 License

This project is open-source and free to modify.
