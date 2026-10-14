
from flask import Flask, make_response, jsonify, request

from pymongo import MongoClient
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client.bizDB
businesses = db.biz

app = Flask(__name__)


# Routes (Endpoints)


@app.route("/", methods=['GET'])
def homePage():
    return make_response("<h1>Hi Rupesh, This is Flask.</h1>", 200)


@app.route("/test", methods=['GET'])
def test():
    return make_response(
        jsonify({"Message": " Welcome to COM661"}), 200
    )


@app.route("/api/v1.0/businesses", methods=['GET'])
def getAllBusinesses():

    page_num, page_size = 1, 5

    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))

    if request.args.get('ps'):
        page_size = int(request.args.get('ps'))

    page_start = page_size * (page_num - 1)

    data_to_return = []

    for biz in businesses.find().skip(page_start).limit(page_size):
        biz['_id'] = str(biz['_id'])

        for review in biz.get('reviews', []):
            if '_id' in review:
                review['_id'] = str(review['_id'])

        data_to_return.append(biz)

    return make_response(jsonify(data_to_return), 200)


@app.route("/api/v1.0/businesses/<string:id>", methods=['GET'])
def getOneBusiness(id):

    if not ObjectId.is_valid(id):
        return make_response(
            jsonify({"Error": "Invalid Business ID"}), 400
        )

    biz = businesses.find_one({"_id": ObjectId(id)})

    if biz:
        biz['_id'] = str(biz['_id'])

        for review in biz.get('reviews', []):
            if '_id' in review:
                review['_id'] = str(review['_id'])

        return make_response(jsonify(biz), 200)

    return make_response(
        jsonify({"Error": "Invalid Business ID"}), 404
    )


@app.route("/api/v1.0/businesses/<string:id>/rating", methods=['GET'])
def getOneBusinessRating(id):

    if not ObjectId.is_valid(id):
        return make_response(
            jsonify({"Error": "Invalid Business ID"}), 400
        )

    biz = businesses.find_one(
        {"_id": ObjectId(id)},
        {"rating": 1}
    )

    if biz:
        return make_response(jsonify(biz.get("rating")), 200)

    return make_response(
        jsonify({"Error": "Invalid Business ID"}), 404
    )


@app.route("/api/v1.0/businesses/<string:id>/reviews", methods=['GET'])
def getOneBusinessReviews(id):

    if not ObjectId.is_valid(id):
        return make_response(
            jsonify({"Error": "Invalid Business ID"}), 400
        )

    biz = businesses.find_one(
        {"_id": ObjectId(id)},
        {"reviews": 1}
    )

    if biz:
        reviews = biz.get("reviews", [])

        for review in reviews:
            if '_id' in review:
                review['_id'] = str(review['_id'])

        return make_response(jsonify(reviews), 200)

    return make_response(
        jsonify({"Error": "Invalid Business ID"}), 404
    )


# Run the server

if __name__ == "__main__":
    app.run(port=5001, debug=True)
