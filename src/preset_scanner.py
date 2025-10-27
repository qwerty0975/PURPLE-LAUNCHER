import os
from PyQt5.QtCore import QThread, pyqtSignal

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