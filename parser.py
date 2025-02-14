import csv
import re
from collections import defaultdict

def parse_log_file(filename):
    players = defaultdict(lambda: defaultdict(int))
    
    with open(filename, 'r', encoding='utf-8') as file:
        current_player = None
        
        for line in file:
            line = line.strip()
            
            if not line:
                continue
            
            # Match player names
            player_match = re.match(r"^(\w+) deaths:\d+", line)
            if player_match:
                current_player = player_match.group(1)
                continue
            
            # Match items and their usage count
            item_match = re.match(r"^(.+?)\s(\d+)(?:\s+\(.*\))?$", line)
            if item_match and current_player:
                item_name = item_match.group(1).strip()
                item_count = int(item_match.group(2))
                players[current_player][item_name] += item_count
    
    return players

def write_csv(players, output_filename):
    # Get all unique items
    all_items = sorted(set(item for player_items in players.values() for item in player_items))
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header row
        writer.writerow(["Player"] + all_items)
        
        # Write player data
        for player, items in players.items():
            row = [player] + [items.get(item, 0) for item in all_items]
            writer.writerow(row)

def main():
    input_filename = "log.txt"
    output_filename = "output.csv"
    
    players = parse_log_file(input_filename)
    write_csv(players, output_filename)
    print(f"CSV file '{output_filename}' has been created successfully.")

if __name__ == "__main__":
    main()
