import csv
import json
from enum import IntEnum
from pathlib import Path

class Region(IntEnum):
    Kanto = 0
    Johto = 1
    Hoenn = 2
    Sinnoh = 3
    Unova = 4
    Kalos = 5
    Alola = 6
    Galar = 7

class Vitamin(IntEnum):
    Protein = 0
    Calcium = 1
    Carbos = 2

data_dir = Path(__file__).parent / 'data'
input_files = {
    Region.Kanto: data_dir / '01-kanto.csv',
    Region.Johto: data_dir / '02-johto.csv',
    Region.Hoenn: data_dir / '03-hoenn.csv',
    Region.Sinnoh: data_dir / '04-sinnoh.csv',
    Region.Unova: data_dir / '05-unova.csv',
    Region.Kalos: data_dir / '06-kalos.csv',
    Region.Alola: data_dir / '07-alola.csv',
    Region.Galar: data_dir / '08-galar.csv',
}

regions = {region: {} for region in Region}

for region, input_file in input_files.items():
    with input_file.open('r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            regions[region][row['#']] = [
                int(row['Optimal Protein']),
                int(row['Optimal Calcium']),
                int(row['Optimal Carbos'])
            ]

    output_file = input_file.with_suffix('.json')
    with output_file.open('w', encoding='utf-8') as jsonfile:
        json.dump(regions[region], jsonfile, separators=(',', ':'), ensure_ascii=False)