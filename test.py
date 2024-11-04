
import requests
import pandas as pd
import time

# Replace with your own Google API key
API_KEY = 'AIzaSyD9Cq1kprcVhicNRFbYVnTszDdWUPORzUQ'

def get_nearby_places(api_key, location, radius, place_type, next_page_token=None):
    # Define the endpoint URL
    endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    # Set up the parameters for the request
    params = {
        'location': location,  # Latitude and Longitude as a string "lat,lng"
        'radius': radius,      # Radius in meters
        'type': place_type,    # Type of place (e.g., restaurant, park, etc.)
        'key': api_key         # Your API key
    }
    
    # Add the next_page_token if it exists (for paginated requests)
    if next_page_token:
        params['pagetoken'] = next_page_token
    
    # Make the request to the Places API
    response = requests.get(endpoint_url, params=params)
    
    # Check if the response is OK (status code 200)
    if response.status_code == 200:
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
    location ="10.016786,76.3412057"  # Example: Latitude,Longitude (New York)
    radius = 1500  # Search within 1500 meters
    place_type = "restaurant"  # Type of places you are searching for
    
    all_places = []  # To store all places across pages
    next_page_token = None  # Initialize with no token
    
    while True:
        # Get nearby places data
        places_data = get_nearby_places(API_KEY, location, radius, place_type, next_page_token)
        
        if places_data:
            # Convert the current page's results to a DataFrame and append to all_places
            df = places_to_dataframe(places_data)
            all_places.append(df)
            
            # Check if there is a next page token
            next_page_token = places_data.get('next_page_token')
            
            if next_page_token:
                print("Next page token found. Waiting for 2 seconds before fetching the next page...")
                # Google API requires a slight delay before using the next_page_token
                time.sleep(2)
            else:
                break  # No more pages, exit the loop
        else:
            break  # Exit if there's an error or no data

    # Concatenate all pages into a single DataFrame
    if all_places:
        final_df = pd.concat(all_places, ignore_index=True)
        
        # Save the final DataFrame to an Excel file
        save_to_excel(final_df, 'all_nearby_places.xlsx')
    else:
        print("No places data found.")
