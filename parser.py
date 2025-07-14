import re
import csv
import requests
from collections import defaultdict

def parse_gold_string(gold_str):
    """Convert '101g 70s 24c' to float gold value"""
    gold = int(re.search(r'(\d+)g', gold_str).group(1)) if 'g' in gold_str else 0
    silver = int(re.search(r'(\d+)s', gold_str).group(1)) if 's' in gold_str else 0
    copper = int(re.search(r'(\d+)c', gold_str).group(1)) if 'c' in gold_str else 0
    return gold + silver / 100 + copper / 10000

def parse_log_from_url(url):
    response = requests.get(url)
    lines = response.text.splitlines()

    player_data = defaultdict(lambda: defaultdict(int))
    player_gold = {}
    current_player = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect player line
        player_match = re.match(r"^(\w+) deaths:\d+", line)
        if player_match:
            current_player = player_match.group(1)
            continue

        # Detect consumable with count (and optional price)
        item_match = re.match(r"^(.+?)\s+(\d+)(?:\s+\(.*\))?$", line)
        if item_match and current_player:
            item = item_match.group(1).strip()
            count = int(item_match.group(2))
            player_data[current_player][item] += count
            continue

        # Detect total spent line
        gold_match = re.match(r"^total spent:\s+(.+)", line)
        if gold_match and current_player:
            gold_str = gold_match.group(1).strip()
            player_gold[current_player] = round(parse_gold_string(gold_str), 2)
            current_player = None

    return player_data, player_gold

def write_csv(player_data, player_gold, output_filename):
    # Gather all unique consumables
    all_items = sorted(set(item for items in player_data.values() for item in items))

    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        header = ["Player"]+ ["Total Gold Used"] + all_items 
        writer.writerow(header)

        for player in sorted(player_data):
            row = [player]
            row.append(player_gold.get(player, 0.0))
            for item in all_items:
                count = player_data[player].get(item, 0)
                row.append(count if isinstance(count, int) and count > 0 else "")
            writer.writerow(row)



def main():
    url = input("Enter the URL to the raw consumables log file: ").strip()
    output_filename = "consumables_summary.csv"

    try:
        player_data, player_gold = parse_log_from_url(url)
        write_csv(player_data, player_gold, output_filename)
        print(f"\nCSV file '{output_filename}' has been created successfully.")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
