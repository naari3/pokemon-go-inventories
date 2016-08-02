"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, jsonify, request, session, redirect, url_for
import json
from FlaskWebProject import app
from PgoInventories import PgoInventories
import hashlib

pi = PgoInventories()
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = 'Pokemon Go is God'

apis = {}
releases = {}

salt = "Salt"

@app.route('/')
def home():
    """Renders the home page."""
    return render_template(
        'pokeform.html'
    )

@app.route('/login', methods=['POST'])
def login():
    """Return pgoapi instance dict's key."""
    username = request.form.get("username", type=str)
    password = request.form.get("password", type=str)
    auth_service = request.form.get("auth_service", type=str)
    login_dict = {"username": username, "password": password, "auth_service": auth_service}
    api = pi.pgologin(username, password, auth_service, "Tokyo sta")
    hashed = hashlib.sha256((salt + username + " " + salt +  password + " " + salt + auth_service).encode('utf-8')).hexdigest()
    for i in range(10000):
        hashed = hashlib.sha256(hashed.encode('utf-8')).hexdigest()
    apis[hashed] = api
    session['apinum'] = hashed
    print(session['apinum'])

    return "success", 200

@app.route('/inventory', methods=['POST'])
def inventory():
    """Return pokemon json."""
    poke_dict = pi.pokedict(apis[session['apinum']])

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

@app.route('/release', methods=['POST'])
def release():
    """receive rename request."""
    if str(session['apinum']):
        print(session['apinum'])
        pokeid = int(request.form.get("pokeid", type=str))
        print(pokeid)
        releases[str(session['apinum'])] = pokeid
        return "success", 200
    else:
        return "You aren't logged in.", 500

@app.route('/release_accept', methods=['POST'])
def release_accept():
    """receive rename request."""
    if str(session['apinum']):
        print(session['apinum'])
        print(str(session['apinum']))
        pokeid = releases[str(session['apinum'])]
        res = apis[session['apinum']].release_pokemon(pokemon_id=pokeid)
        print(res)
        return jsonify(ResultSet=[res, pokeid], ensure_ascii=False)
    else:
        return "You aren't logged in.", 500

@app.route('/release_cancel', methods=['POST'])
def release_cancel():
    """receive rename request."""
    if str(session['apinum']):
        print(session['apinum'])
        releases[str(session['apinum'])] = 0
        return "success", 200
    else:
        return "You aren't logged in.", 500
