import requests
import openpyxl
import time
import json
import math

# Your Google API Key
GOOGLE_MAPS_API_KEY = 'YOUR_API_KEY'

# Load data from data.json
with open('data.json', 'r') as json_file:
    place_data = json.load(json_file)

# Function to get nearby establishments within 1 km, including paginated results
def get_nearby_establishments(lat, lng, radius=1000):
    places = []
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&key={GOOGLE_MAPS_API_KEY}"

    while url:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            places.extend(result.get('results', []))  # Add new places to the list

            # Check if there's a next_page_token
            next_page_token = result.get('next_page_token')
            if next_page_token:
                # Update the URL for the next request with the next_page_token
                url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={next_page_token}&key={GOOGLE_MAPS_API_KEY}"
                time.sleep(2)  # Required delay before requesting the next page
            else:
                # No more pages to fetch
                url = None
        else:
            # If the API request fails, stop further requests
            break

    return places

# Function to map Google's place types to a broader category found in the data.json file
def map_to_broader_category(place_types):
    # Normalize the keys in the JSON file by making them lowercase and replacing spaces with underscores
    normalized_json_keys = {key.lower().replace(" ", "_"): value for key, value in place_data.items()}

    # We'll check if any place types map directly to our normalized JSON categories
    for place_type in place_types:
        broader_category = normalized_json_keys.get(place_type, None)  # Use normalized key lookup
        if broader_category is not None:
            return place_type  # Return the first matched broader category
    return None

# Function to get numeric value for a place category from the normalized JSON data
def get_numeric_value_for_place(place_category):
    # Look up the place category in the normalized JSON data
    normalized_json_keys = {key.lower().replace(" ", "_"): value for key, value in place_data.items()}
    return normalized_json_keys.get(place_category, None)

# Function to calculate average traffic using Google Maps Distance Matrix API
def calculate_average_traffic(lat, lng, radius=1000):
    # Define destinations for traffic checks (some random points within 1km)
    destinations = [
        f"{lat + 0.005},{lng}",
        f"{lat - 0.005},{lng}",
        f"{lat},{lng + 0.005}",
        f"{lat},{lng - 0.005}"
    ]
    
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={lat},{lng}&destinations={'|'.join(destinations)}&departure_time=now&key={GOOGLE_MAPS_API_KEY}"
    
    # Make the API request
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        travel_times = []
        
        # Iterate through the response rows and elements
        for row in data.get('rows', []):
            for element in row.get('elements', []):
                # Try to get 'duration_in_traffic', fallback to 'duration' if not available
                if 'duration_in_traffic' in element:
                    travel_times.append(element['duration_in_traffic']['value'])  # Get traffic time in seconds
                elif 'duration' in element:
                    travel_times.append(element['duration']['value'])  # Fallback to normal travel time
        
        if travel_times:
            avg_traffic_time = sum(travel_times) / len(travel_times)  # Calculate average in seconds
            return avg_traffic_time / 60  # Convert to minutes
        else:
            return None
    else:
        return None

# Function to convert traffic time to traffic severity (1-5 scale)
def convert_traffic_time_to_severity(avg_traffic_time):
    if avg_traffic_time is None:
        return 0  # No traffic data
    if avg_traffic_time < 5:
        return 1  # Low traffic
    elif avg_traffic_time < 10:
        return 2  # Moderate traffic
    elif avg_traffic_time < 15:
        return 3  # Heavy traffic
    elif avg_traffic_time < 20:
        return 4  # Very heavy traffic
    else:
        return 5  # Severe traffic

# Function to find the distance to the nearest main road using Google Maps Roads API
def find_distance_to_nearest_main_road(lat, lng):
    url = f"https://roads.googleapis.com/v1/nearestRoads?points={lat},{lng}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        if 'snappedPoints' in result:
            nearest_road_location = result['snappedPoints'][0]['location']
            nearest_lat = nearest_road_location['latitude']
            nearest_lng = nearest_road_location['longitude']
            
            # Use Haversine formula to calculate distance to the nearest road
            distance = calculate_distance(lat, lng, nearest_lat, nearest_lng)
            return distance
        else:
            return None
    else:
        return None

# Function to calculate the distance between two latitude and longitude points (Haversine formula)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat/2) * math.sin(d_lat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon/2) * math.sin(d_lon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c  # Distance in kilometers
    return distance * 1000  # Convert to meters

# Function to read the Excel file and extract the latitude and longitude
def process_excel_file(file_path):
    # Load the Excel workbook
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active

    # Iterate over the rows in the Excel sheet
    for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip header row
        name, address, rating, rating_total, latitude, longitude = row

        # Ensure latitude and longitude are present
        if latitude and longitude:
            print(f"Processing {name}: Lat {latitude}, Lng {longitude}")
            find_restaurant_details(latitude, longitude, name)

# Main function to handle user input and show results
def find_restaurant_details(lat, lng, restaurant_type):
    # Get nearby establishments within 1 km
    nearby_establishments = get_nearby_establishments(lat, lng)

    # Initialize a list to store unique place categories
    places = []
    
    # Initialize a list to store numeric values corresponding to place categories
    numbers = []

    # Iterate through the nearby establishments and check their types against the JSON file
    for place in nearby_establishments:
        place_types = place.get('types', [])  # List of types for the place
        
        # Try to map the place types to a broader category (only once per place)
        broader_category = map_to_broader_category(place_types)

        if broader_category:
            # Add unique broader category to the places list
            if broader_category not in places:
                places.append(broader_category)
            
            # Get the numeric value for this broader category from the JSON file
            numeric_value = get_numeric_value_for_place(broader_category)
            
            # Only add one numeric value per place
            if numeric_value is not None and broader_category not in numbers:
                numbers.append(int(numeric_value))  # Ensure numeric value is an integer

    # Calculate the average population density based on the numbers list
    if numbers:
        Avg_population_density = sum(numbers) / len(numbers)
    else:
        Avg_population_density = 0

    # Get average traffic in the area
    avg_traffic = calculate_average_traffic(lat, lng)

    # Convert traffic time to a severity rating (1-5)
    traffic_severity = convert_traffic_time_to_severity(avg_traffic)

    # Find distance to nearest main road
    distance_to_main_road = find_distance_to_nearest_main_road(lat, lng)

    # Display the results
    print(f"Unique Place Categories within 1 km: {places}")
    print(f"Length of places list: {len(places)}")
    print(f"List of numeric values (population densities) for nearby places: {numbers}")
    print(f"Average Population Density: {Avg_population_density}")
    print(f"Traffic Severity (1-5): {traffic_severity}")
    print(f"Distance to Nearest Main Road (meters): {distance_to_main_road}")
    print()

# Provide the Excel file path
file_path = "all_nearby_places1.xlsx"
process_excel_file(file_path)
