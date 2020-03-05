import requests
from geopy.geocoders import Nominatim


geolocator = Nominatim(user_agent="test")
location = geolocator.geocode("624 West Barry Ave, CHICAGO, 60657")

headers = {'X-API-Key':'67a3f9ad-bd88-4561-b6fd-7c4719f0b397'}

data = {"query":'{people(latitude: 41.937972898282275, longitude: -87.64515975589266, first: 100){edges {node {name chamber: currentMemberships(classification:["upper", "lower"]){post{label} organization{name classification parent {name}}}}}}}'}

open_states_api = 'https://openstates.org/graphql'

response.json()
