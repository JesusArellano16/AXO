import sys
import subprocess
import importlib.util
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QGridLayout, QFileDialog, QSizePolicy, QComboBox, QLineEdit, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QPainter, QBrush

# --------------------------
# SWITCH DESLIZABLE
# --------------------------
class ToggleSwitch(QWidget):
    toggled = Signal(bool)
    def __init__(self, label: QLabel = None, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 28)
        self._checked = False
        self._hover = False
        self._disabled = False
        self.label = label

    def setDisabled(self, value: bool):
        self._disabled = value
        self.update()

    def enterEvent(self, event):
        if not self._disabled:
            self._hover = True
            self.update()
    def leaveEvent(self, event):
        if not self._disabled:
            self._hover = False
            self.update()
    def mousePressEvent(self, event):
        if not self._disabled:
            self._checked = not self._checked
            self.update_label_style()
            self.toggled.emit(self._checked)
            self.update()
    def isChecked(self):
        return self._checked
    def update_label_style(self):
        if self.label:
            font = self.label.font()
            font.setBold(self._checked)
            self.label.setFont(font)
    def paintEvent(self, event):
        radius = 14
        track_color = QColor("#4cd964") if self._checked else QColor("#bfbfbf")
        if self._hover and not self._disabled and not self._checked:
            track_color = QColor("#a0a0a0")
        if self._disabled:
            track_color = QColor("#d3d3d3")
        knob_x = 32 if self._checked else 4
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(track_color))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, 60, 28, radius, radius)
        p.setBrush(QBrush(Qt.white))
        p.drawEllipse(knob_x, 4, 20, 20)

# --------------------------
# LAUNCHER GUI
# --------------------------
class LauncherGUI(QWidget):
    MAX_ROWS = 8
    MAX_COLS = 5
    MAX_CENTRALES = MAX_ROWS * MAX_COLS

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ejecutor de Reportes")
        self.resize(400, 250)
        self.base_path = None
        self.centrales = []
        self.switches = {}
        self.switches_container = None
        self.current_display_widget = None

        self.layout_main = QVBoxLayout()
        self.setLayout(self.layout_main)

        # Carpeta
        lbl_path = QLabel("Selecciona la carpeta donde están los scripts (DESARROLLO):")
        self.layout_main.addWidget(lbl_path)
        self.lbl_selected_path = QLabel("Ninguna carpeta seleccionada")
        self.lbl_selected_path.setStyleSheet("color: gray;")
        self.layout_main.addWidget(self.lbl_selected_path)
        self.btn_select = QPushButton("Seleccionar carpeta…")
        self.btn_select.setFixedHeight(40)
        self.btn_select.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_select.setStyleSheet(self.select_button_initial_style())
        self.btn_select.clicked.connect(self.select_folder)
        self.layout_main.addWidget(self.btn_select)

        # Dropdown acciones
        self.combo_actions = QComboBox()
        self.combo_actions.setVisible(False)
        self.combo_actions.addItems([
            "Reportes",
            "Add_Central",
            "Remove_Central"
        ])
        self.layout_main.addWidget(self.combo_actions)
        self.combo_actions.currentTextChanged.connect(self.action_selected)

        # Botón ALL (siempre fijo)
        self.lbl_all = QLabel("ALL")
        self.btn_all = ToggleSwitch(label=self.lbl_all)
        self.btn_all.setDisabled(True)
        all_layout = QVBoxLayout()
        all_layout.setAlignment(Qt.AlignHCenter)
        all_layout.addWidget(self.lbl_all)
        all_layout.addWidget(self.btn_all)
        self.layout_main.addLayout(all_layout)
        self.lbl_all.setVisible(False)
        self.btn_all.setVisible(False)
        self.btn_all.toggled.connect(self.toggle_all)

        # Spacer para empujar botones al fondo
        self.layout_main.addStretch()

        # Contenedor único para Clear Day + Ejecutar Reporte
        self.btn_container = QWidget()
        self.h_layout_buttons = QHBoxLayout()
        self.btn_container.setLayout(self.h_layout_buttons)
        self.btn_clear = QPushButton("Clear Day")
        self.btn_clear.setStyleSheet(self.select_button_initial_style())
        self.btn_clear.setFixedHeight(45)
        self.btn_exec = QPushButton("Ejecutar Reporte")
        self.btn_exec.setStyleSheet(self.run_button_style())
        self.btn_exec.setFixedHeight(45)
        self.h_layout_buttons.addWidget(self.btn_clear)
        self.h_layout_buttons.addWidget(self.btn_exec)
        self.btn_container.setVisible(False)
        self.layout_main.addWidget(self.btn_container)

        # Conexiones
        self.btn_clear.clicked.connect(self.ejecutar_clear_day)
        self.btn_exec.clicked.connect(self.run_reports)

    # --------------------------
    # Estilos
    # --------------------------
    def select_button_initial_style(self):
        return """
            QPushButton { background-color: #2979ff; color: white; border-radius: 8px; font-size: 15px; padding:5px; }
            QPushButton:hover { background-color: #1c5ccc; }
            QPushButton:pressed { background-color: #0d3f99; }
        """
    def select_button_after_style(self):
        return """
            QPushButton { background-color: #B0B0B0; color: white; border-radius: 8px; font-size: 15px; padding:5px; }
            QPushButton:hover { background-color: #999797; }
            QPushButton:pressed { background-color: #7f7f7f; }
        """
    def run_button_style(self):
        return self.select_button_initial_style()

    # --------------------------
    # Selección de carpeta
    # --------------------------
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecciona la carpeta DESARROLLO", "", QFileDialog.ShowDirsOnly)
        if folder:
            self.base_path = folder
            self.lbl_selected_path.setText(folder)
            self.lbl_selected_path.setStyleSheet("color: black;")
            self.btn_select.setText("Cambiar carpeta…")
            self.btn_select.setStyleSheet(self.select_button_after_style())
            self.setFixedSize(800, 650)
            self.center_window()
            self.combo_actions.setVisible(True)
            self.combo_actions.setCurrentText("Reportes")
            self.load_centrales()
            self.action_selected("Reportes")

    def center_window(self):
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def load_centrales(self):
        try:
            spec = importlib.util.spec_from_file_location(
                "centrales_bk", f"{self.base_path}/scripts/centrales_bk.py")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.centrales = mod.centrales[:self.MAX_CENTRALES]
        except Exception as e:
            print(e)
            self.centrales = []

    # --------------------------
    # Acción dropdown
    # --------------------------
    def action_selected(self, action_name):
        # Limpiar contenedor dinámico anterior
        if self.current_display_widget:
            self.layout_main.removeWidget(self.current_display_widget)
            self.current_display_widget.deleteLater()
            self.current_display_widget = None
        self.switches.clear()
        if self.switches_container:
            self.switches_container.deleteLater()
            self.switches_container = None

        # Ocultar botones
        self.btn_container.setVisible(False)
        self.lbl_all.setVisible(False)
        self.btn_all.setVisible(False)

        if action_name == "Reportes":
            self.show_switches()
            self.btn_container.setVisible(True)

        elif action_name == "Add_Central":
            container = QWidget()
            v_layout = QVBoxLayout()
            v_layout.setAlignment(Qt.AlignTop)
            lbl_short = QLabel("Short Name:")
            txt_short = QLineEdit()
            lbl_full = QLabel("Full Name:")
            txt_full = QLineEdit()
            btn_add = QPushButton("Agregar Central")
            btn_add.setFixedHeight(40)
            btn_add.setStyleSheet(self.select_button_initial_style())
            v_layout.addWidget(lbl_short)
            v_layout.addWidget(txt_short)
            v_layout.addWidget(lbl_full)
            v_layout.addWidget(txt_full)
            v_layout.addWidget(btn_add)
            container.setLayout(v_layout)
            self.current_display_widget = container
            self.layout_main.insertWidget(4, container)
            btn_add.clicked.connect(lambda: self.agregar_central(txt_short, txt_full))

        elif action_name == "Remove_Central":
            container = QWidget()
            v_layout = QVBoxLayout()
            v_layout.setAlignment(Qt.AlignTop)
            lbl_short = QLabel("Short Name:")
            txt_short = QLineEdit()
            btn_remove = QPushButton("Eliminar Central")
            btn_remove.setFixedHeight(40)
            btn_remove.setStyleSheet(self.select_button_initial_style())
            v_layout.addWidget(lbl_short)
            v_layout.addWidget(txt_short)
            v_layout.addWidget(btn_remove)
            container.setLayout(v_layout)
            self.current_display_widget = container
            self.layout_main.insertWidget(4, container)
            btn_remove.clicked.connect(lambda: self.eliminar_central(txt_short))

    # --------------------------
    # Mostrar switches
    # --------------------------
    def show_switches(self):
        container = QWidget()
        v_layout = QVBoxLayout()
        v_layout.setAlignment(Qt.AlignTop)
        container.setLayout(v_layout)

        self.switches_container = QWidget()
        grid = QGridLayout()
        self.switches_container.setLayout(grid)
        row = col = 0
        for central in self.centrales:
            lbl = QLabel(central.nombre)
            lbl.setAlignment(Qt.AlignHCenter)
            sw = ToggleSwitch(label=lbl)
            sw.toggled.connect(sw.update_label_style)
            grid.addWidget(lbl, row*2, col)
            grid.addWidget(sw, row*2+1, col)
            self.switches[central.nombre] = sw
            col += 1
            if col >= self.MAX_COLS:
                col = 0
                row += 1
                if row >= self.MAX_ROWS: break
        v_layout.addWidget(self.switches_container)

        # Mostrar ALL toggle
        self.lbl_all.setVisible(True)
        self.btn_all.setVisible(True)
        self.btn_all.setDisabled(False)

        self.current_display_widget = container
        self.layout_main.insertWidget(4, container)

    # --------------------------
    # Toggle ALL
    # --------------------------
    def toggle_all(self, state):
        for sw in self.switches.values():
            sw.setDisabled(state)

    # --------------------------
    # Funciones botones
    # --------------------------
    def ejecutar_clear_day(self):
        if self.btn_all.isChecked():
            centrales_names = " ".join([c.nombre for c in self.centrales])
        else:
            centrales_names = " ".join([nombre for nombre, sw in self.switches.items() if sw.isChecked()])
        if not centrales_names: return
        cmd = f'python3 "{self.base_path}/scripts/clear_day.py" {centrales_names}'
        osa_script = f'''tell application "Terminal"
activate
do script "{cmd.replace('"', '\\"')}"
end tell'''
        subprocess.Popen(["osascript", "-e", osa_script])

    def agregar_central(self, txt_short, txt_full):
        shortname = txt_short.text().strip().upper()
        fullname = txt_full.text().strip().upper()
        if not shortname or not fullname: return
        cmd = f'python3 "{self.base_path}/scripts/Add_Central.py" "{shortname}" "{fullname}"'
        osa_script = f'''tell application "Terminal"
activate
do script "{cmd.replace('"', '\\"')}"
end tell'''
        subprocess.Popen(["osascript", "-e", osa_script])
        txt_short.setText("")
        txt_full.setText("")
        QTimer.singleShot(500, self.load_centrales)

    def eliminar_central(self, txt_short):
        shortname = txt_short.text().strip().upper()
        if not shortname: return
        cmd = f'python3 "{self.base_path}/scripts/remove_central.py" "{shortname}"'
        osa_script = f'''tell application "Terminal"
activate
do script "{cmd.replace('"', '\\"')}"
end tell'''
        subprocess.Popen(["osascript", "-e", osa_script])
        txt_short.setText("")
        QTimer.singleShot(500, self.load_centrales)

    # --------------------------
    # Ejecutar reportes
    # --------------------------
    def run_reports(self):
        if not self.base_path: return
        selected_centrales = [c.nombre for c in self.centrales] if self.btn_all.isChecked() \
            else [nombre for nombre, sw in self.switches.items() if sw.isChecked()]
        if not selected_centrales: return
        prefix = f"cd '{self.base_path}'; source reportes3/bin/activate;"
        command = f"{prefix} Reportes {' '.join(selected_centrales)}"
        self.execute_sequential([command])

    def execute_sequential(self, commands):
        full_script = ";".join(commands) + ";"
        osa_script = f'''tell application "Terminal"
activate
do script "{full_script.replace('"', '\\"')}"
end tell'''
        subprocess.Popen(["osascript", "-e", osa_script])

# --------------------------
# MAIN
# --------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LauncherGUI()
    window.show()
    sys.exit(app.exec())
