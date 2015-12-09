import httplib

# use this server for dev
# SERVER = 'localhost:5000'

# use this server for prod, once it's on ec2
SERVER = 'http://ec2-52-35-201-209.us-west-2.compute.amazonaws.com:5000'


def get_games():
    h = httplib.HTTPConnection(SERVER)
    print 'http://' + SERVER + '/nba/games'
    h.request('GET', 'http://' + SERVER + '/nba/games/')
    resp = h.getresponse()
    out = resp.read()
    return out


def get_teams(abbr):
    h = httplib.HTTPConnection(SERVER)
    print 'http://' + SERVER + '/nba/teams?abbr='+abbr
    h.request('GET', 'http://' + SERVER + '/teams?abbr='+abbr)
    resp = h.getresponse()
    out = resp.read()
    return out


if __name__ == '__main__':
    print "************************************************"
    print "test of my flask app running at ", SERVER
    print "created by Alex Morris"
    print "************************************************"
    print " "
    print "******** Get all games **********"
    print get_games()
    print " "
    print "******** Get Golden State Warriors information **********"
    print get_teams('GSW')
