import os
import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5 import QtCore
from detect import FileDetectionModule
from backup import BackupModule

import ctypes
myappid = 'skybackup' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class MainView(QWidget):

    checkbox_state = {"save" : 0, "mo_local" : 0, "steam" : 0, "mo": 0}
    labels = {
        "save" : "Saves" ,
        "mo_local" : "Mod Organizer Local Cache" ,
        "steam" : "Steam Installation",
        "mo" : "Mod Organizer Directory"
    }
    output_dir = "./output/"
  
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Skybackup")
        self.file_detector = FileDetectionModule()
    
        self.progress_bar = QProgressBar(self)
        progress_bar = self.progress_bar
        
        self.layout = QVBoxLayout()

        self.paths = self.file_detector.find_all()
        
        for key in self.paths.keys():
            current_layout = self.render_path_display(key)
            self.layout.addLayout(current_layout)

        self.status_label = QLabel()
        self.layout.addWidget(self.status_label)
        self.status_label.hide()

        # Progress Bar
        progress_bar.setValue(0)
        self.layout.addWidget(progress_bar)
        progress_bar.hide()

        self.backup_button = QPushButton("Backup")
        self.backup_button.clicked.connect(lambda i : self.run_backup(progress_bar))
        self.layout.addWidget(self.backup_button) 


        self.setLayout(self.layout)
    
    def render_path_display(self, key):
        path_layout = QHBoxLayout()

        checkbox = QCheckBox()
        checkbox.stateChanged.connect(lambda i: self.handle_checkbox(i, key))
        path_layout.addWidget(checkbox)

        path_text_input = QLineEdit(self.paths[key])
        path_text_input.setPlaceholderText(self.labels[key])
        path_text_input.textChanged.connect(lambda i : self.update_path(i, key))
        path_layout.addWidget(path_text_input)

        path_select_button = QPushButton("...")
        path_layout.addWidget(path_select_button)
        path_select_button.clicked.connect(lambda i : self.select_file(path_text_input))

        return path_layout 
    
    def select_file(self, lineEdit):
        new_path = QFileDialog().getExistingDirectory()
        if new_path != "":
            lineEdit.setText(new_path)
    
    def update_path(self, new_path, key):
        self.paths[key] = new_path
    
    def init_button(self, label, onClick):
        new_button = QPushButton(label) 
        new_button.clicked.connect(lambda response: onClick())
        return new_button
    
    def handle_checkbox(self, i, label):
        if i == 0:
            self.checkbox_state[label] = 0
        else:
            self.checkbox_state[label] = 1
    
    @QtCore.pyqtSlot(int, str)
    def on_progress(self, status, filename):
        self.progress_bar.setValue(status)
        self.status_label.setText(filename)
    
    @QtCore.pyqtSlot()
    def on_worker_done(self):
        self.backup_button.setEnabled(True)
        self.threads[0].quit()
    
    def run_backup(self, progress_bar : QProgressBar):
        progress_bar.setValue(0)
        progress_bar.show()
        self.status_label.show()

        self.backup_button.setEnabled(False)
        print("backing up files...")

        backup_module = BackupModule(self.output_dir, self.paths, self.checkbox_state)

        new_thread = QtCore.QThread()
        self.threads = ([new_thread, backup_module])
        backup_module.moveToThread(new_thread)
        
        backup_module.sig_done.connect(self.on_worker_done)
        backup_module.sig_progress.connect(self.on_progress)

        new_thread.started.connect(backup_module.backup)
        new_thread.start()


if __name__ == "__main__":
    app = QApplication([])
    window = MainView()
    window.setWindowIcon(QtGui.QIcon('../nordic_ruin.png'))

    window.setMinimumWidth(500)
    window.show()
    sys.exit(app.exec_()) 

