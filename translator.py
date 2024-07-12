import argparse
import csv
from enum import Enum
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QFileDialog, QLabel, QWidget, QComboBox
from PyQt6.QtCore import Qt


class Mode(Enum):
    EB = 1
    FL = 2


class Translator:
    def __init__(self, eem_filename: str, uuvis_filename: str, output_filename: str, mode: Mode):
        self.eem_values = []
        self.uuvis_values = {}
        self.offsets = []
        self.output_data = []
        self.uuvis_filename = uuvis_filename
        self.eem_filename = eem_filename
        self.output_filename = output_filename
        self.mode = mode

    def translate(self):
        if self.mode == Mode.EB:
            self._translate_eb()
        elif self.mode == Mode.FL:
            self._translate_fl()

    def _translate_fl(self):
        pass

    def _translate_eb(self):
        self._parse_eem_file()
        self._parse_uuvis_file()

        self.output_data.append(['lem (nm)', 'lex (nm)', 'IF', 'Aex (–)', 'Aem (–)', 'IFC'])

        detector_index = 1
        for offset in self.offsets:
            self._generate_data_entry(offset, detector_index)
            detector_index += 1

        # write the output data to a csv file, with semicolon separator and comas for floats
        self._write_output_file()

    def _generate_data_entry(self, offset: int, detector_index: int):
        for eem_value in self.eem_values:
            lem_value = int(eem_value[0])
            lex_value = int(offset)
            if_value = float(eem_value[detector_index])
            aex_value = float(self.uuvis_values[offset])
            aem_value = float(self.uuvis_values[eem_value[0]])
            ifc_value = float(if_value * 10 ** ((aex_value + aem_value) * 0.5))
            self.output_data.append([lem_value, lex_value, if_value, aex_value, aem_value, ifc_value])

    def _write_output_file(self):
        output_data_with_commas = []
        for row in self.output_data:
            new_row = [str(value).replace('.', ',') if isinstance(value, float) else value for value in row]
            output_data_with_commas.append(new_row)

        with open(self.output_filename, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerows(output_data_with_commas)

    def _parse_eem_file(self):
        with open(self.eem_filename, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                if line_number <= 24:
                    tokens = line.strip().split(',')
                    print(f"Metadata line {line_number}: {line.strip()}")
                    if tokens[0] == 'Fixed/Offset':
                        self.offsets = [int(float(token)) if token.strip() else 0 for token in tokens[1:]]

                else:
                    tokens = line.strip().split(',')
                    self.eem_values.append([float(token) if token.strip() else 0 for token in tokens])
        self.offsets = [offset for offset in self.offsets if offset != 0]

    def _parse_uuvis_file(self):
        with open(self.uuvis_filename, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                if line_number <= 47:
                    continue
                else:
                    tokens = line.strip().split(',')
                    self.uuvis_values[int(float(tokens[0]))] = float(tokens[1])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--eem")
    parser.add_argument("--uvvis")
    parser.add_argument("--output")
    parser.add_argument("--mode", choices=[mode.name for mode in Mode])
    args = parser.parse_args()

    translator = Translator(args.eem, args.uvvis, args.output, Mode[args.mode])
    translator.translate()


#if __name__ == "__main__":
    # add a simple pyqt6 gui to select the files

 #   main()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Selector")

        self.layout = QVBoxLayout()

        self.eem_line_edit = QLineEdit()
        self.uvvis_line_edit = QLineEdit()
        self.output_line_edit = QLineEdit()

        self.mode_combo_box = QComboBox()
        self.mode_combo_box.addItems([mode.name for mode in Mode])

        self.layout.addWidget(QLabel("EEM File"))
        self.layout.addWidget(self.eem_line_edit)
        self.layout.addWidget(QPushButton("Browse", clicked=self.browse_eem))

        self.layout.addWidget(QLabel("UVVIS File"))
        self.layout.addWidget(self.uvvis_line_edit)
        self.layout.addWidget(QPushButton("Browse", clicked=self.browse_uvvis))

        self.layout.addWidget(QLabel("Output File"))
        self.layout.addWidget(self.output_line_edit)
        self.layout.addWidget(QPushButton("Browse", clicked=self.browse_output))

        self.layout.addWidget(QLabel("Mode"))
        self.layout.addWidget(self.mode_combo_box)

        self.layout.addWidget(QPushButton("Start", clicked=self.start))

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def browse_eem(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select EEM file")
        if file:
            self.eem_line_edit.setText(file)

    def browse_uvvis(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select UVVIS file")
        if file:
            self.uvvis_line_edit.setText(file)

    def browse_output(self):
        file, _ = QFileDialog.getSaveFileName(self, "Select output file")
        if file:
            self.output_line_edit.setText(file)

    def start(self):
        eem_filename = self.eem_line_edit.text()
        uvvis_filename = self.uvvis_line_edit.text()
        output_filename = self.output_line_edit.text()
        mode = Mode[self.mode_combo_box.currentText()]

        translator = Translator(eem_filename, uvvis_filename, output_filename, mode)
        translator.translate()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()