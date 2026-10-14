from flask import Flask, make_response, jsonify, request
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017")
db = client.bizDB
businesses = db.biz

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return make_response("<h1>Welcome to Flask</h1>", 200)


# GET all businesses (with paging)
@app.route("/api/v1.0/businesses", methods=["GET"])
def show_all_businesses():
    page_num, page_size = 1, 5

    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))
    if request.args.get('ps'):
        page_size = int(request.args.get('ps'))

    page_start = page_size * (page_num - 1)

    data_to_return = []
    for business in businesses.find().skip(page_start).limit(page_size):
        business["_id"] = str(business["_id"])
        data_to_return.append(business)

    return make_response(jsonify(data_to_return), 200)


# GET one business by its _id
@app.route("/api/v1.0/businesses/<string:id>", methods=["GET"])
def show_one_business(id):
    if not ObjectId.is_valid(id):
        return make_response(jsonify({"error": "Invalid business ID"}), 404)

    business = businesses.find_one({"_id": ObjectId(id)})
    if business is None:
        return make_response(jsonify({"error": "Business not found"}), 404)

    business["_id"] = str(business["_id"])
    return make_response(jsonify(business), 200)


# POST - add a new business
@app.route("/api/v1.0/businesses", methods=["POST"])
def add_business():
    new_business = {
        "name": request.form["name"],
        "town": request.form["town"],
        "rating": int(request.form["rating"]),
        "reviews": []
    }
    result = businesses.insert_one(new_business)
    new_link = "http://localhost:5001/api/v1.0/businesses/" + str(result.inserted_id)
    return make_response(jsonify({"url": new_link}), 201)


# PUT - edit an existing business
@app.route("/api/v1.0/businesses/<string:id>", methods=["PUT"])
def edit_business(id):
    if not ObjectId.is_valid(id):
        return make_response(jsonify({"error": "Invalid business ID"}), 404)

    result = businesses.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "name": request.form["name"],
            "town": request.form["town"],
            "rating": int(request.form["rating"])
        }}
    )
    if result.matched_count == 0:
        return make_response(jsonify({"error": "Business not found"}), 404)

    edited_link = "http://localhost:5001/api/v1.0/businesses/" + id
    return make_response(jsonify({"url": edited_link}), 200)


# DELETE - remove a business
@app.route("/api/v1.0/businesses/<string:id>", methods=["DELETE"])
def delete_business(id):
    if not ObjectId.is_valid(id):
        return make_response(jsonify({"error": "Invalid business ID"}), 404)

    result = businesses.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return make_response(jsonify({"error": "Business not found"}), 404)

    return make_response(jsonify({"message": "Business removed successfully"}), 200)


if __name__ == "__main__":
    app.run(debug=True, port=5001)