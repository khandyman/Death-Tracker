import os.path
from tkinter import filedialog


class Load:
    def __init__(self, arg):
        if arg != "":
            self.choose_log()

        self._file_path = self.load_config()

    def set_log(self, path):
        self._file_path = path

    def get_log(self):
        return self._file_path

    def load_config(self):
        if not os.path.isfile("config"):
            self.choose_log()

        return self.read_log()

    def choose_log(self):
        log_file = filedialog.askopenfilename(title="Select Log File", filetypes=[("Log Files", "*pq.proj.txt")])
        self.write_log(log_file)

    def read_log(self):
        with open("config") as file:
            return file.readline()

    def write_log(self, log_file):
        with open("config", 'w') as file:
            file.write(f"{log_file}")
