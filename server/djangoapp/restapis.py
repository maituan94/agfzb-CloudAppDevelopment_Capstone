import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, api_key=None, **kwargs):
    try:
        if api_key:
            # Basic authentication GET  
            # response = requests.get(url, params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
            authenticator = IAMAuthenticator(api_key)
            natural_language_understanding = NaturalLanguageUnderstandingV1(
                version='2021-03-25',
                authenticator=authenticator)

            natural_language_understanding.set_service_url(url)
            response = natural_language_understanding.analyze(text=kwargs['params']['text'], features=Features(sentiment=SentimentOptions())).get_result()
            return response
        else:
            # no authentication GET
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
            status_code = response.status_code
            print("With status {} ===".format(status_code))
            json_data = json.loads(response.text)
            return json_data
    except Exception as e:
        # If any error occurs
        print("Network exception occurred {}".format(str(e)))

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
     return requests.post(url, params=kwargs, json=json_payload)

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["data"]
        print(dealers)
        # For each dealer object
        for dealer in dealers:
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"], state=dealer["state"])
            
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    # 1. get the reviews by dealerId
    # 2. convert the json objects to DealerReview objects
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        reviews = json_result["rows"]
        for review in reviews:
            review_obj = DealerReview(dealership= review.get("dealership"), name= review.get("name"), purchase= review.get("purchase"),
                                purchase_date= review.get("purchase_date"), car_make= review.get("car_make"), car_model= review.get("car_model"),
                                review= review.get("review"),
                                car_year= review.get("car_year"), id= review.get("id"))
            sentiment = analyze_review_sentiments(review_obj.review)
            if sentiment:
                review_obj.sentiment = sentiment['sentiment']['document']['label']
            else:
                review_obj.sentiment = 'neutral'
            results.append(review_obj)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerreview, **kwargs):
    url = 'https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/6fda4e06-6c2a-4641-a6a0-92f06610597e'
    api_key = 'mOj8BwTMho7MXC5VqikRhgAwKqS3dvW_qTDpmSEjsGcu'
    params = dict()

    params["text"] = dealerreview
    params["version"] = '2021-08-01'
    params["features"] = ["sentiment"]
    params["return_analyzed_text"] = False
    response = get_request(url, api_key=api_key, params=params)
    return response


