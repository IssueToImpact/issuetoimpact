import requests
from geopy.geocoders import Nominatim

def find_rep_from_address(address_string):
    '''
    '''
    lat, long = calculate_lat_long_from_address(address_string)
    openstates_rep_response = call_openstates_api(lat, long)

    return process_openstates_response(openstates_rep_response)


def calculate_lat_long_from_address(address_string):
    '''
    '''
    geolocator = Nominatim(user_agent="test")
    location = geolocator.geocode(address_string)

    return (location.latitude, location.longitude)

def call_openstates_api(lat, long):
    '''
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
       "lat": round(float(lat), 9),
       "long": round(float(long), 9)
    }

    open_states_api = 'https://openstates.org/graphql'
    headers = {'X-API-Key':'67a3f9ad-bd88-4561-b6fd-7c4719f0b397'}
    response = requests.post(open_states_api, headers=headers, json={'query': query.format(**variables)})
    return response.json()

def process_openstates_response(openstates_response):
    '''
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
