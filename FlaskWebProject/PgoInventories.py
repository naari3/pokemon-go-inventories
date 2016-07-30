#!/usr/bin/env python
"""
pgoapi - Pokemon Go API
Copyright (c) 2016 tjado <https://github.com/tejado>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

Author: tjado <https://github.com/tejado>
"""


import os
import re
import sys
import json
import time
import struct
import pprint
import logging
import requests
import getpass

# add directory of this file to PATH, so that the package will be found
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# import Pokemon Go API lib
from pgoapi import pgoapi
from pgoapi import utilities as util

# other stuff
from google.protobuf.internal import encoder
from geopy.geocoders import GoogleV3
from s2sphere import Cell, CellId, LatLng
from collections import defaultdict


log = logging.getLogger(__name__)

class PgoInventories(object):
    def __init__(self):
        pass

    def get_pos_by_name(self, location_name):
        geolocator = GoogleV3()
        loc = geolocator.geocode(location_name, timeout=10)
        if not loc:
            return None

        log.info('Your given location: %s', loc.address.encode('utf-8'))
        log.info('lat/long/alt: %s %s %s', loc.latitude, loc.longitude, loc.altitude)

        return (loc.latitude, loc.longitude, loc.altitude)

    def get_cell_ids(self, lat, long, radius = 10):
        origin = CellId.from_lat_lng(LatLng.from_degrees(lat, long)).parent(15)
        walk = [origin.id()]
        right = origin.next()
        left = origin.prev()

        # Search around provided radius
        for i in range(radius):
            walk.append(right.id())
            walk.append(left.id())
            right = right.next()
            left = left.prev()

        # Return everything
        return sorted(walk)

    def encode(self, cellid):
        output = []
        encoder._VarintEncoder()(output.append, cellid)
        return ''.join(output)

    def init_config(self, username, password, auth_service, location):

        class Config: pass
        config = Config()

        config.username = username
        config.password = password
        config.auth_service = auth_service
        config.location = location
        config.debug = False
        config.test = False

        return config


    def main(self, username, password, auth_service, location):
        # log settings
        # log format
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(module)10s] [%(levelname)5s] %(message)s')
        # log level for http request class
        logging.getLogger("requests").setLevel(logging.WARNING)
        # log level for main pgoapi class
        logging.getLogger("pgoapi").setLevel(logging.INFO)
        # log level for internal pgoapi class
        logging.getLogger("rpc_api").setLevel(logging.INFO)

        config = self.init_config(username, password, auth_service, location)
        if not config:
            return

        if config.debug:
            logging.getLogger("requests").setLevel(logging.DEBUG)
            logging.getLogger("pgoapi").setLevel(logging.DEBUG)
            logging.getLogger("rpc_api").setLevel(logging.DEBUG)

        position = self.get_pos_by_name(config.location)
        if not position:
            return

        if config.test:
            return

        # instantiate pgoapi
        api = pgoapi.PGoApi()

        # provide player position on the earth
        api.set_position(*position)

        if not api.login(config.auth_service, config.username, config.password):
            return

        # get inventory call
        # ----------------------
        api.get_inventory()

        # execute the RPC call
        response_dict = api.call()

        approot = os.path.dirname(os.path.realpath(__file__))

        with open(os.path.join(approot, 'data/moves_ja.json')) as data_file:
            moves = json.load(data_file)

        with open(os.path.join(approot, 'data/pokemon_ja.json')) as data_file:
            pokemon = json.load(data_file)

        def format(i):
            i = i['inventory_item_data']['pokemon_data']
            i = {k: v for k, v in i.items() if k in ['nickname','move_1', 'move_2', 'pokemon_id', 'individual_defense', 'stamina', 'cp', 'individual_stamina', 'individual_attack']}
            i['individual_defense'] =  i.get('individual_defense', 0)
            i['individual_attack'] =  i.get('individual_attack', 0)
            i['individual_stamina'] =  i.get('individual_stamina', 0)
            i['power_quotient'] = round(((float(i['individual_defense']) + float(i['individual_attack']) + float(i['individual_stamina'])) / 45) * 100)
            i['name'] = list(filter(lambda j: int(j['Number']) == i['pokemon_id'], pokemon))[0]['Name']
            i['move_1'] = list(filter(lambda j: j['id'] == i['move_1'], moves))[0]['name']
            i['move_2'] = list(filter(lambda j: j['id'] == i['move_2'], moves))[0]['name']
            return i

        all_pokemon = filter(lambda i: 'pokemon_data' in i['inventory_item_data'] and 'is_egg' not in i['inventory_item_data']['pokemon_data'], response_dict['responses']['GET_INVENTORY']['inventory_delta']['inventory_items'])
        all_pokemon = list(map(format, all_pokemon))
        all_pokemon.sort(key=lambda x: x['power_quotient'], reverse=True)

        return all_pokemon
