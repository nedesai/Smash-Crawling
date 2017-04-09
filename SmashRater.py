import pickle
import glicko2
import re

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
		
def main():
	pathToMatches = "data/matches.txt"
	pathToPlayers = "data/players.pkl"
	# Initial data construction
	players = initPlayerDataWrite(pathToMatches, pathToPlayers)
	
	#players = loadObj(pathToPlayerData)
	for playerName in players:
		print "Player:\t" + playerName
		print players[playerName]
		print '\n'
	
	
if __name__ == "__main__":
	main()