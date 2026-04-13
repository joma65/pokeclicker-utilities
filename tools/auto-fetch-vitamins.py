import csv
import json
import time
import os
import re
from enum import IntEnum
from pathlib import Path

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class Region(IntEnum):
    Kanto = 0
    Johto = 1
    Hoenn = 2
    Sinnoh = 3
    Unova = 4
    Kalos = 5
    Alola = 6
    Galar = 7

data_dir = Path(__file__).parent / 'data'
data_dir.mkdir(exist_ok=True)

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

def fetch_data():
    print("Starting browser to fetch new data...")
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    prefs = {
        "download.default_directory": str(data_dir.resolve()),
        "download.prompt_for_download": False,
        "profile.default_content_setting_values.automatic_downloads": 1
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get("https://companion.pokeclicker.com/#!VitaminTracker")
        time.sleep(5)

        for region_enum, target_path in input_files.items():
            print(f"Exporting {region_enum.name}...")
            before_files = set(os.listdir(data_dir))
            driver.execute_script(f"VitaminTracker.highestRegion({region_enum.value}).exportData()")

            new_file = None
            for _ in range(10):
                time.sleep(1)
                added = set(os.listdir(data_dir)) - before_files
                csv_added = [f for f in added if f.endswith('.csv')]
                if csv_added:
                    new_file = csv_added[0]
                    break

            if new_file:
                (data_dir / new_file).replace(target_path)
    finally:
        driver.quit()

def update_js_file(regions_dict):
    js_file_path = Path(__file__).parent / 'optimal-vitamins.user.js'
    if not js_file_path.exists():
        print("optimal-vitamins.user.js not found.")
        return

    # 1. Convert to compact JSON string
    new_data_json = json.dumps(regions_dict, separators=(',', ':'), ensure_ascii=False)

    # 2. Fix the keys: "0": -> 0:
    new_data_json = re.sub(r'\"(\d+)\":', r'\1:', new_data_json)

    # 3. Add line breaks after each region: },1: -> },\n1:
    # This finds the comma between regions and adds a newline
    new_data_json = re.sub(r'(\},)(\d+:)', r'\1\n    \2', new_data_json)

    # 4. Clean up the start and end of the object for better alignment
    new_data_json = new_data_json.replace('{0:', '{\n    0:').replace('}}', '}\n  }')

    # 5. Injection
    js_content = js_file_path.read_text(encoding='utf-8')
    pattern = r'(const vitaminsByRegion = ){.*?}(;)'
    new_js_content = re.sub(pattern, f'\\1{new_data_json}\\2', js_content, flags=re.DOTALL)

    js_file_path.write_text(new_js_content, encoding='utf-8')
    print("JavaScript file updated!")

if __name__ == "__main__":
    # 1. Download every region
    fetch_data()

    # 2. Process the downloaded CSVs
    all_regions_data = {}
    for region_enum, input_file in input_files.items():
        if not input_file.exists():
            continue

        region_data = {}
        with input_file.open('r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                region_data[row['#']] = [
                    int(row['Optimal Protein']),
                    int(row['Optimal Calcium']),
                    int(row['Optimal Carbos'])
                ]

        # Store using the integer value of the Enum
        all_regions_data[int(region_enum.value)] = region_data

        # Also save individual JSONs as your original script did
        output_file = input_file.with_suffix('.json')
        with output_file.open('w', encoding='utf-8') as jsonfile:
            json.dump(region_data, jsonfile, separators=(',', ':'))

    # 3. Update the JS file
    update_js_file(all_regions_data)
