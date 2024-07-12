#import pandas as pd
import csv

# create a class for the data with parsing functions
class Translator:
    uuvis_filename = '/home/nothrax/Documents/fch/UVVIS_raw.csv'
    eem_filename = '/home/nothrax/Documents/fch/EEM_raw_EB.csv'

    def __init__(self, eem_filename: str, uuvis_filename: str):
        self.eem_values = []
        self.uuvis_values = {}
        self.offsets = []
        self.output_data = []
        self.uuvis_filename = uuvis_filename
        self.eem_filename = eem_filename
        self.output_filename = 'output.csv'

    def translate(self):
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
    uuvis_filename = '/home/nothrax/Documents/fch/UVVIS_raw.csv'
    eem_filename = '/home/nothrax/Documents/fch/EEM_raw_EB.csv'

    translator = Translator(eem_filename, uuvis_filename)
    translator.translate()


if __name__ == "__main__":
    main()
