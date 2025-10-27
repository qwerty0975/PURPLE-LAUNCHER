import os
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout,
    QHBoxLayout, QTextEdit, QDialog, QGroupBox, QListWidget,
    QListWidgetItem, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from config import PATCH_INFO, PRESET_GLOB_DIR
from file_utils import classify_file
from preset_io import parse_preset, preview_presets, save_preset as io_save_preset
from preset_scanner import PresetScanner

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

        self.engine_button = self.styled_button("Select Source Port (.exe)")
        self.engine_button.clicked.connect(self.select_engine)
        self.engine_label = QLabel("No engine selected")
        self.engine_label.setFont(lbl_font)

        self.iwad_button = self.styled_button("Select Base IWAD (.wad)")
        self.iwad_button.clicked.connect(self.select_iwad)
        self.iwad_label = QLabel("No IWAD selected")
        self.iwad_label.setFont(lbl_font)

        self.mod_button = self.styled_button("Select Mod (.wad/.pk3)")
        self.mod_button.clicked.connect(self.select_mod)
        self.mod_label = QLabel("No mod selected")
        self.mod_label.setFont(lbl_font)

        self.map_button = self.styled_button("Select Map (.wad/.pk3/.zip)")
        self.map_button.clicked.connect(self.select_map)
        self.map_label = QLabel("No map selected")
        self.map_label.setFont(lbl_font)

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

        self.launch_button = self.styled_button("LAUNCH")
        self.launch_button.clicked.connect(self.launch_game)
        self.credits_button = self.styled_button("Credits")
        self.credits_button.clicked.connect(self.show_credits)

        layout = QVBoxLayout()
        top_row = QHBoxLayout()
        left_col = QVBoxLayout()
        right_col = QVBoxLayout()

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

        left_col.addWidget(engine_group)
        left_col.addWidget(iwad_group)
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

    def on_preset_selection_changed(self):
        items = self.preset_list.selectedItems()
        paths = [item.data(Qt.UserRole) for item in items]
        preview = preview_presets(paths, self.preset_root)
        self.preset_preview.setPlainText(preview)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        dropped = [u.toLocalFile() for u in event.mimeData().urls()]
        for path in dropped:
            file_type = classify_file(path)
            if file_type == "engine":
                self.selected_engine = path
                self.engine_label.setText(os.path.basename(path))
            elif file_type == "mod":
                self.selected_mod = path
                self.mod_label.setText(os.path.basename(path))
            elif file_type in ["wad", "map"]:
                if not self.selected_iwad:
                    self.selected_iwad = path
                    self.iwad_label.setText(os.path.basename(path))
                elif not self.selected_mod:
                    self.selected_mod = path
                    self.mod_label.setText(os.path.basename(path))
                elif not self.selected_map:
                    self.selected_map = path
                    self.map_label.setText(os.path.basename(path))

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
        path, _ = QFileDialog.getOpenFileName(self, "Select Map", "", "Map Files (*.wad *.pk3 *.zip)")
        if path:
            # Put zips/pk3/wad into map slot if map chosen explicitly
            self.selected_map = path
            self.map_label.setText(os.path.basename(path))

    def save_preset(self):
        start_dir = self.preset_root
        name, _ = QFileDialog.getSaveFileName(self, "Save Preset As", start_dir + os.sep, "Preset Files (*.preset)")
        if not name:
            return
        if not name.lower().endswith(".preset"):
            name += ".preset"
        try:
            io_save_preset(name, self.selected_engine, self.selected_iwad, self.selected_mod, self.selected_map)
            self.start_scan()
            QMessageBox.information(self, "Preset Saved", f"Preset saved: {os.path.basename(name)}")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))

    def load_selected_presets(self):
        items = self.preset_list.selectedItems()
        if not items:
            QMessageBox.warning(self, "Load Failed", "No presets selected.")
            return
        combined = {"engine": "", "iwad": "", "mod": "", "map": ""}
        for item in items:
            path = item.data(Qt.UserRole)
            if not path or not os.path.isfile(path):
                continue
            parsed = parse_preset(path)
            for k in combined:
                if not combined[k]:
                    combined[k] = parsed.get(k, "")
        self.selected_engine = combined["engine"]
        self.selected_iwad = combined["iwad"]
        self.selected_mod = combined["mod"]
        self.selected_map = combined["map"]
        self.engine_label.setText(os.path.basename(self.selected_engine) if self.selected_engine else "No engine selected")
        self.iwad_label.setText(os.path.basename(self.selected_iwad) if self.selected_iwad else "No IWAD selected")
        self.mod_label.setText(os.path.basename(self.selected_mod) if self.selected_mod else "No mod selected")
        self.map_label.setText(os.path.basename(self.selected_map) if self.selected_map else "No map selected")
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

    def closeEvent(self, event):
        if self.scanner and self.scanner.isRunning():
            self.scanner.stop()
            self.scanner.wait(200)
        return super().closeEvent(event)