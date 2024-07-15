# Simple data parsing app for FCH
* App si able to convert EEM and UVVIS files to CSV format in order to evaluate the results. 
* App has two modes, one for EB EEM files and one for FL EEM files.
* FL EEM file is expected in xlsx format, with data starting from second row
* EB EEM file is expected in txt format, with data starting from 25th row with offset values starting with name "Fixed/Offset"
* UUVIS file is expected in xlsx format with data starting at row 48
* output format is semi-colon separated CSV file with comma as decimal separator

## Installation
* python3 -m venv venv
* source venv/bin/activate
* pip install -r requirements.txt
* pyinstaller --onefile translator.py