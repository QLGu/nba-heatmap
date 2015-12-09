
from flask import Flask
from flask.ext.compress import Compress
from secret import SECRET_KEY

app = Flask(__name__)
Compress(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config.from_object(__name__)
