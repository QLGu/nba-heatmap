# Entry point for all to avoid circular imports
from app import app
from views import *
from flask.ext.compress import Compress

if __name__ == "__main__":
    compress = Compress()
    app.config['COMPRESS_LEVEL'] = 9

    compress.init_app(app)
    app.run(debug=True)

