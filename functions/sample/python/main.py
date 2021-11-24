#
#
# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#
#
from cloudant.client import Cloudant
from cloudant.error import CloudantException
import requests


def main(dict=None):
    try:
        client = Cloudant.iam(
            account_name=dict["COUCH_USERNAME"],
            api_key=dict["IAM_API_KEY"],
            url=dict['COUCH_URL'],
        )
        my_result = {'rows': []}
        reviews_db = client["reviews"]
        # if "__ow_method" in dict and dict["__ow_method"] == 'get':
        if 'dealerId' in dict:
            dealerId = int(dict['dealerId'])
            reviews_db.create_query_index(
                design_document_id='query',
                index_name='dealer_id',
                fields=['dealership']
            ).create()
            include_docs = reviews_db.get_query_result({'dealership': dealerId})
            for doc in include_docs:
                my_result['rows'].append(doc)
            return my_result
        if 'review' in dict:
            fields = ['id', 'name', 'dealership', 'review', 'purchase', 'another', 'purchase_date', 'car_make', 'car_model', 'car_year']
            for field in fields:
                if field not in dict['review']:
                    return {"error": "All fields are required"}
            review = dict['review']
            for key, val in review.items():
                if val == "":
                    return {"error": "empty values are not allowed!"}
            reviews_db.create_document(review)
            return {"message": "Review has been created!"}
        return {"message": "Review is missing!"}
    except CloudantException as ce:
        print("unable to connect")
        return {"error": ce}
    except (requests.exceptions.RequestException, ConnectionResetError) as err:
        print("connection error")
        return {"error": err}

    # return {"dbs": client.all_dbs()}
print(main({"dealerId" : 15}))