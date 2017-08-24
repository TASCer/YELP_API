"""
Yelp Fusion API code sample.

This program demonstrates the capability of the Yelp Fusion API
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.

Please refer to http://www.yelp.com/developers/v3/documentation for the API
documentation.

This program requires the Python requests library, which you can install via:
`pip install -r requirements.txt`.

Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""
import json
import requests

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    print("Don't use Python 2.x")

# OAuth credential placeholders that must be filled in by users.
CLIENT_ID = "**********************************"
CLIENT_SECRET = "********************************"

# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
TOKEN_PATH = '/oauth2/token'
GRANT_TYPE = 'client_credentials'


#We'll use the get_lat_lng function we wrote way back in week 3
def get_lat_lng(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address='
    url += address
    import requests
    response = requests.get(url)
    if not (response.status_code == 200):
        return None
    data = response.json()
    if not( data['status'] == 'OK'):
        return None
    main_result = data['results'][0]
    geometry = main_result['geometry']
    latitude = geometry['location']['lat']
    longitude = geometry['location']['lng']
    return latitude,longitude

#Now set up our search parameters
def set_search_parameters(lat, long, radius):
    # See the Yelp API for more details
    params = {}
    params["term"] = "restaurant"
    params["latitude"] = "{}".format(str(lat))
    params["longitude"] =  "{}".format(str(long))
    params["radius"] = str(radius)  # The distance around our point in metres
    params["limit"] = "10"  # Limit ourselves to 10 results

    return params

##GET RESULTS TO BE PROCESSED
def get_results(params):
    ##CREATE BEARER TOKEN FOR AUTHORIZATION
    print(params)
    auth_url = '{0}{1}'.format(API_HOST, quote(TOKEN_PATH.encode('utf8')))
    print(auth_url)
    client_data = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,  # only client_credentials for now per Yelp
    })
    #print( client_data)
    auth_headers = {'content-type': 'application/x-www-form-urlencoded'}
    auth_response = requests.request('POST', auth_url, data=client_data, headers=auth_headers)
    print(auth_response)   #200 = GOOD
    bearer_token = auth_response.json()['access_token']

    ##REQUEST DATA FOR THE SEARCH
    search_url = API_HOST+SEARCH_PATH
    print(search_url)
    search_header = {'Authorization': 'Bearer %s' % bearer_token}
    search_response = requests.request('GET', search_url, headers=search_header, params=params)
    print(search_response)
    search_response = search_response.json()

    return search_response

lat, long = get_lat_lng("Columbia University")
params = set_search_parameters(lat,long,200)
#print(lat, long, params)
#print(set_search_parameters(lat, long, 200))
response = get_results(set_search_parameters(get_lat_lng("Community Food and Juice")[0],get_lat_lng("Community Food and Juice")[1],200))
print(response)