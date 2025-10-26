import sys
import subprocess
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QTextEdit, QDialog, QGroupBox,
    QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# ---------------- PATCH INFO ----------------
PATCH_INFO = {
    "version": "PATCH 2",
    "notes": [
        "Multi-selectable presets with combined preview",
        "Fast recursive preset scanning in background thread",
        "Readable INI-style presets",
        "Drag-and-drop and PK3 support"
    ]
}
# --------------------------------------------

PRESET_GLOB_DIR = "."  # default search root

class PresetScanner(QThread):
    scanned = pyqtSignal(list)

    def __init__(self, root):
        super().__init__()
        self.root = root
        self._running = True

    def run(self):
        results = []
        try:
            stack = [self.root]
            while stack and self._running:
                current = stack.pop()
                try:
                    with os.scandir(current) as it:
                        for entry in it:
                            if not self._running:
                                break
                            if entry.is_dir(follow_symlinks=False):
                                stack.append(entry.path)
                            elif entry.is_file(follow_symlinks=False) and entry.name.lower().endswith(".preset"):
                                results.append(entry.path)
                except PermissionError:
                    continue
        except Exception:
            pass
        results.sort()
        if self._running:
            self.scanned.emit(results)

    def stop(self):
        self._running = False

class PurpleLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.preset_root = os.path.abspath(PRESET_GLOB_DIR)
        self.scanner = None
        self.setWindowTitle(f"Purple Launcher — {PATCH_INFO['version']}")
        self.setFixedSize(900, 620)
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: black; color: #B400FF;")
        self.selected_engine = ""
        self.selected_iwad = ""
        self.selected_mod = ""
        self.selected_map = ""
        self.init_ui()
        self.start_scan()

    def styled_button(self, label):
        btn = QPushButton(label)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #1a001a;
                color: #B400FF;
                border: 2px solid #B400FF;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #330033;
            }
        """)
        btn.setMinimumHeight(36)
        return btn

    def init_ui(self):
        font = QFont("Courier", 12)
        self.setFont(font)
        lbl_font = QFont("Courier", 11, QFont.Bold)

        # Engine
        self.engine_button = self.styled_button("Select Source Port (.exe)")
        self.engine_button.clicked.connect(self.select_engine)
        self.engine_label = QLabel("No engine selected")
        self.engine_label.setFont(lbl_font)

        # IWAD
        self.iwad_button = self.styled_button("Select Base IWAD (.wad)")
        self.iwad_button.clicked.connect(self.select_iwad)
        self.iwad_label = QLabel("No IWAD selected")
        self.iwad_label.setFont(lbl_font)

        # Mod
        self.mod_button = self.styled_button("Select Mod (.wad/.pk3)")
        self.mod_button.clicked.connect(self.select_mod)
        self.mod_label = QLabel("No mod selected")
        self.mod_label.setFont(lbl_font)

        # Map
        self.map_button = self.styled_button("Select Map (.wad)")
        self.map_button.clicked.connect(self.select_map)
        self.map_label = QLabel("No map selected")
        self.map_label.setFont(lbl_font)

        # Preset list (multi-select) + preview
        self.preset_list = QListWidget()
        self.preset_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.preset_list.itemSelectionChanged.connect(self.on_preset_selection_changed)
        self.preset_root_label = QLabel(f"Preset folder: {self.preset_root}")
        self.preset_root_label.setFont(QFont("Courier", 10))
        self.preset_preview = QTextEdit()
        self.preset_preview.setReadOnly(True)
        self.preset_preview.setStyleSheet("background-color: #070007; color: #B400FF; font-family: Courier; font-size: 11pt;")
        self.preset_preview.setFixedHeight(240)

        self.save_preset_button = self.styled_button("Save Preset")
        self.save_preset_button.clicked.connect(self.save_preset)
        self.load_preset_button = self.styled_button("Load Selected")
        self.load_preset_button.clicked.connect(self.load_selected_presets)
        self.delete_preset_button = self.styled_button("Delete Selected")
        self.delete_preset_button.clicked.connect(self.delete_selected_presets)
        self.refresh_presets_button = self.styled_button("Refresh Presets")
        self.refresh_presets_button.clicked.connect(self.start_scan)
        self.set_preset_dir_button = self.styled_button("Set Preset Folder")
        self.set_preset_dir_button.clicked.connect(self.set_preset_folder)

        # Launch and credits
        self.launch_button = self.styled_button("LAUNCH")
        self.launch_button.clicked.connect(self.launch_game)
        self.credits_button = self.styled_button("Credits")
        self.credits_button.clicked.connect(self.show_credits)

        # Layout assembly
        layout = QVBoxLayout()

        engine_group = QGroupBox("Source Port")
        engine_layout = QVBoxLayout()
        engine_layout.addWidget(self.engine_button)
        engine_layout.addWidget(self.engine_label)
        engine_group.setLayout(engine_layout)

        iwad_group = QGroupBox("Base IWAD")
        iwad_layout = QVBoxLayout()
        iwad_layout.addWidget(self.iwad_button)
        iwad_layout.addWidget(self.iwad_label)
        iwad_group.setLayout(iwad_layout)

        file_group = QGroupBox("Mod + Map")
        file_layout = QVBoxLayout()
        file_layout.addWidget(self.mod_button)
        file_layout.addWidget(self.mod_label)
        file_layout.addWidget(self.map_button)
        file_layout.addWidget(self.map_label)
        file_group.setLayout(file_layout)

        preset_group = QGroupBox("Presets (multi-select)")
        preset_layout = QVBoxLayout()
        preset_layout.addWidget(self.preset_root_label)
        preset_layout.addWidget(self.preset_list)
        preset_layout.addWidget(self.preset_preview)
        row1 = QHBoxLayout()
        row1.addWidget(self.save_preset_button)
        row1.addWidget(self.load_preset_button)
        row1.addWidget(self.delete_preset_button)
        row2 = QHBoxLayout()
        row2.addWidget(self.refresh_presets_button)
        row2.addWidget(self.set_preset_dir_button)
        preset_layout.addLayout(row1)
        preset_layout.addLayout(row2)
        preset_group.setLayout(preset_layout)

        top_row = QHBoxLayout()
        left_col = QVBoxLayout()
        left_col.addWidget(engine_group)
        left_col.addWidget(iwad_group)
        right_col = QVBoxLayout()
        right_col.addWidget(file_group)
        right_col.addWidget(preset_group)
        top_row.addLayout(left_col, 1)
        top_row.addLayout(right_col, 2)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(self.launch_button)
        button_row.addWidget(self.credits_button)

        layout.addLayout(top_row)
        layout.addLayout(button_row)
        self.setLayout(layout)

    # Scanning logic (background)
    def start_scan(self):
        if self.scanner and self.scanner.isRunning():
            self.scanner.stop()
            self.scanner.wait(200)
        self.preset_list.clear()
        self.preset_preview.setPlainText("Scanning for presets...")
        self.scanner = PresetScanner(self.preset_root)
        self.scanner.scanned.connect(self.on_scan_complete)
        self.scanner.start()

    def on_scan_complete(self, files):
        self.preset_list.blockSignals(True)
        self.preset_list.clear()
        for p in files:
            item = QListWidgetItem(os.path.relpath(p, self.preset_root))
            item.setData(Qt.UserRole, p)
            self.preset_list.addItem(item)
        self.preset_list.blockSignals(False)
        if self.preset_list.count() > 0:
            self.preset_list.setCurrentRow(0)
            self.on_preset_selection_changed()
        else:
            self.preset_preview.clear()

    # Drag and drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        dropped = [u.toLocalFile() for u in event.mimeData().urls()]
        for path in dropped:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".exe":
                self.selected_engine = path
                self.engine_label.setText(os.path.basename(path))
        for path in dropped:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".pk3":
                self.selected_mod = path
                self.mod_label.setText(os.path.basename(path))
        for path in dropped:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".wad":
                if not self.selected_iwad:
                    self.selected_iwad = path
                    self.iwad_label.setText(os.path.basename(path))
                elif not self.selected_mod:
                    self.selected_mod = path
                    self.mod_label.setText(os.path.basename(path))
                elif not self.selected_map:
                    self.selected_map = path
                    self.map_label.setText(os.path.basename(path))

    # File selectors
    def select_engine(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Source Port", "", "Executable (*.exe)")
        if path:
            self.selected_engine = path
            self.engine_label.setText(os.path.basename(path))

    def select_iwad(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select IWAD", "", "WAD Files (*.wad)")
        if path:
            self.selected_iwad = path
            self.iwad_label.setText(os.path.basename(path))

    def select_mod(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Mod", "", "WAD/PK3 Files (*.wad *.pk3)")
        if path:
            self.selected_mod = path
            self.mod_label.setText(os.path.basename(path))

    def select_map(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Map", "", "WAD Files (*.wad)")
        if path:
            self.selected_map = path
            self.map_label.setText(os.path.basename(path))

    # Launch
    def launch_game(self):
        if not self.selected_engine:
            QMessageBox.warning(self, "Launch Failed", "No source port selected.")
            return
        cmd = [self.selected_engine]
        if self.selected_iwad:
            cmd += ["-iwad", self.selected_iwad]
        if self.selected_mod:
            cmd += ["-file", self.selected_mod]
        if self.selected_map:
            cmd += ["-file", self.selected_map]
        try:
            subprocess.Popen(cmd)
        except Exception as e:
            QMessageBox.critical(self, "Launch Failed", str(e))

    # Credits
    def show_credits(self):
        credits = QDialog(self)
        credits.setWindowTitle("Credits")
        credits.setFixedSize(520, 320)
        credits.setStyleSheet("background-color: black; color: #B400FF;")
        text = QTextEdit(credits)
        text.setReadOnly(True)
        text.setStyleSheet("background-color: black; color: #B400FF; font-family: Courier; font-size: 11pt;")
        text.setText(f"""
---- CREATORS ----
Qwerty0975
CoderPenguin1-dev
---- TESTERS ----
CoderPenguin1-dev

---- INSPIRATIONS ----
Minty Launcher CoderPenguin1-dev
GZDoom Launcher

Purple Launcher — {PATCH_INFO['version']}
""")
        text.resize(500, 300)
        credits.exec_()

    # Preset IO and preview
    def save_preset(self):
        start_dir = self.preset_root
        name, _ = QFileDialog.getSaveFileName(self, "Save Preset As", start_dir + os.sep, "Preset Files (*.preset)")
        if not name:
            return
        if not name.lower().endswith(".preset"):
            name += ".preset"
        try:
            header = [
                "# Purple Launcher preset",
                f"# Created: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')}",
                f"# VERSION: {PATCH_INFO['version']}",
                "[PRESET]"
            ]
            with open(name, "w", encoding="utf-8") as f:
                f.write("\n".join(header) + "\n")
                f.write(f"name={os.path.splitext(os.path.basename(name))[0]}\n")
                f.write(f"engine={self.selected_engine or ''}\n")
                f.write(f"iwad={self.selected_iwad or ''}\n")
                f.write(f"mod={self.selected_mod or ''}\n")
                f.write(f"map={self.selected_map or ''}\n")
            self.start_scan()
            QMessageBox.information(self, "Preset Saved", f"Preset saved: {os.path.basename(name)}")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))

    def on_preset_selection_changed(self):
        items = self.preset_list.selectedItems()
        if not items:
            self.preset_preview.clear()
            return
        previews = []
        for item in items:
            path = item.data(Qt.UserRole)
            if not path or not os.path.isfile(path):
                previews.append(f"Missing: {item.text()}")
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                header = f"--- {os.path.relpath(path, self.preset_root)} ---"
                previews.append(header + "\n" + content)
            except Exception as e:
                previews.append(f"Failed to read {item.text()}: {e}")
        self.preset_preview.setPlainText("\n\n".join(previews))

    def load_selected_presets(self):
        items = self.preset_list.selectedItems()
        if not items:
            QMessageBox.warning(self, "Load Failed", "No presets selected.")
            return
        engine = iwad = mod = mapf = ""
        for item in items:
            path = item.data(Qt.UserRole)
            if not path or not os.path.isfile(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        if "=" in line and not line.strip().startswith("#"):
                            key, value = line.strip().split("=", 1)
                            if key == "engine" and not engine:
                                engine = value
                            elif key == "iwad" and not iwad:
                                iwad = value
                            elif key == "mod" and not mod:
                                mod = value
                            elif key == "map" and not mapf:
                                mapf = value
            except Exception:
                continue
        self.selected_engine = engine
        self.selected_iwad = iwad
        self.selected_mod = mod
        self.selected_map = mapf
        self.engine_label.setText(os.path.basename(engine) if engine else "No engine selected")
        self.iwad_label.setText(os.path.basename(iwad) if iwad else "No IWAD selected")
        self.mod_label.setText(os.path.basename(mod) if mod else "No mod selected")
        self.map_label.setText(os.path.basename(mapf) if mapf else "No map selected")
        QMessageBox.information(self, "Presets Loaded", f"Loaded {len(items)} preset(s).")

    def delete_selected_presets(self):
        items = self.preset_list.selectedItems()
        if not items:
            QMessageBox.warning(self, "Delete Failed", "No presets selected.")
            return
        failed = []
        deleted = 0
        for item in items:
            path = item.data(Qt.UserRole)
            if not path or not os.path.isfile(path):
                failed.append(item.text())
                continue
            try:
                os.remove(path)
                deleted += 1
            except Exception:
                failed.append(item.text())
        self.start_scan()
        msg = f"Deleted {deleted} preset(s)."
        if failed:
            msg += " Failed: " + ", ".join(failed)
        QMessageBox.information(self, "Delete Presets", msg)

    def set_preset_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Preset Folder", self.preset_root)
        if folder:
            self.preset_root = os.path.abspath(folder)
            self.preset_root_label.setText(f"Preset folder: {self.preset_root}")
            self.start_scan()

    def closeEvent(self, event):
        if self.scanner and self.scanner.isRunning():
            self.scanner.stop()
            self.scanner.wait(200)
        return super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = PurpleLauncher()
    launcher.show()
    sys.exit(app.exec_())
