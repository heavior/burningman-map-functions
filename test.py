import json
from collections import defaultdict
from python.coordinates import locationObjectToCoordinate

def count_camp_locations(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    location_counts = defaultdict(int)
    location_details = {}
    total_count = len(data)
    
    for item in data:
        if 'location' in item:
            location = item['location']
            coordinates = tuple(locationObjectToCoordinate(location))  # Convert to tuple
            location_counts[coordinates] += 1
            # Only store one camp's details for each unique location
            if coordinates not in location_details:
                location_details[coordinates] = {
                    "string": location.get('string', 'N/A'),
                    "location": location
                }
    
    return location_counts, location_details, total_count

def print_location_counts(location_counts, location_details, total_count):
    unique_locations = 0
    non_unique_locations = 0
    none_none_count = location_counts.get((None, None), 0)
    max_count = 0
    
    sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
    
    for coordinates, count in sorted_locations:
        if count > 1:
            details = location_details[coordinates]
            # print(f"Coord: {coordinates}, \tCount: {count}, \tLoc : {details['string']}")
            if coordinates != (None, None):
                non_unique_locations += count
            if coordinates != (None, None) and count > max_count:
                max_count = count
        elif count == 1:
            unique_locations += 1
    
    total_non_unique_unique = unique_locations + non_unique_locations + none_none_count
    
    print(f"\nSummary of Counts:")
    print(f"Total number of objects in the file: \t\t{total_count}")
    print(f"Number of unique locations: \t\t\t{unique_locations}")
    print(f"Total count for non-unique locations: \t\t{non_unique_locations}")
    print(f"Max count for a single location: \t\t{max_count}")
    print(f"Count for (None, None): \t\t\t{none_none_count}")
    print(f"Sum of None, Unique, and Non-Unique counts: \t{total_non_unique_unique}")

if __name__ == "__main__":
    camp_file_path = 'camp.json'
    location_counts, location_details, total_count = count_camp_locations(camp_file_path)
    
    print_location_counts(location_counts, location_details, total_count)



def count_items(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return len(data)

def main():
    event_file_path = 'event.json'
    art_file_path = 'art.json'
    camp_file_path = 'camp.json'
    
    event_count = count_items(event_file_path)
    art_count = count_items(art_file_path)
    camp_count = count_items(camp_file_path)
    
    print(f"Total number of events: {event_count}")
    print(f"Total number of art: {art_count}")
    print(f"Total number of camps: {camp_count}")

if __name__ == "__main__":
    main()
