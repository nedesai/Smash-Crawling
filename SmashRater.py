import pickle
import glicko2
import re
import operator
import Queue
import urllib2
import urlparse
import socket
from sets import Set
from bs4 import BeautifulSoup as bs

class Match:
	def __init__(self, player1name, player1score, player2name, player2score):
		self.player1name = player1name
		self.player1score = player1score
		self.player2name = player2name
		self.player2score = player2score

''''''
# http://stackoverflow.com/questions/19201290/how-to-save-a-dictionary-to-a-file

# Update the pkl file
def saveObj(obj, path):
	with open(path, 'wb') as f:
		pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

# Return the data at path
def loadObj(path):
	with open(path, 'rb') as f:
		return pickle.load(f)	
''''''
# Purpose: Use this function once. It is for constructing the .pkl data file
# 		   that will store the map of player names to ratings.
# In:      pathToMatches - string of path to the file that holds the match data
#	       pathToPlayers - string of path to the file that WILL hold the player
#		   data
# Out: 	   Dictionary of player names to glicko2.Player() objects. Every player
#		   will have their glicko2 rating after all the matches seen.
def initPlayerDataWrite(pathToMatches, pathToPlayers):

	matches = []
	players = {}

	# Construct an ordered list of the matches
	with open(pathToMatches, "r") as f:
		for line in f:
			info = re.split('\s+', line.rstrip())
			matches.append(Match(info[0], int(info[1]), info[2], int(info[3])))

	for match in matches:
		
		player1name = match.player1name
		player1score = match.player1score
		player2name = match.player2name
		player2score = match.player2score
		
		if player1name not in players:
			players[player1name] = glicko2.Player()
		if player2name not in players:
			players[player2name] = glicko2.Player()
			
		# Update both players ratings and rd's
		# There are no ties in matches
		players[player1name].update_player([players[player2name].getRating()], [players[player2name].getRd()], [player1score > player2score])
		players[player2name].update_player([players[player1name].getRating()], [players[player1name].getRd()], [player1score < player2score])
		
		# FIXME: too slow? worth it?
		# Update the rating deviation of all other players
		for playerName in players:
			if playerName != player1name and playerName != player2name:
				players[playerName].did_not_compete()
				
	# Write pkl file of players
	selfref_list = [1, 2, 3]
	selfref_list.append(selfref_list)
	output = open(pathToPlayers, 'wb')
	pickle.dump(players, output)
	pickle.dump(selfref_list, output, -1)
	output.close()
	
	return players

# Purpose: Prints top N players in desc order by rating.
# In:      N - number of players to print
def printTopN(N, players):
	
	if N > len(players):
		N = len(players)
	if N < 0:
		N = 1
	
	namePlayerTuples = players.items()
	namePlayerTuples.sort(key = lambda x : x[1].getRating(), reverse = True)

	for name, player in namePlayerTuples:
		printPlayer(name, player)

# Purpose: Prints in a cleaner way the name, rating, and deviation of a player
# In:      playerName - name of the player to print
#		   playerObj - the glicko2.Player() object to print rating and rd from
def printPlayer(playerName, playerObj):
	print "Player:\t" + playerName
	print playerObj
	print '\n'
		
# Returns a list of all brackets under MichiganSmash.challonge.com domain
def compileMatches():
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

	return tournaments

def main():
	brackets = compileMatches()
	"""
	pathToMatches = "data/matches.txt"
	pathToPlayers = "data/players.pkl"
	# Initial data construction
	players = initPlayerDataWrite(pathToMatches, pathToPlayers)
	
	#players = loadObj(pathToPlayerData)

	printTopN(10, players)
	"""
	
	
if __name__ == "__main__":
	main()