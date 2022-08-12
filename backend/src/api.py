import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

"""
    References for this file: 
    https://github.com/conjohnson712/Trivia_API/blob/main/backend/flaskr/__init__.py
    https://github.com/udacity/FSND/blob/master/BasicFlaskAuth/app.py
    Previous Course 'API Development and Documentation': Lesson 3: Endpoints and payloads
"""


'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()

# ROUTES
  @app.after_request
  def after_request(response):
  """ Function that sets request allowances """
      response.headers.add("Access-Control-Allow-Headers", 
                          "Content-Type,Authorization,true")
      response.headers.add("Access-Control-Allow-Methods", 
                            "GET,PUT,POST,DELETE,OPTIONS")

      return response




""" 
Function that gets the short list of drinks 
Does not require special authorization to access
"""

@app.route("/drinks", methods=['GET'])
def get_drinks():
    # Get drinks via query, set to variable
    drinks = Drink.query.all()      

    # If the length of the drink list is 0, raise 404 error
    if len(drinks) == 0:        
        abort(404)

    # Return JSON object with short list of drinks and 200 status
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200


""" 
Function that returns long list of drinks. 
Requires Barista or Manager authorization.
:param payload {string} 'Token Payload (jwt)'

""" 
@app.route("/drinks-detail", methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):


    # Get drinks via query
    drinks = Drink.query.all()

    # If length of drink list is 0, raise 404 error
    if len(drinks) == 0: 
        abort(404)

    # Return JSON object containing long drink list and 200 status
    return jsonify({
        'success': True, 
        'drinks-detail': [drink.long() for drink in drinks]
    }), 200


""" 
Function that creates a new drink entry and adds it to the list. 
Requires Manager Authorization or higher
:param payload {string} 'Token Payload (jwt)'
"""
@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    # Requests the JSON body
    body = request.get_json()

    # If the body comes in empty, raise a 404 error
    if len(body) == 0:
        abort(404)

    # If the required parameters for new drinks aren't present, abort
    if 'title' and 'recipe' not in body:
        abort(422)

    # If parameters are present, return JSON object with drinks.long
    try:
        title = body['title']
        recipe = body['recipe']

        drink = Drink(title=title, recipe=recipe)
        drink.insert()

        return jsonify({
            'success': True, 
            'drinks': [drinks.long()]
        }), 200

    # Raise 422 error for any other caught errors
    except BaseException:
        abort(422)

"""
Function that updates drink information.
Requires Manager authorization or higher 
:param payload {string} 'Token Payload (jwt)
:param id {integer} 'Drink Serial ID'
Reference: https://github.com/udacity/cd0037-API-Development-and-Documentation-exercises/blob/master/1_Requests_Review/backend/flaskr/__init__.py
"""
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, id)
    # Request JSON body
    body = request.get_json()

    # Gather drinks, filtering by id
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    # If there are no drinks, raise a 404 error
    if drink is None:
        abort(404)

    # If JSON body doesn't contain needed parameters, raise 404
    if "title" and 'recipe' not in body:
        abort(404)
        
    # If title and recipe in body, update title and recipe
    try: 
        drink.title = body['title']
        drink.recipe = body['recipe']

        drink.update()      # Update drink

        # Return JSON object with long drink list and 200 status
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200

    # Have a bad request error to catch any other errors
    except BaseException:
        abort(400)




"""
Function that deletes a specific drink from the menu
Requires Manager Authorization or higher 
:param payload {string} 'Token Payload (jwt)'
:param id {integer} 'Drink serial id'
"""
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id)
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    try: 
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink.id
        }), 200

    # Raise 422 error if any other errors are caught
    except BaseException: 
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

if __name__ == "__main__":
    app.debug = True
    app.run()
