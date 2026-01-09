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


def get_fieldnames(fname) -> list[str]:
    # ignore first two lines, header is on third
    with open(fname, encoding='utf-8') as f:
        f.readline()
        f.readline()
        header = f.readline()
    header = header.split(',')
    # change 'Amount (total)' to 'Amount' for formating purposes
    header[8] = 'Amount'
    return header


def format_line(fields: list[str], output_columns: list[int]) -> str:
    global balance
    output_line = ''

    try:
        dt = datetime.fromisoformat(fields[output_columns[0]])
        output_line = dt.strftime('%b %d %Y')
    except ValueError:
        # first line is header, so return field name
        output_line = f'{fields[output_columns[0]]:11}'

    for column in output_columns[1:]:
        output_line += f' | {fields[column]:11}'

    if re.search('rent', fields[output_columns[-1]], re.IGNORECASE):
        rent_mark = '* '
    else:
        rent_mark = '  '
        balance += get_transaction_amount(fields)

    output_line = rent_mark + output_line + '\n'
    return output_line


# return float value of amount field
def get_transaction_amount(fields: list[str]) -> float:
    amount_column_index = 8
    try:
        amount_field = fields[amount_column_index]
        # amount_field ~ /[+-] \$\d+\.\d\d/ e.g. '+ $65.00'
        amount = float(amount_field[3:])
        sign = {'+': 1, '-': -1}[amount_field[0]]
        amount *= sign
    except ValueError:
        amount = 0.0
    return amount


if __name__ == '__main__':
    csv_files_dir = Path('./csv')
    csv_files = list(csv_files_dir.glob('VenmoStatement*.csv'))
    output_file = 'Venmo_transactions.txt'
    name = 'Amanda Ruiz'
    # holds the balances of non-rent transactions
    balance = 0.0
    hr = '-' * 80 + '\n'

    if len(csv_files) == 0:
        print('No .csv files in', csv_files_dir)
        exit(1)

    # Field names:
    # ,ID,Datetime,Type,Status,Note,From,To,Amount (total),Amount (tip),
    # Amount (tax),Amount (fee),Tax Rate,Tax Exempt,Funding Source,
    # Destination,Beginning Balance,Ending Balance,Statement Period Venmo Fees,
    # Terminal Location,Year to Date Venmo Fees,Disclaimer
    fieldnames = get_fieldnames(csv_files[0])

    # transactions: list[list[str]]
    # first row of transactions is header
    # the rest will be transactions between G and I
    transactions = [fieldnames]
    for csv_file in csv_files:
        with open(csv_file, newline='', encoding='utf-8') as f:
            csv_reader = csv.reader(f, dialect=VenmoDialect)
            for transaction in csv_reader:
                if name in transaction:
                    transactions.append(transaction)


    # Get indices of output fields: [2, 6, 7, 8, 5]
    output_fields = ['Datetime', "From", 'To', 'Amount', 'Note']
    columns = [fieldnames.index(field) for field in output_fields]
    output_header = format_line(transactions[0], columns)

    doc = 'VENMO TRANSACTIONS BETWEEN @PETER-GRACE-16 AND @AMANDA-RUIZ-139\n'
    doc += 'FROM FEBRUARY 2023 TO NOVEMBER 2024\n'
    doc += '\n'
    doc += '(For source code and data see:\n'
    doc += 'https://github.com/petergrace1618/venmo-data-extractor.git)\n'
    doc += '\n'
    doc += output_header
    doc += hr

    for transaction in transactions[1:]:
        doc += format_line(transaction, columns)

    doc += hr
    doc += f"Balance of non-rent transactions....${str(balance)}\n"

    with open(output_file, 'w', encoding='utf-8') as o:
        o.write(doc)

