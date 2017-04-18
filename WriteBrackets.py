import Queue
import urllib2
import urlparse
import socket
from sets import Set
from bs4 import BeautifulSoup as bs
import os

# Returns a list of all brackets under MichiganSmash.challonge.com domain
def writeChallongeBracketURLs():
	seed_link = "http://michigansmash.challonge.com/"

	unvisited = Queue.Queue()
	visited = set([])

	unvisited.put(seed_link)

	tournaments = []
	while not unvisited.empty():
		url = unvisited.get()
		try:
			req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
			page = urllib2.urlopen(req, timeout=3.05)
		except urllib2.HTTPError, err: 
			continue
		except urllib2.URLError, err:
			continue
		except socket.error as err:
			continue
		except Exception as err:
			continue

		visited.add(url)

		#print page.read()
		soup = bs(page.read(), 'html.parser')

		
		for link in soup.find_all('a', href=True):
			l = urlparse.urlparse(link.get('href'))

			# Put all challonge pages to be visited in unvisited
			if "/?page=" in l.geturl():
				other_page = "http://michigansmash.challonge.com" + l.geturl()
				if other_page not in unvisited.queue and other_page not in visited:
					unvisited.put("http://michigansmash.challonge.com" + l.geturl())

			# Put all tournaments into a list
			if "http://michigansmash.challonge.com" in l.geturl() and "/module/instructions" not in l.geturl():
				tournaments.append(l.geturl()) 
	

	f = open("data/challongeBracketURLs.txt", "w")
	for URL in tournaments:
		f.write(URL + "\n")


def writeSmashGGBracketURLs():
	seed_link = "https://smash.gg/tournaments?per_page=100&filter=%7B%22upcoming%22%3Afalse%2C%22countryCode%22%3A%22US%22%2C%22addrState%22%3A%22MI%22%2C%22past%22%3Atrue%7D&page=1"
	unvisited = Queue.Queue()
	visited = set([])


	unvisited.put(seed_link)

	tournaments = []
	while not unvisited.empty():
		url = unvisited.get()
		try:
			req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
			page = urllib2.urlopen(req, timeout=3.05)
		except urllib2.HTTPError, err: 
			continue
		except urllib2.URLError, err:
			continue
		except socket.error as err:
			continue
		except Exception as err:
			continue

		visited.add(url)

		#print page.read()
		soup = bs(page.read(), 'html.parser')

		
		for link in soup.find_all('a', href=True):
			l = urlparse.urlparse(link.get('href'))
			#print l.geturl()
			
	f = open("smashggbrackets.txt", "r")
	o = open("data/smashGGBracketURLs.txt", "w")
	for URL in f:
		o.write(URL + "\n")
