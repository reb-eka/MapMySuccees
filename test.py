import requests
import pandas as pd

# Replace with your own Google API key
API_KEY = ''

def get_nearby_places(api_key, location, radius, place_type):
    # Define the endpoint URL
    endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    # Set up the parameters for the request
    params = {
        'location': location,  # Latitude and Longitude as a string "lat,lng"
        'radius': radius,      # Radius in meters
        'type': place_type,    # Type of place (e.g., restaurant, park, etc.)
        'key': api_key         # Your API key
    }
    
    # Make the request to the Places API
    response = requests.get(endpoint_url, params=params)
    
    # Check if the response is OK (status code 200)
    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def places_to_dataframe(places_data):
    # Extract relevant details into a list of dictionaries
    places_list = []

    for place in places_data.get('results', []):
        place_info = {
            'Name': place.get('name'),
            'Address': place.get('vicinity'),
            'Rating': place.get('rating', 'N/A'),
            'User Ratings Total': place.get('user_ratings_total', 'N/A'),
            'Latitude': place['geometry']['location']['lat'],
            'Longitude': place['geometry']['location']['lng']
        }
        places_list.append(place_info)
    # Convert the list to a DataFrame
    df = pd.DataFrame(places_list)
    return df

def save_to_excel(df, filename='places_output.xlsx'):
    # Save DataFrame to Excel file
    df.to_excel(filename, index=False)
    print(f"Data successfully saved to {filename}")

if __name__ == "__main__":
    # Define your search parameters
    location = "10.016786,76.3412057"  # Example: Latitude,Longitude (New York)
    radius = 1500  # Search within 1500 meters
    place_type = "restaurant"  # Type of places you are searching for
    
    # Get nearby places data
    places_data = get_nearby_places(API_KEY, location, radius, place_type)
    
    if places_data:
        # Convert the results to a DataFrame
        df = places_to_dataframe(places_data)
        
        # Save the DataFrame to an Excel file
        save_to_excel(df, 'nearby_places.xlsx')
