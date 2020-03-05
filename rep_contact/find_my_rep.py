import requests
from geopy.geocoders import Nominatim

REP_CONTACT_DEFAULT = {"name": '',
               "chamber": '',
               "contact_details": {}}

def calculate_lat_long_from_address(address_string):
    '''
    '''
    geolocator = Nominatim(user_agent="test")
    location = geolocator.geocode(address_string)

    return (location.latitude, location.longitude)

def call_openstates_api(lat, long):
    '''
    '''
    open_states_api = 'https://openstates.org/graphql'
    headers = {'X-API-Key':'67a3f9ad-bd88-4561-b6fd-7c4719f0b397'}
    query_str = '{people(latitude: 41.9378578, longitude: -87.6482882, first: 100){edges {node {name contact: contactDetails {type, value} chamber: currentMemberships(classification:["upper", "lower"]){post{label} organization{name classification parent {name}}}}}}}'
    data = {'query': query_str}
    response = requests.get(open_states_api, headers=headers, params=data)
    return response.json()

def process_openstates_response(openstates_response):
    '''
    '''
    representatives = []
    for person in openstates_response["data"]["people"]["edges"]:
        rep_dict = REP_CONTACT_DEFAULT
        rep_dict['name'] = person["node"]["name"]
        rep_dict['chamber'] = person["node"]["chamber"][0]["organization"]["name"]
        for contact in person["node"]["contact"]:
            rep_dict['contact_details'][contact["type"]] = contact["value"]
        representatives.append(rep_dict)

    return representatives

def find_rep_from_address(address_string):
    '''
    '''
    lat, long = calculate_lat_long_from_address(address_string)
    openstates_rep_response = call_openstates_api(lat, long)

    return process_openstates_response(openstates_rep_response)
