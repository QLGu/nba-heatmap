from bs4 import BeautifulSoup
import urllib
from lxml import html

#storing response
testfile = urllib.URLopener()
page = open('teams.html').read()


soup = BeautifulSoup(page, "lxml")
soup.prettify()


for block in soup.findAll('div',  {"class":"team-block__logo"}):
    file_name = block.find('a')['href'].split("/")[-1] + ".svg"
    url = "http://stats.nba.com" + block.find('img')['src']
    testfile.retrieve(url, "../static/assets/logos/" + file_name)
