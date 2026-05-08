from __future__ import annotations

import json
import sys
from pathlib import Path


def run_gui():
    """
    Optional PyQt GUI entry point for AI Serviter.

    Install optional dependencies manually:
      python -m pip install PyQt5 pandas matplotlib
    """
    try:
        from PyQt5.QtCore import QThread, pyqtSignal
        from PyQt5.QtWidgets import (
            QApplication, QComboBox, QFileDialog, QGroupBox, QHBoxLayout, QLabel,
            QMainWindow, QPushButton, QStatusBar, QTextEdit, QVBoxLayout, QWidget
        )
    except ImportError as exc:
        raise RuntimeError("GUI dependencies missing. Install PyQt5 first.") from exc

    from .serviter import AIServiter

    class Worker(QThread):
        finished = pyqtSignal(dict)
        error = pyqtSignal(str)

        def __init__(self, root: str, action: str, text: str):
            super().__init__()
            self.root = root
            self.action = action
            self.text = text

        def run(self):
            try:
                serviter = AIServiter(self.root)
                if self.action == "analyze":
                    result = serviter.analyze()
                elif self.action == "plan":
                    result = serviter.plan(self.text)
                else:
                    result = serviter.propose(self.text)
                self.finished.emit(result)
            except Exception as exc:
                self.error.emit(str(exc))

    class AIServiterGUI(QMainWindow):
        def __init__(self):
            super().__init__()
            self.root = "."
            self.worker = None
            self.init_ui()

        def init_ui(self):
            self.setWindowTitle("AI Serviter Control Panel")
            self.setGeometry(100, 100, 1100, 700)

            main = QWidget()
            layout = QHBoxLayout(main)

            left = QWidget()
            left_layout = QVBoxLayout(left)

            root_group = QGroupBox("Project")
            root_layout = QVBoxLayout(root_group)
            self.root_label = QLabel(f"Root: {self.root}")
            choose = QPushButton("Choose Project Root")
            choose.clicked.connect(self.choose_root)
            root_layout.addWidget(self.root_label)
            root_layout.addWidget(choose)
            left_layout.addWidget(root_group)

            task_group = QGroupBox("Task")
            task_layout = QVBoxLayout(task_group)
            self.action = QComboBox()
            self.action.addItems(["analyze", "plan", "propose"])
            self.instruction = QTextEdit()
            self.instruction.setPlaceholderText("Enter instruction, task, or order...")
            run = QPushButton("Run")
            run.clicked.connect(self.run_action)
            task_layout.addWidget(QLabel("Action"))
            task_layout.addWidget(self.action)
            task_layout.addWidget(QLabel("Instruction"))
            task_layout.addWidget(self.instruction)
            task_layout.addWidget(run)
            left_layout.addWidget(task_group)

            self.output = QTextEdit()
            self.output.setReadOnly(True)

            layout.addWidget(left, 1)
            layout.addWidget(self.output, 2)
            self.setCentralWidget(main)
            self.status = QStatusBar()
            self.setStatusBar(self.status)

        def choose_root(self):
            folder = QFileDialog.getExistingDirectory(self, "Choose Project Root", self.root)
            if folder:
                self.root = folder
                self.root_label.setText(f"Root: {folder}")

        def run_action(self):
            self.status.showMessage("Running...")
            self.worker = Worker(self.root, self.action.currentText(), self.instruction.toPlainText())
            self.worker.finished.connect(self.done)
            self.worker.error.connect(self.fail)
            self.worker.start()

        def done(self, result):
            self.output.setText(json.dumps(result, indent=2))
            self.status.showMessage("Done", 3000)

        def fail(self, error):
            self.status.showMessage(error, 5000)

    app = QApplication(sys.argv)
    window = AIServiterGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_gui()
