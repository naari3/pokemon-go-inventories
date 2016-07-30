"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, jsonify, request
import json
from FlaskWebProject import app
from PgoInventories import PgoInventories
pi = PgoInventories()
app.config['JSON_AS_ASCII'] = False

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
    print(login_dict)
    poke_dict = pi.main(username, password, auth_service, "Nakameguro sta")

    return jsonify(ResultSet=poke_dict, ensure_ascii=False)
