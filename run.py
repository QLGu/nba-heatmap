# Entry point for all to avoid circular imports
from views import *

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, threaded=True) # need this to access from the outside world!

