# context_menu_backup.pyw
# Full GUI app to backup & restore Windows context menu registry keys into ONE .reg file
# Now with smart auto-elevate to Administrator using ShellExecuteW("runas", ...)

import os
import sys
import subprocess
import shutil
import datetime
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText

APP_TITLE = "ContextKeeper"
APP_VERSION = "v1.1"


def is_windows():
    return os.name == "nt"


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def elevate_if_needed():
    """
    Relaunch the script with admin rights AND without a console window.
    Works for both .py and .pyw, but runs cleanest as .pyw.
    """
    if is_admin():
        return  # already admin

    # Path to pythonw.exe for no-console execution
    pythonw = sys.executable
    if pythonw.lower().endswith("python.exe"):
        pythonw = pythonw.replace("python.exe", "pythonw.exe")

    # Build command line parameters
    if getattr(sys, "frozen", False):
        # For PyInstaller EXE build
        target = sys.executable
        params = " ".join(f'"{a}"' for a in sys.argv[1:])
    else:
        target = pythonw  # run with no console
        params = " ".join(f'"{a}"' for a in sys.argv)

    try:
        rc = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            target,
            params,
            None,
            0  # SW_HIDE → NO CONSOLE WINDOW
        )

        if rc > 32:
            # Relaunch succeeded → exit old process
            os._exit(0)
        else:
            return  # user cancelled UAC
    except Exception:
        return



def get_desktop_folder():
    return os.path.join(os.path.expanduser("~"), "Desktop")


class ContextMenuBackupApp(tk.Tk):
    def __init__(self):
        super().__init__()

        if not is_windows():
            messagebox.showerror("Error", "This tool only works on Windows.")
            sys.exit(1)

        self.title(f"{APP_TITLE} {APP_VERSION}")
        self.geometry("780x520")
        self.minsize(700, 450)

        # Center window
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.configure(padx=10, pady=10)

        self.backup_dir = os.path.join(get_desktop_folder(), "ContextMenuBackup")
        self.outfile_name = "ContextMenu_ALL.reg"
        self.outfile_path = os.path.join(self.backup_dir, self.outfile_name)

        # NEW: remember last backup file user saved
        self.last_backup_path = None

        self._build_ui()

        if not is_admin():
            self.log(
                "[!] Warning: Application is NOT running as Administrator.\n"
                "Some registry keys may fail to export/import.\n"
                "Right-click this .pyw and choose 'Run as administrator' for best results.\n",
                tag="warn",
            )

    def _build_ui(self):
        # Top frame: title + admin info
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", pady=(0, 10))

        title_label = ttk.Label(
            top_frame,
            text=APP_TITLE,
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(side="left")

        version_label = ttk.Label(
            top_frame,
            text=APP_VERSION,
            font=("Segoe UI", 10)
        )
        version_label.pack(side="left", padx=(6, 0))

        # Admin status
        admin_text = "Running as Administrator" if is_admin() else "NOT running as Administrator"
        admin_color = "#008000" if is_admin() else "#b00000"
        self.admin_label = ttk.Label(
            top_frame,
            text=admin_text,
            foreground=admin_color,
            font=("Segoe UI", 9, "bold")
        )
        self.admin_label.pack(side="right")

        # Info label
        info = (
            "This tool will:\n"
            " • Backup your context menu registry keys into ONE .reg file\n"
            " • Locations: *, AllFilesystemObjects, Directory, Background, Drive, Folder\n"
            " • Restore later by importing the .reg file\n"
        )
        info_label = ttk.Label(self, text=info, justify="left")
        info_label.pack(fill="x", pady=(0, 10))

        # Buttons frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=(0, 10))

        self.btn_backup = ttk.Button(
            btn_frame,
            text="Create FULL Backup (.reg)",
            command=self.on_backup_clicked
        )
        self.btn_backup.pack(side="left", padx=(0, 5))

        self.btn_restore = ttk.Button(
            btn_frame,
            text="Restore from .reg file",
            command=self.on_restore_clicked
        )
        self.btn_restore.pack(side="left", padx=(0, 5))

        self.btn_open_folder = ttk.Button(
            btn_frame,
            text="Open Backup Folder",
            command=self.on_open_folder_clicked
        )
        self.btn_open_folder.pack(side="left", padx=(0, 5))

        # Log area
        log_label = ttk.Label(self, text="Log:")
        log_label.pack(anchor="w")

        self.log_text = ScrolledText(
            self,
            wrap="word",
            height=18,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.config(state="disabled")

        # Tag styles for log
        self.log_text.tag_config("info", foreground="#000000")
        self.log_text.tag_config("warn", foreground="#b00000")
        self.log_text.tag_config("ok", foreground="#006400")
        self.log_text.tag_config("error", foreground="#b00000")
        self.log_text.tag_config("cmd", foreground="#000080")

        # Status bar
        self.status_var = tk.StringVar(value="Ready.")
        status_bar = ttk.Label(
            self,
            textvariable=self.status_var,
            anchor="w",
            relief="sunken"
        )
        status_bar.pack(fill="x", pady=(5, 0))

    def log(self, text, tag="info"):
        self.log_text.config(state="normal")
        self.log_text.insert("end", text, (tag,))
        if not text.endswith("\n"):
            self.log_text.insert("end", "\n", (tag,))
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def set_status(self, text):
        self.status_var.set(text)
        self.update_idletasks()

    # ------------ BACKUP LOGIC ------------ #

    def on_backup_clicked(self):
        if not is_admin():
            if not messagebox.askyesno(
                "Not Administrator",
                "You are NOT running as Administrator.\n\n"
                "Some registry keys may fail to export.\n\n"
                "Do you still want to continue?"
            ):
                return

        # Προτεινόμενος φάκελος: Desktop\ContextMenuBackup
        suggested_dir = self.backup_dir
        try:
            os.makedirs(suggested_dir, exist_ok=True)
        except Exception:
            # αν κάτι πάει στραβά, έστω Desktop
            suggested_dir = get_desktop_folder()

        # Διάλογος: πού να σωθεί το backup;
        save_path = filedialog.asksaveasfilename(
            title="Save FULL context menu backup as...",
            initialdir=suggested_dir,
            initialfile="ContextMenu_ALL.reg",
            defaultextension=".reg",
            filetypes=[("Registry files", "*.reg"), ("All files", "*.*")]
        )
        if not save_path:
            return  # Cancel

        # Βεβαιώσου ότι ο φάκελος υπάρχει
        folder = os.path.dirname(save_path)
        if folder and not os.path.isdir(folder):
            try:
                os.makedirs(folder, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create folder:\n{e}")
                return

        self.log("-" * 60)
        self.log(f"Starting backup at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"Target file:\n{save_path}")
        self.set_status("Backing up registry keys...")

        success = self.create_full_backup(save_path)

        if success:
            # remember last backup file
            self.last_backup_path = save_path

            self.log(f"[OK] Backup complete.\nSaved as:\n{save_path}", tag="ok")
            self.set_status("Backup complete.")
            messagebox.showinfo("Backup Complete", f"Backup saved as:\n{save_path}")
        else:
            self.log("[!] Backup finished with errors. See log above.", tag="warn")
            self.set_status("Backup finished with errors.")
            messagebox.showwarning(
                "Backup Finished",
                "Backup finished, but some keys may have failed.\nCheck the log for details."
            )

    def create_full_backup(self, out_path: str):
        """
        Export all relevant context menu registry keys,
        merge them into one .reg file at out_path, and clean temporary files.
        """
        # List of registry keys to export
        reg_keys = [
            (r"HKEY_CLASSES_ROOT\*\shell",                      "1_star_shell"),
            (r"HKEY_CLASSES_ROOT\*\shellex",                    "2_star_shellex"),
            (r"HKEY_CLASSES_ROOT\AllFilesystemObjects\shell",   "3_allfiles_shell"),
            (r"HKEY_CLASSES_ROOT\AllFilesystemObjects\shellex", "4_allfiles_shellex"),
            (r"HKEY_CLASSES_ROOT\Directory\shell",              "5_directory_shell"),
            (r"HKEY_CLASSES_ROOT\Directory\shellex",            "6_directory_shellex"),
            (r"HKEY_CLASSES_ROOT\Directory\Background\shell",   "7_background_shell"),
            (r"HKEY_CLASSES_ROOT\Directory\Background\shellex", "8_background_shellex"),
            (r"HKEY_CLASSES_ROOT\Drive\shell",                  "9_drive_shell"),
            (r"HKEY_CLASSES_ROOT\Drive\shellex",                "10_drive_shellex"),
            (r"HKEY_CLASSES_ROOT\Folder\shell",                 "11_folder_shell"),
            (r"HKEY_CLASSES_ROOT\Folder\shellex",               "12_folder_shellex"),
        ]

        temp_files = []
        any_success = False

        # Export each key
        for reg_path, base_name in reg_keys:
            temp_file = os.path.join(self.backup_dir, base_name + ".tmp")
            cmd = ["reg", "export", reg_path, temp_file, "/y"]

            self.log(f"[CMD] {' '.join(cmd)}", tag="cmd")
            self.set_status(f"Exporting {reg_path} ...")

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    shell=False
                )
            except FileNotFoundError:
                self.log("[ERROR] 'reg' command not found. This must run on Windows.", tag="error")
                return False
            except Exception as e:
                self.log(f"[ERROR] Failed to run reg export: {e}", tag="error")
                continue

            if result.returncode == 0:
                self.log(f"[OK] Exported {reg_path}", tag="ok")
                temp_files.append(temp_file)
                any_success = True
            else:
                # Some keys may simply not exist on the system – log as warning
                self.log(
                    f"[WARN] Could not export {reg_path} (code {result.returncode}).",
                    tag="warn"
                )
                if result.stderr:
                    self.log(f"       {result.stderr.strip()}", tag="warn")

        # If nothing was exported, stop here
        if not any_success:
            self.log("[ERROR] No keys were exported. Nothing to merge.", tag="error")
            return False

        # Create final .reg file with header at the chosen path
        try:
            with open(out_path, "w", encoding="utf-16le") as out_f:
                # .reg files on modern Windows are typically UTF-16 LE with BOM
                out_f.write("\ufeff")  # BOM
                out_f.write("Windows Registry Editor Version 5.00\r\n\r\n")

                for temp_file in temp_files:
                    if not os.path.isfile(temp_file):
                        continue
                    try:
                        with open(temp_file, "r", encoding="utf-16le", errors="ignore") as tf:
                            lines = tf.readlines()
                    except UnicodeError:
                        # Try ANSI fallback
                        with open(temp_file, "r", encoding="cp1252", errors="ignore") as tf:
                            lines = tf.readlines()

                    # Skip the first line (its own header)
                    if lines:
                        lines = lines[1:]

                    # Ensure blank line separation
                    out_f.writelines(lines)
                    if not (lines and lines[-1].endswith("\n")):
                        out_f.write("\r\n")
                    out_f.write("\r\n")

            self.log(f"[OK] Merged all temporary exports into:\n{out_path}", tag="ok")
        except Exception as e:
            self.log(f"[ERROR] Failed to write final .reg file:\n{e}", tag="error")
            return False
        finally:
            # Clean up temp files
            for temp_file in temp_files:
                try:
                    if os.path.isfile(temp_file):
                        os.remove(temp_file)
                except Exception:
                    pass

        return True

    # ------------ RESTORE LOGIC ------------ #

    def on_restore_clicked(self):
        if not is_admin():
            if not messagebox.askyesno(
                "Not Administrator",
                "You are NOT running as Administrator.\n\n"
                "Restoring registry keys normally requires admin rights.\n\n"
                "Do you still want to continue?"
            ):
                return

        initial_dir = self.backup_dir if os.path.isdir(self.backup_dir) else get_desktop_folder()

        reg_file = filedialog.askopenfilename(
            title="Select .reg file to import",
            initialdir=initial_dir,
            filetypes=[("Registry files", "*.reg"), ("All files", "*.*")]
        )
        if not reg_file:
            return

        self.log("-" * 60)
        self.log(f"Starting restore from:\n{reg_file}")
        self.set_status("Restoring from .reg file...")

        cmd = ["reg", "import", reg_file]
        self.log(f"[CMD] {' '.join(cmd)}", tag="cmd")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=False
            )
        except FileNotFoundError:
            self.log("[ERROR] 'reg' command not found. This must run on Windows.", tag="error")
            self.set_status("Restore failed.")
            messagebox.showerror("Error", "'reg' command not found. This tool must run on Windows.")
            return
        except Exception as e:
            self.log(f"[ERROR] Failed to run reg import: {e}", tag="error")
            self.set_status("Restore failed.")
            messagebox.showerror("Error", f"Failed to run reg import:\n{e}")
            return

        if result.returncode == 0:
            self.log("[OK] Registry import completed successfully.", tag="ok")
            self.set_status("Restore complete.")
            messagebox.showinfo(
                "Restore Complete",
                "Registry successfully imported.\n\n"
                "You may need to restart Explorer or Windows for changes to take full effect."
            )
        else:
            self.log(f"[ERROR] reg import failed (code {result.returncode}).", tag="error")
            if result.stderr:
                self.log(result.stderr.strip(), tag="error")
            self.set_status("Restore failed.")
            messagebox.showerror(
                "Restore Failed",
                f"reg import failed with code {result.returncode}.\n\n"
                f"Details:\n{result.stderr}"
            )

    # ------------ OPEN FOLDER ------------ #

    def on_open_folder_clicked(self):
        # 1. Αν υπάρχει τελευταίο backup και ο φάκελος του υπάρχει, άνοιξε αυτόν
        folder_to_open = None

        if self.last_backup_path and os.path.isfile(self.last_backup_path):
            folder_to_open = os.path.dirname(self.last_backup_path)

        # 2. Αλλιώς δοκίμασε τον default φάκελο backup_dir
        if not folder_to_open:
            if os.path.isdir(self.backup_dir):
                folder_to_open = self.backup_dir

        # 3. Αν πάλι τίποτα, δοκίμασε Desktop
        if not folder_to_open:
            desktop = get_desktop_folder()
            if os.path.isdir(desktop):
                folder_to_open = desktop

        if not folder_to_open:
            messagebox.showwarning(
                "Folder not found",
                "No backup folder or Desktop could be found."
            )
            return

        try:
            os.startfile(folder_to_open)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open folder:\n{e}")



if __name__ == "__main__":
    # Smart auto-elevate: if not admin, ask for UAC and relaunch.
    elevate_if_needed()

    app = ContextMenuBackupApp()
    app.mainloop()
