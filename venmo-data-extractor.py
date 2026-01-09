from sys import exit
from pathlib import Path
import csv
from datetime import datetime
import re

class VenmoDialect(csv.excel):
    def __init__(self):
        setattr(self, 'delimiter', ',')
        setattr(self, 'quotechar', '"')
        setattr(self, 'doublequote', False)
        setattr(self, 'escapechar', '\\')
        setattr(self, 'lineterminator', r'\r\n')
        setattr(self, 'quoting', csv.QUOTE_ALL)
        setattr(self, 'skipinitialspace', False)
        setattr(self, 'strict', True)


def get_fieldnames(fname):
    # ignore first two lines, header is on third
    with open(fname, encoding='utf-8') as f:
        f.readline()
        f.readline()
        header = f.readline()
    return header.split(',')


def format_line(fields: list[str], output_columns: list[int]) -> str:
    output_line = ''
    try:
        dt = datetime.fromisoformat(fields[output_columns[0]])
        output_line = dt.strftime('%b %d %Y')
    except ValueError:
        # first line is header, so return field name
        output_line = fields[output_columns[0]]

    for column in output_columns[1:]:
        output_line += f', {fields[column]}'

    rent_mark = '* ' if re.search('rent', fields[output_columns[-1]], re.IGNORECASE) else '  '
    output_line = rent_mark + output_line + '\n'
    return output_line


if __name__ == '__main__':
    csv_files_dir = Path('./csv')
    csv_files = list(csv_files_dir.glob('VenmoStatement*.csv'))
    output_file = 'Venmo_transactions.txt'

    if len(csv_files) == 0:
        print('No .csv files in', csv_files_dir)
        exit()

    # Field names:
    # ,ID,Datetime,Type,Status,Note,From,To,Amount (total),Amount (tip),
    # Amount (tax),Amount (fee),Tax Rate,Tax Exempt,Funding Source,
    # Destination,Beginning Balance,Ending Balance,Statement Period Venmo Fees,
    # Terminal Location,Year to Date Venmo Fees,Disclaimer

    # get field names
    fieldnames = get_fieldnames(csv_files[0])

    name = 'Amanda Ruiz'

    # lines is a 2D array of strings that holds all transactions between G and I
    lines = [fieldnames]
    for csv_file in csv_files:
        with open(csv_file, newline='', encoding='utf-8') as f:
            csv_reader = csv.reader(f, dialect=VenmoDialect)
            for line in csv_reader:
                if name in line:
                    lines.append(line)


    # Get indices of output fields
    output_fields = ['Datetime', "From", 'To', 'Amount (total)', 'Note']
    columns = [fieldnames.index(field) for field in output_fields]
    # columns = [2, 6, 7, 8, 5]

    doc = 'VENMO TRANSACTIONS BETWEEN @PETER-GRACE-16 AND @AMANDA-RUIZ-139\n'
    doc += 'FROM FEBRUARY 2023 TO NOVEMBER 2024\n'
    doc += '\n'
    doc += '(For source code and data see:\n'
    doc += 'https://github.com/petergrace1618/venmo-data-extractor.git)\n'
    doc += '\n'
    doc += format_line(lines[0], columns)
    doc += '-' * 64 + '\n'

    for line in lines[1:]:
        doc += format_line(line, columns)

    # print(summary)
    # Write summary to file
    with open(output_file, 'w', encoding='utf-8') as o:
        o.write(doc)

