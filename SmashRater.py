import json
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
from challonge import participants, matches, tournaments
import requests

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
def compileChallongeBrackets():
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

def compileSmashGGBrackets():
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
			print l.geturl()
			

def compileChallongePlayers(challongeTournamentURLs):
	
	APIkey = "2tyMsGrcQanAq3EQeMytrsGrdMMFutDDz0BxNAAh"
	
	matchResultsAllPlayers = []
	
	for URL in challongeTournamentURLs:
		
		# A tournament participant is object w/ player id for this tournament
		tournamentParticipants = requests.get("https://Amirzy:" + APIkey + "@api.challonge.com/v1/tournaments/" + URL + "/participants.json").json()

		if len(tournamentParticipants) < 35:
			continue
			
		IdToPlayerName = {}
			
		for p in tournamentParticipants:
			playerName = p["participant"]["display_name"]
			playerName = playerName.replace(' ' , '')
			playerName = playerName.replace('\t', '')
			print playerName
			IdToPlayerName[p["participant"]["id"]] = playerName
			
		# Matches sorted 0 to N
		matchInfo = requests.get("https://Amirzy:" + APIkey + "@api.challonge.com/v1/tournaments/" + URL + "/matches.json").json() 

		#pureMatchInfo = []

		#for m in matchInfo:
		#	pureMatchInfo.append(m["match"])
			
		#pureMatchInfo.sort(key=lambda x: x["round"])
		
		for i in range(0, len(matchInfo)):
			match = matchInfo[i]
			#print match
			#print len(match["match"]["scores_csv"])
			if (len(match["match"]["scores_csv"]) == 3):
				scoreStr = match["match"]["scores_csv"]
				print scoreStr
				player1name = IdToPlayerName[match["match"]["player1_id"]]
				player1score = scoreStr[0]
				player2name = IdToPlayerName[match["match"]["player2_id"]]
				player2score = scoreStr[2]
				print player1name
				print player1score
				print player2name
				print player2score
			
				matchResultsAllPlayers.append(Match(player1name, player1score, player2name, player2score))
		
#		for m in pureMatchInfo:
#			print i
#			i+=1
#			scoreStr = m["scores_csv"]
#			player1name = IdToPlayerName[m["player1_id"]]
#			player1score = scoreStr[0]
#			player2name = IdToPlayerName[m["player2_id"]]
#			player2score = scoreStr[2]
#			
#			matchResultsAllPlayers.append(Match(player1name, player1score, player2name, player2score))
		
	return matchResultsAllPlayers
		
def writeMatches(matches, pathToMatches):
	f = open(pathToMatches, "w")
	#print matches
	for match in matches:
	#	print match
		print match.player1name
		print match.player1score
		print match.player2name
		print match.player2score
		f.write(match.player1name + " " + match.player1score + " " + match.player2name + " " + match.player2score + "\n")
	f.close()

def main():
	challonge_brackets = compileChallongeBrackets()
#	#smashgg_brackets = compileSmashGGBrackets()
#	compileSmashGGBrackets()
	
	pathToMatches = "data/matches.txt"
	pathToPlayers = "data/players.pkl"
	
	# Make a list of challonge tournament URLs
	tournamentURLs = []
	with open("data/bracketURLs.txt", "r") as f:
		for line in f:
			name = line[35:].rstrip()
			tournamentURLs.append("michigansmash-" + name)
			
	# List of Match objects for challonge matches in chronological order
	matches = compileChallongePlayers(tournamentURLs)
	writeMatches(matches, pathToMatches)

	# Initial data construction
	players = initPlayerDataWrite(pathToMatches, pathToPlayers)
	
	#players = loadObj(pathToPlayerData)

	printTopN(10, players)
	
	
	
if __name__ == "__main__":
	main()