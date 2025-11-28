import json
import reverse_geocoder as rg
from shapely.geometry import shape

# CONFIGURATION
INPUT_FILE = 'cities.geojson' 
OUTPUT_FILE = 'cities_with_country_state.geojson'

def enrich_data():
    print(f"Loading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    # 1. Extract coordinates for batch processing
    # We use the 'centroid' (center point) of the polygon to determine location
    coords = []
    indices = []
    
    print("Calculating centroids...")
    for i, feature in enumerate(data['features']):
        # Convert GeoJSON geometry to a Shapely shape to easily find the center
        geom = shape(feature['geometry'])
        centroid = geom.centroid
        
        # IMPORTANT: GeoJSON is (Longitude, Latitude)
        # reverse_geocoder expects (Latitude, Longitude)
        coords.append((centroid.y, centroid.x))
        indices.append(i)

    # 2. Perform the lookup
    # doing this in one batch is much faster than a loop
    print(f"Looking up locations for {len(coords)} cities...")
    results = rg.search(coords)

    # 3. Inject the new data back into the GeoJSON
    print("Updating dataset...")
    for i, result in zip(indices, results):
        props = data['features'][i]['properties']
        
        # 'cc' = Country Code (e.g., US, JP)
        # 'admin1' = Top-level administrative region (State, Prefecture, Province)
        props['country_code'] = result['cc']
        props['state'] = result['admin1'] 
        
        # Optional: Add full country name if you prefer that over code
        # props['country_name'] = result['country']

    # 4. Save to new file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Done! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    enrich_data()