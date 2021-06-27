import os
from flask import (
    Flask,
    request,
    jsonify,
    abort)
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# Uncomment the following line to initialize the datbase
# THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
# THIS MUST BE UNCOMMENTED ON FIRST RUN
# Running this funciton will add one

# db_drop_and_create_all()


# ROUTES

# Gets the drinks records.
# This endpoint does not need authorization is public.
# Contain only the drink.short() data representation.
# Returns: status code 200 and json {"success": True, "drinks": drinks}
#          where drinks is the list of drinks
#          or appropriate status code indicating reason for failure.
@app.route('/drinks')
def retrieve_drinks():

    try:
        drinks_q = Drink.query.all()

        drinks = [drink.short() for drink in drinks_q]

        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200

    except():
        abort(400)


# This endpoint require the 'get:drinks-detail' permission,
# contain the drink.long() data representation and
# returns status code 200 and json {"success": True, "drinks": drinks}
# where drinks is the list of drinks.
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrieve_drink_detail(payload):
    try:
        drinks_q = Drink.query.all()

        drinks = [drink.long() for drink in drinks_q]

        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200

    except():
        abort(400)


# This endpoint create a new row in the drinks table
# require the 'post:drinks' permission
# contain the drink.long() data representation
# returns: status code 200 and json {"success": True, "drinks": drink}
# where drink an array containing only the newly created drink
# or appropriate status code indicating reason for failure.
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):

    try:
        body = request.get_json(force=True)

        req_title = body.get('title', None)
        req_recipe = body.get('recipe', None)

        # verify that the recipe is not null
        if req_recipe is None:
            abort(422)

        # verify that there is no other drink with the same title
        drink_compare_title = Drink.query\
            .filter(Drink.title.like(req_title.lower())).count()

        if drink_compare_title > 0:
            abort(422)

        # json.dumps() function converts a Python object
        # into a json string.
        drink_new = Drink(title=req_title, recipe=json.dumps(req_recipe))
        drink_new.insert()
        drink = [drink_new.long()]

        return jsonify({
            'success': True,
            'drinks': drink
        }), 200

    except():
        abort(400)


# Update the corresponding row for <id> of drink.
# Respond with a 404 error if <id> is not found.
# Require the 'patch:drinks' permission.
# Contain the drink.long() data representation.
# Returns: status code 200 and json {"success": True, "drinks": drink}
# where drink an array containing only the updated drink
# or appropriate status code indicating reason for failure.
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    try:

        body = request.get_json(force=True)
        upd_title = body.get('title', None)
        upd_recipe = body.get('recipe', None)

        # verify that the recipe is not null
        if upd_recipe is None:
            abort(422)

        # verify that there is no other drink with the same title
        drink_compare_title = Drink.query.filter(Drink.id != id)\
            .filter(Drink.title.like(upd_title.lower())).count()

        if drink_compare_title > 0:
            abort(422)

        drink_upd = Drink.query.filter(Drink.id == id).one_or_none()

        if drink_upd is None:
            abort(404)

        drink_upd.title = upd_title
        drink_upd.recipe = json.dumps(upd_recipe)
        drink_upd.update()
        drink = [drink_upd.long()]

        return jsonify({
            'success': True,
            'drinks': drink
        }), 200

    except():
        abort(400)


# Delete the corresponding row for <id> of drink.
# Respond with a 404 error if <id> is not found.
# Require the 'delete:drinks' permission
# Returns: status code 200 and json {"success": True, "delete": id}
# where id is the id of the deleted record
# or appropriate status code indicating reason for failure.
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:

        drink_delete = Drink.query.filter(Drink.id == id).one_or_none()

        if drink_delete is None:
            abort(404)

        drink_delete.delete()

        return jsonify({
            'success': True,
            'delete': id
        }), 200

    except():
        abort(400)


# Error Handling
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(403)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


# Receive the raised authorization error and propagates it as response
@app.errorhandler(AuthError)
def auth_error(ex):
    print(ex.error['code'], "is the code")
    return jsonify({
        "success": False,
        "error": ex.status_code,
        "message": ex.error['code']
    }),  ex.status_code
