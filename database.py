import requests
import openpyxl
import time


place_density = {
    "Airport": 5,
    "Amusement Park": 5,
    "Aquarium": 3,
    "Art Gallery": 3,
    "Bakery": 3,
    "Bank": 4,
    "Bar": 5,
    "Book Store": 3,
    "Bus Station": 5,
    "Cafe": 4,
    "Campground": 2,
    "Car Rental": 3,
    "Car Repair": 3,
    "Casino": 4,
    "Cemetery": 1,
    "Church": 4,
    "City Hall": 4,
    "Clothing Store": 4,
    "Courthouse": 3,
    "Dentist": 3,
    "Department Store": 5,
    "Doctor": 4,
    "Electrician": 2,
    "Embassy": 4,
    "Fire Station": 3,
    "Florist": 3,
    "Funeral Home": 2,
    "Furniture Store": 2,
    "Gas Station": 2,
    "Gym": 4,
    "Hair Salon": 3,
    "Hospital": 5,
    "Hotel": 4,
    "Jewelry Store": 3,
    "Library": 3,
    "Liquor Store": 4,
    "Local Government Office": 4,
    "Mall": 5,
    "Movie Theater": 5,
    "Museum": 4,
    "Night Club": 5,
    "Park": 3,
    "Pharmacy": 4,
    "Police Station": 3,
    "Post Office": 4,
    "Restaurant": 5,
    "School": 4,
    "Shopping Mall": 5,
    "Stadium": 5,
    "Subway Station": 5,
    "Supermarket": 5,
    "Train Station": 5,
    "University": 4,
    "Zoo": 4
}

# You can print the dictionary to verify
#print(place_density)


# Your Google API Key
GOOGLE_MAPS_API_KEY = 'YOUR API KEY'

# Function to get nearby establishments within 1 km
def get_nearby_establishments(lat, lng, radius=1000):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&key={GOOGLE_MAPS_API_KEY}"
    
    response = requests.get(url)
    if response.status_code == 200:
        places = response.json().get('results', [])
        return places
    else:
        return []

# Function to get numeric value for a place type from the dictionary
def get_numeric_value_for_place(place_category):
    # Look up the place category in the dictionary
    return place_density.get(place_category, None)

# Function to map Google's place types to a broader category in the place_density dictionary
def map_to_broader_category(place_types):
    # We'll check if any place types map directly to our place_density categories
    for place_type in place_types:
        # Capitalize the place_type to match the keys in place_density dictionary
        broader_category = place_density.get(place_type.capitalize(), None)
        if broader_category is not None:
            return place_type.capitalize()  # Return the first matched broader category
    return None

# Main function to handle user input and show results
def find_restaurant_details(lat, lng, restaurant_type):
    # Get nearby establishments within 1 km
    nearby_establishments = get_nearby_establishments(lat, lng)

    # Initialize a list to store numeric values corresponding to place categories
    numbers = []

    # Iterate through the nearby establishments and check their types against the dictionary
    for place in nearby_establishments:
        place_types = place.get('types', [])  # List of types for the place
        
        # Try to map the place types to a broader category
        broader_category = map_to_broader_category(place_types)

        if broader_category:
            # Get the numeric value for this broader category from the dictionary
            numeric_value = get_numeric_value_for_place(broader_category)
            if numeric_value is not None:
                numbers.append(numeric_value)

    # Calculate the average population density based on the numbers list
    if numbers:
        Avg_population_density = sum(numbers) / len(numbers)
    else:
        Avg_population_density = 0

    # Display the results
    print(f"Nearby Establishments within 1 km: {[place['name'] for place in nearby_establishments]}")
    print(f"List of numeric values (population densities) for nearby places: {numbers}")
    print(f"Average Population Density: {Avg_population_density}")

# Example usage
lat, lng = 10.003391878837881, 76.34690985147948  # Example coordinates
restaurant_type = "Chinese"
find_restaurant_details(lat, lng, restaurant_type)