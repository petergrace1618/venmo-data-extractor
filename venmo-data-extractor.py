from sys import exit
from pathlib import Path
import csv
from datetime import datetime

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
    f = open(fname, encoding='utf-8')
    # ignore first two lines, header is on third
    for l in range(3):
        header = f.readline()
    f.close()
    return header.split(',')


# l contains all fields of transaction
# cc contains the output fields of transaction
# os is output string
def format_line(l: list[str], cc: list[int]) -> str:
    os = ''
    try:
        dt = datetime.fromisoformat(l[cc[0]])
        os = dt.strftime('%b %d %Y')
    except ValueError:
        # first line is header, so return field name
        os = l[cc[0]]

    for c in cc[1:]:
        os += f', {l[c]}'
    os += '\n'
    return os

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

    summary = 'VENMO TRANSACTIONS BETWEEN @PETER-GRACE-16 AND @AMANDA-RUIZ-139\n'
    summary += 'FROM FEBRUARY 2023 TO NOVEMBER 2024\n'
    summary += '\n'
    summary += '(The source code and data of the following report can be found here:\n'
    summary += 'https://github.com/petergrace1618/venmo-data-extractor.git)\n'
    summary += '\n'
    summary += format_line(lines[0], columns)
    summary += '-' * 64 + '\n'

    for line in lines[1:]:
        summary += format_line(line, columns)

    # print(summary)
    # Write summary to file
    with open(output_file, 'w', encoding='utf-8') as o:
        o.write(summary)

    # Append individual csv files by name

