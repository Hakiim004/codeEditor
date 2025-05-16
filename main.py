import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPlainTextEdit, QVBoxLayout, QSplitter,
    QPushButton, QToolBar, QLabel, QFileDialog, QTabWidget, QInputDialog
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QProcess, QEvent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Éditeur avec Terminal et Exécution")
        self.resize(1000, 700)

        # ---- Barre de menus ----
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet('''
            QMenuBar { background: #e9e9e9; color: #222; font-weight: bold; font-size: 15px; }
            QMenuBar::item { background: #e9e9e9; color: #222; padding: 6px 18px; border-radius: 6px; }
            QMenuBar::item:selected { background: #1976d2; color: #fff; }
            QMenu { background: #fff; color: #222; border: 1px solid #b0b0b0; }
            QMenu::item:selected { background: #1976d2; color: #fff; }
        ''')
        fichier_menu = menu_bar.addMenu("Fichier")
        executer_action = QAction("Exécuter", self)
        executer_action.triggered.connect(self.run_code)
        fichier_menu.addAction(executer_action)

        # ---- Actions de gestion de fichiers ----
        nouveau_action = QAction("Nouveau", self)
        nouveau_action.setShortcut("Ctrl+N")
        nouveau_action.triggered.connect(self.nouveau_fichier)
        fichier_menu.addAction(nouveau_action)

        ouvrir_action = QAction("Ouvrir...", self)
        ouvrir_action.setShortcut("Ctrl+O")
        ouvrir_action.triggered.connect(self.ouvrir_fichier)
        fichier_menu.addAction(ouvrir_action)

        enregistrer_action = QAction("Enregistrer", self)
        enregistrer_action.setShortcut("Ctrl+S")
        enregistrer_action.triggered.connect(self.enregistrer_fichier)
        fichier_menu.addAction(enregistrer_action)

        enregistrer_sous_action = QAction("Enregistrer sous...", self)
        enregistrer_sous_action.triggered.connect(self.enregistrer_fichier_sous)
        fichier_menu.addAction(enregistrer_sous_action)

        # ---- Menu Affichage pour le thème ----
        affichage_menu = menu_bar.addMenu("Affichage")
        self.theme_mode = "clair"
        self.theme_action = QAction("Basculer le thème (Clair/Sombre)", self)
        self.theme_action.setShortcut("Ctrl+T")
        self.theme_action.triggered.connect(self.toggle_theme)
        affichage_menu.addAction(self.theme_action)

        self.current_file = None

        # ---- Barre d'outils ----
        toolbar = QToolBar("Barre d'outils")
        self.addToolBar(toolbar)
        run_button = QPushButton("▶ Exécuter")
        run_button.clicked.connect(self.run_code)
        toolbar.addWidget(run_button)

        # ---- Widget central avec onglets et terminal redimensionnable ----
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.fermer_onglet)
        self.tabs.tabBarDoubleClicked.connect(self.renommer_onglet)
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.tabs)
        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setPlaceholderText("Terminal système (lecture seule)")
        terminal_font = self.terminal.font()
        terminal_font.setFamily("Consolas")
        terminal_font.setPointSize(12)
        self.terminal.setFont(terminal_font)
        self.terminal.setStyleSheet("background-color: #181818; color: #e0e0e0; border: none;")
        splitter.addWidget(self.terminal)
        splitter.setSizes([500, 200])
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(splitter)
        self.setCentralWidget(container)

        # ---- Barre d'état pour le comptage des lignes ----
        self.status = self.statusBar()
        self.line_count_label = QLabel("Lignes : 0")
        self.status.addPermanentWidget(self.line_count_label)
        self.cursor_line_label = QLabel("Ligne curseur : 1")
        self.status.addPermanentWidget(self.cursor_line_label)

        self.nouveau_fichier()  # Ouvre un premier onglet par défaut

        self.update_line_count()
        self.update_cursor_line()

        # ---- Processus Python ----
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_error)

        # ---- Thème moderne ----
        self.set_theme("clair")

        # ---- Message d'accueil ----
        self.status.showMessage("Bienvenue dans l'éditeur Python ! Ctrl+N : nouvel onglet, Ctrl+S : sauvegarder, Ctrl+O : ouvrir", 6000)

    def run_code(self):
        current_editor = self.tabs.currentWidget()
        if isinstance(current_editor, QPlainTextEdit):
            code = current_editor.toPlainText()

            # Écrit le code dans un fichier temporaire
            with open("temp_code.py", "w", encoding="utf-8") as f:
                f.write(code)

            # Vide le terminal
            self.terminal.clear()

            # Lance le processus
            self.process.start("python", ["temp_code.py"])

    def read_output(self):
        output = self.process.readAllStandardOutput().data().decode()
        self.terminal.appendPlainText(output)

    def read_error(self):
        error = self.process.readAllStandardError().data().decode()
        self.terminal.appendPlainText(error)

    def update_line_count(self):
        current_editor = self.tabs.currentWidget()
        if isinstance(current_editor, QPlainTextEdit):
            text = current_editor.toPlainText()
            line_count = text.count('\n') + 1 if text else 0
            self.line_count_label.setText(f"Lignes : {line_count}")

    def update_cursor_line(self):
        current_editor = self.tabs.currentWidget()
        if isinstance(current_editor, QPlainTextEdit):
            cursor = current_editor.textCursor()
            line = cursor.blockNumber() + 1
            self.cursor_line_label.setText(f"Ligne curseur : {line}")

    def nouveau_fichier(self):
        editor = QPlainTextEdit()
        editor.setPlaceholderText("Écrivez votre code Python ici...")
        font = editor.font()
        font.setFamily("Consolas")
        font.setPointSize(12)
        editor.setFont(font)
        self.tabs.addTab(editor, f"Fichier {self.tabs.count()+1}")
        self.tabs.setCurrentWidget(editor)

    def renommer_onglet(self, index):
        if index != -1:
            nom, ok = QInputDialog.getText(self, "Renommer l'onglet", "Nouveau nom :", text=self.tabs.tabText(index))
            if ok and nom:
                self.tabs.setTabText(index, nom)

    def fermer_onglet(self, index):
        self.tabs.removeTab(index)

    def ouvrir_fichier(self):
        path, _ = QFileDialog.getOpenFileName(self, "Ouvrir un fichier", "", "Fichiers Python (*.py);;Tous les fichiers (*)")
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                editor = QPlainTextEdit()
                editor.setPlainText(f.read())
                font = editor.font()
                font.setFamily("Consolas")
                font.setPointSize(12)
                editor.setFont(font)
                self.tabs.addTab(editor, path.split('/')[-1] or path.split('\\')[-1])
                self.tabs.setCurrentWidget(editor)
            self.current_file = path
            self.status.showMessage(f"Fichier ouvert : {path}", 2000)

    def enregistrer_fichier(self):
        current_editor = self.tabs.currentWidget()
        if isinstance(current_editor, QPlainTextEdit):
            if self.current_file:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(current_editor.toPlainText())
                self.status.showMessage(f"Fichier enregistré : {self.current_file}", 2000)
            else:
                self.enregistrer_fichier_sous()

    def enregistrer_fichier_sous(self):
        current_editor = self.tabs.currentWidget()
        if isinstance(current_editor, QPlainTextEdit):
            path, _ = QFileDialog.getSaveFileName(self, "Enregistrer sous", "", "Fichiers Python (*.py);;Tous les fichiers (*)")
            if path:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(current_editor.toPlainText())
                self.current_file = path
                self.status.showMessage(f"Fichier enregistré : {path}", 2000)

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_S:
            self.enregistrer_fichier()
        elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_N:
            self.nouveau_fichier()
        else:
            super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        if obj == self.terminal and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                lines = self.terminal.toPlainText().splitlines()
                if lines:
                    cmd = lines[-1].strip()
                    if cmd:
                        self.executer_commande(cmd)
                return True
        return super().eventFilter(obj, event)

    def set_theme(self, mode):
        if mode == "clair":
            self.setStyleSheet('''
                QMainWindow { background: #f7f7f7; }
                QTabWidget::pane { border: 1px solid #b0b0b0; }
                QTabBar::tab { background: #e9e9e9; color: #222; padding: 8px 16px; border-radius: 4px; margin: 2px; }
                QTabBar::tab:selected { background: #1976d2; color: #fff; }
                QToolBar { background: #f7f7f7; border: none; }
                QPushButton { background: #1976d2; color: #fff; border-radius: 4px; padding: 4px 12px; }
                QPushButton:hover { background: #125ea2; }
                QStatusBar { background: #f7f7f7; color: #222; }
                QPlainTextEdit { background: #fff; color: #222; selection-background-color: #cce2ff; }
            ''')
            self.terminal.setStyleSheet("background-color: #f4f4f4; color: #222; border: none;")
        else:
            self.setStyleSheet('''
                QMainWindow { background: #23272e; }
                QTabWidget::pane { border: 1px solid #444; }
                QTabBar::tab { background: #2d323b; color: #e0e0e0; padding: 8px 16px; border-radius: 4px; margin: 2px; }
                QTabBar::tab:selected { background: #007acc; color: #fff; }
                QToolBar { background: #23272e; border: none; }
                QPushButton { background: #007acc; color: #fff; border-radius: 4px; padding: 4px 12px; }
                QPushButton:hover { background: #005fa3; }
                QStatusBar { background: #23272e; color: #e0e0e0; }
                QPlainTextEdit { background: #181818; color: #e0e0e0; selection-background-color: #2d323b; }
            ''')
            self.terminal.setStyleSheet("background-color: #181818; color: #e0e0e0; border: none;")
        self.theme_mode = mode

    def toggle_theme(self):
        if self.theme_mode == "clair":
            self.set_theme("sombre")
        else:
            self.set_theme("clair")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
