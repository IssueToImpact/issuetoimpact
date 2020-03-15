import requests
from geopy.geocoders import Nominatim
'''
Find a user's local representatives (and their contact details) given an
address string input
'''

def calculate_lat_long_from_address(address_string):
    '''
    Find latitude and longitude of address

    Inputs:
        address_string (str): user's address string
    Returns:
        (latitude, longitude) (floats): the lat and long of the inputed address
    '''
    geolocator = Nominatim(user_agent="issuetoimpact")
    location = geolocator.geocode(address_string)

    return (location.latitude, location.longitude)

def call_openstates_api(lat, long):
    '''
    Call openstates api to find local representatives and their contact
    information, given address latitude and longitude

    Inputs:
        lat (float): address latitude
        long (float): address longitude
    Returns:
        Api call response json
    '''
    query = """
    {{
      people(latitude: {lat}, longitude: {long}, first: 100) {{
        edges {{
          node {{
            name
            contact: contactDetails {{type, value}}
            chamber: currentMemberships(classification:["upper", "lower"]) {{
              post {{
                label
              }}
              organization {{
                name
                classification
                parent {{
                  name
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """
    variables = {
       "lat": lat,
       "long": long
    }

    open_states_api = 'https://openstates.org/graphql'
    headers = {'X-API-Key':'67a3f9ad-bd88-4561-b6fd-7c4719f0b397'}
    response = requests.post(open_states_api, headers=headers,
                            json={'query': query.format(**variables)})
    return response.json()

def process_openstates_response(openstates_response):
    '''
    Generate representatives contact information dictionary from api response

    Inputs:
        openstates_response (json): api request response
    Returns:
        representatives (dict): representatives and contact info dictionary
    '''
    representatives = {}
    for person in openstates_response["data"]["people"]["edges"]:
        rep_dict = {}
        rep_dict['name'] = person["node"]["name"]
        rep_dict['chamber'] = person["node"]["chamber"][0]["organization"]["name"]
        rep_dict['contact_details'] = {}
        for contact in person["node"]["contact"]:
            rep_dict['contact_details'][contact["type"]] = contact["value"]
        representatives[rep_dict['name']] = rep_dict

    return representatives

def find_rep_from_address(address_string):
    '''
    Given address string input, generate dictionary of local representatives
    and their contact information

    Inputs:
        address_string (str): address string
    Returns:
        (dict) representatives contact information dictionary
    '''
    lat, long = calculate_lat_long_from_address(address_string)
    openstates_rep_response = call_openstates_api(lat, long)

    return process_openstates_response(openstates_rep_response)
