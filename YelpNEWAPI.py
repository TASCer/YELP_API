
import json
import requests
import collections
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    print("Don't use Python 2.x")

# OAuth credential placeholders that must be filled in by users.
CLIENT_ID = "-----------------"
CLIENT_SECRET = "------------------"

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
    auth_url = '{0}{1}'.format(API_HOST, quote(TOKEN_PATH.encode('utf8')))
    #print(auth_url)
    client_data = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,  # only client_credentials for now per Yelp
    })
    auth_headers = {'content-type': 'application/x-www-form-urlencoded'}
    auth_response = requests.request('POST', auth_url, data=client_data, headers=auth_headers)
    #print(auth_response)   #200 = GOOD
    bearer_token = auth_response.json()['access_token']

    ##REQUEST DATA FOR THE SEARCH
    search_url = API_HOST+SEARCH_PATH
    search_header = {'Authorization': 'Bearer %s' % bearer_token}
    search_response = requests.request('GET', search_url, headers=search_header, params=params)
    #print(search_response)
    search_response = search_response.json()

    return search_response

def get_snippets(response):
    all_snippets = []
    auth_url = '{0}{1}'.format(API_HOST, quote(TOKEN_PATH.encode('utf8')))
    client_data = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,  # only client_credentials for now per Yelp
    })
    auth_headers = {'content-type': 'application/x-www-form-urlencoded'}
    auth_response = requests.request('POST', auth_url, data=client_data, headers=auth_headers)
    #print(auth_response)  # 200 = GOOD
    bearer_token = auth_response.json()['access_token']

    Reviews_LIST = [] #A LIST of TUPLES
    for business in response['businesses']:
        id = business['id']
        name = business['name']
        URL = API_HOST+BUSINESS_PATH+id+'/reviews'.format(id)
        Reviews_LIST.append((id, name, URL))
    for item in Reviews_LIST:
        review_header = {'Authorization': 'Bearer %s' % bearer_token}
        review_response = requests.request('GET', item[2], headers=review_header, params=params)
        review_response = review_response.json()
        reviews = review_response.get('reviews')[0]
        #print(reviews)
        snippet = reviews['text']
        #print(all_snippets)
        all_snippets.append((item[1], snippet))
    return all_snippets

##CREATE NRC EMOTIONS DICT
def get_nrc_data():
    nrc = "data/NRC-emotion-lexicon-wordlevel-alphabetized-v0.92.txt"
    count=0
    emotion_dict=dict()
    with open(nrc,'r') as f:
        all_lines = list()
        for line in f:
            if count < 46:
                count+=1
                continue
            line = line.strip().split('\t')
            if int(line[2]) == 1:
                if emotion_dict.get(line[0]):
                    emotion_dict[line[0]].append(line[1])
                else:
                    emotion_dict[line[0]] = [line[1]]
    return emotion_dict

emotion_dict = get_nrc_data()

def emotion_analyzer(text, emotion_dict=emotion_dict):
    # Set up the result dictionary
    #print(emotion_dict.values())
    #print(text)
    emotions = {x for y in emotion_dict.values() for x in y}
    emotion_count = dict()
    for emotion in emotions:
        emotion_count[emotion] = 0
    # Analyze the text and normalize by total number of words
    total_words = len(text.split())
    for word in text.split():
        if emotion_dict.get(word):
            for emotion in emotion_dict.get(word):
                emotion_count[emotion] += 1 / len(text.split())
    return emotion_count

def comparative_emotion_analyzer(text_tuples):
    #print("TEXT TUPLES! ", text_tuples)
    print("%-20s %1s\t%1s %1s %1s %1s   %1s %1s %1s %1s" % (
        "restaurant", "fear", "trust", "negative", "positive", "joy", "disgust", "anticip",
        "sadness", "surprise"))

    for text_tuple in text_tuples:
        #print("TEXT TUPLE!", text_tuple)
        text = text_tuple[1]
        #print("-------text", text)
        result = emotion_analyzer(text)
        #print("RESULT: ", result)
        print("%-20s %1.2f\t%1.2f\t%1.2f\t%1.2f\t%1.2f\t%1.2f\t%1.2f\t%1.2f\t%1.2f" % (
            text_tuple[0][0:20], result['fear'], result['trust'],
            result['negative'], result['positive'], result['joy'], result['disgust'],
            result['anticipation'], result['sadness'], result['surprise']))

    return
lat, long = get_lat_lng("Columbia University")
params = set_search_parameters(lat,long,200)
response = get_results(set_search_parameters(get_lat_lng("Community Food and Juice")[0],get_lat_lng("Community Food and Juice")[1],200))

all_snippets = get_snippets(response)

print(comparative_emotion_analyzer(all_snippets))