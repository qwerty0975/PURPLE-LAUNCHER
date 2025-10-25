import sys, subprocess, os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QTextEdit, QDialog, QGroupBox
)
from PyQt5.QtGui import QFont

# ---------------- PATCH INFO ----------------
PATCH_INFO = {
    "version": "PATCH 1",
    "notes": [
        "PATCH 1"
    ]
}
# --------------------------------------------

class PurpleLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Purple Launcher — {PATCH_INFO['version']}")
        self.setFixedSize(560, 420)
        self.setStyleSheet("background-color: black; color: #B400FF;")
        self.selected_engine = ""
        self.selected_iwad = ""
        self.selected_mod = ""
        self.selected_map = ""
        self.init_ui()

    def styled_button(self, label):
        btn = QPushButton(label)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #1a001a;
                color: #B400FF;
                border: 2px solid #B400FF;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #330033;
            }
        """)
        return btn

    def init_ui(self):
        font = QFont("Courier", 10)
        self.setFont(font)

        # Source Port
        self.engine_button = self.styled_button("Select Source Port (.exe)")
        self.engine_button.clicked.connect(self.select_engine)
        self.engine_label = QLabel("No engine selected")

        # IWAD
        self.iwad_button = self.styled_button("Select Base IWAD")
        self.iwad_button.clicked.connect(self.select_iwad)
        self.iwad_label = QLabel("No IWAD selected")

        # Mod
        self.mod_button = self.styled_button("Select Mod")
        self.mod_button.clicked.connect(self.select_mod)
        self.mod_label = QLabel("No mod selected")

        # Map
        self.map_button = self.styled_button("Select Map")
        self.map_button.clicked.connect(self.select_map)
        self.map_label = QLabel("No map selected")

        # Launch and Credits
        self.launch_button = self.styled_button("LAUNCH")
        self.launch_button.clicked.connect(self.launch_game)

        self.credits_button = self.styled_button("Credits")
        self.credits_button.clicked.connect(self.show_credits)

        # Layout
        layout = QVBoxLayout()

        # Group: Engine
        engine_group = QGroupBox("Source Port")
        engine_layout = QVBoxLayout()
        engine_layout.addWidget(self.engine_button)
        engine_layout.addWidget(self.engine_label)
        engine_group.setLayout(engine_layout)

        # Group: IWAD
        iwad_group = QGroupBox("Base IWAD")
        iwad_layout = QVBoxLayout()
        iwad_layout.addWidget(self.iwad_button)
        iwad_layout.addWidget(self.iwad_label)
        iwad_group.setLayout(iwad_layout)

        # Group: Mod + Map
        file_group = QGroupBox("Mod + Map")
        file_layout = QVBoxLayout()
        file_layout.addWidget(self.mod_button)
        file_layout.addWidget(self.mod_label)
        file_layout.addWidget(self.map_button)
        file_layout.addWidget(self.map_label)
        file_group.setLayout(file_layout)

        # Buttons
        button_row = QHBoxLayout()
        button_row.addWidget(self.launch_button)
        button_row.addWidget(self.credits_button)

        # Assemble
        layout.addWidget(engine_group)
        layout.addWidget(iwad_group)
        layout.addWidget(file_group)
        layout.addLayout(button_row)
        self.setLayout(layout)

    def select_engine(self):
        self.selected_engine, _ = QFileDialog.getOpenFileName(self, "Select Source Port", "", "Executable (*.exe)")
        self.engine_label.setText(os.path.basename(self.selected_engine) if self.selected_engine else "No engine selected")

    def select_iwad(self):
        self.selected_iwad, _ = QFileDialog.getOpenFileName(self, "Select IWAD", "", "WAD Files (*.wad)")
        self.iwad_label.setText(os.path.basename(self.selected_iwad) if self.selected_iwad else "No IWAD selected")

    def select_mod(self):
        self.selected_mod, _ = QFileDialog.getOpenFileName(self, "Select Mod", "", "WAD/PK3 Files (*.wad *.pk3)")
        self.mod_label.setText(os.path.basename(self.selected_mod) if self.selected_mod else "No mod selected")

    def select_map(self):
        self.selected_map, _ = QFileDialog.getOpenFileName(self, "Select Map", "", "WAD Files (*.wad)")
        self.map_label.setText(os.path.basename(self.selected_map) if self.selected_map else "No map selected")

    def launch_game(self):
        if not self.selected_engine:
            print("No source port selected.")
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
            print("Launch failed:", e)

    def show_credits(self):
        credits = QDialog(self)
        credits.setWindowTitle("Credits")
        credits.setFixedSize(400, 250)
        credits.setStyleSheet("background-color: black; color: #B400FF;")

        text = QTextEdit(credits)
        text.setReadOnly(True)
        text.setStyleSheet("background-color: black; color: #B400FF; font-family: Courier; font-size: 10pt;")
        text.setText(f"""
---- CREATORS ----
Qwerty09

---- TESTERS ----
(I have none yet)

---- INSPIRATIONS ----
Minty Launcher (made by Coder Penguin)
GZDoom Launcher

Purple Launcher — {PATCH_INFO['version']}
""")
        text.resize(380, 230)
        credits.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = PurpleLauncher()
    launcher.show()
    sys.exit(app.exec_())