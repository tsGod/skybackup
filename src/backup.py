import shutil
import os
import sys
from tabnanny import check
from typing import Dict
import py7zr
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

class BackupModule(QtCore.QObject):

    sig_progress = QtCore.pyqtSignal(int, str)
    sig_done = QtCore.pyqtSignal()

    def __init__(self, output_dir, paths: Dict, checkbox_state: Dict):
        super().__init__()
        self.output_dir = output_dir
        self.total = 0
        self.current = 0
        self.paths = paths
        self.checkbox_state = checkbox_state
    
    @QtCore.pyqtSlot()
    def backup(self):
        if (os.path.isdir(self.output_dir)):
            self.sig_progress.emit(0, "Creating output directory...")
            shutil.rmtree(self.output_dir)

        os.mkdir(self.output_dir)

        for key in self.paths.keys():
            if self.checkbox_state[key] == 1:
                self.backup_directory(self.paths[key], key)
        
        self.zip_dir(self.output_dir)

        self.sig_done.emit()

    def _logpath(self, path, names):
        self.total = len(names)
        # logging.info('Working in %s' % path)
        # print('Working in %s' % path)
        # print("Current: %s" % names)
        return []   # nothing will be ignored
    
    def copy2_verbose(self, src, dst):
        # print('Copying {0}'.format(src))
        self.current = self.current + 1
        self.sig_progress.emit(int((self.current / self.total) * 100), "Copying: " + src)
        shutil.copy2(src,dst)
    
    def backup_directory(self, path, dirname):
        # Reseting progress bar counters
        self.total = 0
        self.current = 0

        try:
            shutil.copytree(path, os.path.join(self.output_dir, dirname),  ignore=self._logpath, copy_function=self.copy2_verbose)
        except:
            print(sys.exc_info())
    
    def zip_dir(self, path):
        with py7zr.SevenZipFile(self.output_dir + "/backup.7z", 'w') as archive:
            self.sig_progress.emit(0, "Zipping output files...")
            for dir in os.listdir(path):
                if (dir != 'backup.7z'):
                    n = len(os.listdir(os.path.join(path, dir)))
                    i = 0
                    for file in os.listdir(os.path.join(path, dir)):
                        self.sig_progress.emit((int(i / n * 100)), "Zipping: " + file)
                        archive.write(os.path.join(path, dir, file), path)
                        i+=1

