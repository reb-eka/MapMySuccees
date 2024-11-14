import requests
import openpyxl
import time
import json

# Load data from data.json
with open('data.json', 'r') as json_file:
    place_data = json.load(json_file)

# Your Google API Key
GOOGLE_MAPS_API_KEY = 'YOUR API KEY'

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

    # Display the results
    print(f"Unique Place Categories within 1 km: {places}")
    print(f"Length of places list: {len(places)}")
    print(f"List of numeric values (population densities) for nearby places: {numbers}")
    print(f"Length of numbers list: {len(numbers)}")
    print(f"Average Population Density: {Avg_population_density}")

# Example usage
lat, lng = 10.003391878837881, 76.34690985147948  # Example coordinates
restaurant_type = "Chinese"
find_restaurant_details(lat, lng, restaurant_type)