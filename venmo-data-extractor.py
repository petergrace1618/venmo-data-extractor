from pathlib import Path

if __name__ == '__main__':
    csv_files = Path('csv').glob('VenmoStatement*.csv')
    for f in csv_files:
        print(f)