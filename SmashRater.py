import json
import pickle
import glicko2
import re
import operator
import Queue
from challonge import participants, matches, tournaments
import requests
import WriteBrackets

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

class Match:
	def __init__(self, player1name, player1score, player2name, player2score):
		self.player1name = player1name
		self.player1score = player1score
		self.player2name = player2name
		self.player2score = player2score

class RaterSetup:
	
	def __init__(self, pathToPlayers, pathToMatches):
		
		self.pathToPlayers = pathToPlayers
		self.pathToMatches = pathToMatches
		
		# Player names |-> Glicko2 Player objects
		self.players = {}
		
		self.matches = []
		
		# Write to bracket URLs files
		WriteBrackets.writeChallongeBracketURLs()
		WriteBrackets.writeSmashGGBracketURLs()

		# Fill list of matches
		self.__setMatches()	
		
		# Write list of matches to text file	
		self.__writeMatches()
		
		# Fill map of players to Glicko2 Player objects
		self.__setPlayers()
		
		# Write file of player map (.pkl)
		self.__writePlayers()
		
	def getPlayerMap(self):
		return self.players	
		
	def __setMatches(self):
		minParticipants = 35
		challongeTournamentIds = self.__getChallongeTournamentIds()
		self.__setChallongeMatches(challongeTournamentIds, minParticipants)
		
	def __getChallongeTournamentIds(self):
		# Make a list of challonge tournament Ids
		challongeTournamentIds = []
		with open("data/challongeBracketURLs.txt", "r") as f:
			for line in f:
				name = line[35:].rstrip()
				challongeTournamentIds.append("michigansmash-" + name)
		return challongeTournamentIds
		
	# Purpose: Compile list of Match objects from Challonge
	# In:      tournamentIds - list of tournament names in format:
	# 		   michigansmash-<name>
	#		   tournaments must be in chronological order (oldest to youngest)
	#		   minParticipants - ignore tournaments with fewer participants
	# Out:	   List of Match objects of Challonge matches in chronological order
	#		   (oldest to youngest)
	def __setChallongeMatches(self, tournamentIds, minParticipants):
		
		APIkey = "2tyMsGrcQanAq3EQeMytrsGrdMMFutDDz0BxNAAh"
		tournamentsURL = "https://Amirzy:" + APIkey + "@api.challonge.com/v1/tournaments/"
		
		# Construct list of Match objects from all tournaments
		for tournamentId in tournamentIds:
			
			# A tournament participant is object w/ player id for this tournament
			participantsInTournament = requests.get(tournamentsURL + tournamentId + "/participants.json").json()

			# Ignore small tournaments
			if len(participantsInTournament) < minParticipants:
				continue
				
			# Maps player Ids to player names
			IdToPlayerName = {}
				
			# Compile id:name map
			for p in participantsInTournament:
				
				# Get playername
				playerName = p["participant"]["display_name"]
				playerName = playerName.replace(" ", "")
				playerName = playerName.replace("\t", "")
				#print playerName
				
				# Add to map
				IdToPlayerName[p["participant"]["id"]] = playerName
				
			# Dictionary from int index to json match objects
			jsonMatchesDict = requests.get(tournamentsURL + tournamentId + "/matches.json").json()
			
			# Turn the dict into a list
			jsonMatches = []
			for i in range(0, len(jsonMatchesDict)):
				jsonMatches.append(jsonMatchesDict[i]["match"])
			
			# Scores must be of the format ">-<"
			scoreFormat = re.compile("\d+-\d+")
			
			# Compile the list of Match objects
			for jsonMatch in jsonMatches:

				# Some scores are not of the right format, so skip these
				scoreStr = jsonMatch["scores_csv"]
				if not scoreFormat.match(scoreStr):
					continue
				
				# Extract scores
				separatorIndex = scoreStr.index("-")
				player1score = int(scoreStr[:separatorIndex])
				player2score = int(scoreStr[separatorIndex+1:])
				
				# Extract names
				player1name = IdToPlayerName[jsonMatch["player1_id"]].lower()
				player2name = IdToPlayerName[jsonMatch["player2_id"]].lower()
				
				# This bar indicates two players played as teammates, so skip
				if "|" in player1name or "|" in player2name:
					continue
				
				newMatch = Match(player1name, player1score, player2name, player2score)
				self.matches.append(newMatch)
		
	# Purpose: Write info of Match objects in txt file
	def __writeMatches(self):
		f = open(self.pathToMatches, "w")
		for match in self.matches:
			line = match.player1name + " "
			line += str(match.player1score) + " "
			line += match.player2name + " "
			line += str(match.player2score) + "\n"
			f.write(line)
		f.close()

	# Purpose: Use this function once. It is for constructing the .pkl data file
	# 		   that will store the map of player names to ratings.
	# Out: 	   Dictionary of player names to glicko2.Player() objects. Every player
	#		   will have their glicko2 rating after all the matches seen.
	def __setPlayers(self):

		for match in self.matches:
			
			p1name = match.player1name
			p2name = match.player2name
			p1score = match.player1score
			p2score = match.player2score
			
			# Add all players to dictionary as unrated Glicko2 player objects
			if p1name not in self.players:
				self.players[p1name] = glicko2.Player()
			if p2name not in self.players:
				self.players[p2name] = glicko2.Player()
				
			# Update both players ratings and rd's
			# There are no ties in matches
			self.players[p1name].update_player([self.players[p2name].getRating()], [self.players[p2name].getRd()], [p1score > p2score])
			self.players[p2name].update_player([self.players[p1name].getRating()], [self.players[p1name].getRd()], [p1score < p2score])
			
			# Update the rating deviation of all other players
			for playerName in self.players:
				if playerName != p1name and playerName != p2name:
					self.players[playerName].did_not_compete()
	
	# Purpose: Persist the map of players
	def __writePlayers(self):
		selfref_list = [1, 2, 3]
		selfref_list.append(selfref_list)
		output = open(self.pathToPlayers, 'wb')
		pickle.dump(self.players, output)
		pickle.dump(selfref_list, output, -1)
		output.close()

# Purpose: Prints top N players in desc order by rating.
# In:      N - number of players to print
def printTopN(N, players):
	
	if N > len(players):
		N = len(players)
	if N < 0:
		N = 1
	
	namePlayerTuples = players.items()
	namePlayerTuples.sort(key = lambda x : x[1].getRating(), reverse = True)

	i = 0
	for name, player in namePlayerTuples:
		if i >= N:
			break
		print i + 1
		printPlayer(name, player)
		i += 1

# Purpose: Prints in a cleaner way the name, rating, and deviation of a player
# In:      playerName - name of the player to print
#		   playerObj - the glicko2.Player() object to print rating and rd from
def printPlayer(playerName, playerObj):
	print "Player:\t" + playerName
	print playerObj		

def main():

	pathToMatches = "data/matches.txt"
	pathToPlayers = "data/players.pkl"
	
	# Will map names to glicko2.player()'s
	players = {}
	
	# Uncomment to construct all files from scratch and comment out the loadObj line
	players = RaterSetup(pathToPlayers, pathToMatches).getPlayerMap()
	#players = loadObj(pathToPlayers)

	printTopN(100, players)
	
if __name__ == "__main__":
	main()