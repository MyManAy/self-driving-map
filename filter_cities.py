import json

# Files
CONFIG_FILE = 'public/operations.json'
INPUT_FILE = 'cities_with_country_state.geojson'
OUTPUT_FILE = 'public/av_cities_filtered.json'

def get_city_targets_from_config():
    """Reads the config.json and extracts only the international cities."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: {CONFIG_FILE} not found.")
        return []

    targets = []
    
    # Iterate through Providers (WAYMO, ZOOX)
    for provider in config.values():
        # Iterate through Categories (serving, next, driving)
        for category_list in provider.values():
            for item in category_list:
                # We only care about type: city for this script
                if item.get('type') == 'city':
                    targets.append(item)
    return targets

def filter_geojson():
    targets = get_city_targets_from_config()
    if not targets:
        print("No cities found in config to filter.")
        return

    print(f"Loading {INPUT_FILE}...")
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: Input file not found.")
        return

    filtered_features = []
    print(f"Filtering for {len(targets)} targets...")
    
    for feature in data.get('features', []):
        props = feature.get('properties', {})
        
        f_name = (props.get('NAME') or props.get('name') or "").upper()
        f_country = (props.get('country_code') or props.get('country') or "").upper()
        
        for target in targets:
            t_name = target['name'].upper()
            t_country = target['country_code'].upper()
            
            if f_name == t_name and f_country == t_country:
                print(f" -> Found: {target['name']}, {target['country_code']}")
                filtered_features.append(feature)

    new_geojson = {
        "type": "FeatureCollection",
        "features": filtered_features
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_geojson, f)
        
    print(f"Success! Saved filtered cities to '{OUTPUT_FILE}'")

if __name__ == "__main__":
    filter_geojson()