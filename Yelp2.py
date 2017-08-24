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
#from __future__ import print_function #USED FOR CROSS PYTHON ver CODE. ONLY USING 3.x
#import argparse
import json
import pprint
import requests
import sys

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    print("Don't use Python 2.x")
# OAuth credential placeholders that must be filled in by users.
CLIENT_ID = "***********"
CLIENT_SECRET = "*********"

# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
TOKEN_PATH = '/oauth2/token'
GRANT_TYPE = 'client_credentials'

# Defaults for our simple example.
DEFAULT_TERM = 'restaurant'
DEFAULT_LAT = None
DEFAULT_LONG = None
DEFAULT_LOCATION = None
SEARCH_LIMIT = 5

#We'll use the get_lat_lng function we wrote way back in week 3
def get_lat_lng(address, radius=None):
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

def obtain_bearer_token(host, path):
    """Given a bearer token, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (ddatict): An optional set of query parameters in the request.
    Returns:
        str: OAuth bearer token, obtained using client_id and client_secret.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    data = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,           #only client_credentials for now per Yelp
    })
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.request('POST', url, data=data, headers=headers)
    bearer_token = response.json()['access_token']

    return bearer_token

def request(host, path, bearer_token, url_params=None):
    """Given a bearer token, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        bearer_token (str): OAuth bearer token, obtained using client_id and client_secret.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {'Authorization': 'Bearer %s' % bearer_token}
    print(u'Querying {0} ...'.format(url))
    response = requests.request('GET', url, headers=headers, params=url_params)
    print(response)

    return response.json()

def search(bearer_token, term, lat, long, r=None):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """
    url_params = {
        'term': term.replace(' ', '+'),
        'latitude': lat,
        'longitude':long,
        'r':20,
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, bearer_token, url_params=url_params)

def get_business(bearer_token, business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, bearer_token)

def query_api(term, lat, long, r=None):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    print(lat, long, r)
    bearer_token = obtain_bearer_token(API_HOST, TOKEN_PATH)
    #print("BEARER TOKEN", bearer_token)
    search_response = search(bearer_token, term, lat, long, r)
    print("SEARCH RESPONSE", search_response, type(search_response))
    businesses = search_response.get('businesses')
    print("BUSINESSES", businesses, type(businesses), len(businesses))
    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term))
        return
    ##GET REVIEWS OF TOP BUSINESS
    business_id = businesses[0]['id']
    reviews_url =  API_HOST+BUSINESS_PATH+business_id+'/reviews'
    print(reviews_url)
    headers = {'Authorization': 'Bearer %s' % bearer_token}
    print("*****REVIEWS URL*****", reviews_url)
    reviews = requests.request('GET', reviews_url, headers=headers)
    print("***************reviews***************", reviews.text)
    print(u'{0} businesses found, querying business info ' \
        'for the top result "{1}" ...'.format(len(businesses), business_id))
    response = get_business(bearer_token, business_id)

    print(u'Result for business "{0}" found:'.format(business_id))
    pprint.pprint(response, indent=7)


def main():
    #if not DEFAULT_LOCATION
    lat, long = (get_lat_lng("Arizona State University"))
    try:
        query_api(DEFAULT_TERM,lat,long, 2)   #input_values.location)
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )

if __name__ == '__main__':
    main()
