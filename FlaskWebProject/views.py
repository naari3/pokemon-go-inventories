"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, jsonify, request, session, redirect, url_for
import json
from FlaskWebProject import app
from PgoInventories import PgoInventories
pi = PgoInventories()
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = 'Pokemon Go is God'

apis = []

@app.route('/')
def home():
    """Renders the home page."""
    return render_template(
        'pokeform.html'
    )

@app.route('/rcv', methods=['POST'])
def recv():
    """Return pokemon json."""
    username = request.form.get("username", type=str)
    password = request.form.get("password", type=str)
    auth_service = request.form.get("auth_service", type=str)
    login_dict = {"username": username, "password": password, "auth_service": auth_service}
    poke_dict, api = pi.main(username, password, auth_service, "Tokyo sta")
    apis.append(api)
    session['apinum'] = apis.index(api)
    print(session['apinum'])

    return jsonify(ResultSet=poke_dict, ensure_ascii=False)

@app.route('/rename', methods=['POST'])
def rename():
    """receive rename request."""
    if str(session['apinum']):
        print(session['apinum'])
        pokeid = int(request.form.get("pokeid", type=str))
        pokename = request.form.get("pokename", type=str)
        print(pokeid, pokename)
        res = apis[session['apinum']].nickname_pokemon(pokemon_id=pokeid, nickname=pokename)
        print(res)
        return jsonify(ResultSet=res, ensure_ascii=False)
    else:
        return "You aren't logged in.", 500

@app.route('/favorite', methods=['POST'])
def favorite():
    """receive favorite request."""
    if str(session['apinum']):
        print(session['apinum'])
        pokeid = int(request.form.get("pokeid", type=str))
        is_favorite = request.form.get("is_favorite", type=str)
        print(pokeid, is_favorite)
        if "true" == is_favorite:
            is_favorite = True
        else:
            is_favorite = False
        res = apis[session['apinum']].set_favorite_pokemon(pokemon_id=pokeid, is_favorite=is_favorite)
        print(res)
        return jsonify(ResultSet=res, ensure_ascii=False)
    else:
        return "You aren't logged in.", 500
