from flask import Flask
from secret import SECRET_KEY
from flask import Flask
from flask.ext.compress import Compress

compress = Compress()
app = Flask(__name__)
# app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config.from_object(__name__)
compress.init_app(app)
