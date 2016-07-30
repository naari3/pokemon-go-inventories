"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)

import FlaskWebProject.pogo_optimizer_cli
import FlaskWebProject.views
