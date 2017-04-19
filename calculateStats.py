
#this function will output precision at each iteration for top 20 plaer list we generated
#and will also generate a MAP score for seeing how good our precision is for this list.
def calculatePrecision():
	#this is the numerator for the precision value from 1 to 20 and represents
	#the number of players that are in the correct position on the ranking
	correctSpots = 0.0
	#this is a list of the precisions for each of the relevant documents that we find in our ranking comparison.
	precisionAtKValues = []
	for i in range(0,20):
		if (top20PlayersControl[i] == top20PlayersGenerated[i]):
			correctSpots += 1
			#must calculate current precision for the precisionAtK list
			currentPrecision = correctSpots / (i + 1)
			precisionAtKValues.append(currentPrecision)
		#calcuate precision for current iteration, even if non relevant player is found
		currentPrecision = correctSpots / (i + 1)
		print "Precision for iteration",i+1,"is",currentPrecision
	#this is a value used for MAP calculation.
	precisionSum = 0
	for score in precisionAtKValues:
		precisionSum += score
	#map score that will be returned to the main function
	MAPScore = len(precisionAtKValues) * precisionSum

	return MAPScore

#this function will output a list of relevant players that will be used as the set of players
#that will have pairs generated between the two player lists for the kendall tau calculation
#This function also outputs the recall at every iteration from 1 to 20 for the top 20 player list we generated.
def calculateRecall():
	#this value keeps track of how many players we have found who should exist in the top20
	correctPlayers = 0.0
	relevantPlayers = []
	for i in range(0,20):
		#if a player from our calculated list exists in the top 20 control, then increase recall
		if (top20PlayersGenerated[i] in top20PlayersControl):
			correctPlayers += 1
			relevantPlayers.append(top20PlayersGenerated[i])
		#calcuate recall for current iteration, even if non relevant player is found
		currentRecall = correctPlayers / (i + 1)
		print "Recall for iteration",i + 1,"is",currentRecall

	#returns our list of relevant players that exist in both top 20 lists.
	return relevantPlayers

#this function will generate the pairs that will be used for kendall tau
# Function Parameters: 
# rankingList: list that contains the top 20 players
# relevantPlayers: the list of players who are relevant of the 20 names generated
# We only care about pairs between the relevant player names because that is how we
# will calculate an accurate kendall tau distance between our generated and control top 20 list.
def generatePairs(rankingList, relevantPlayers):
	#need to generate pairs for every entity between the two lists.
	pairs = []
	for i in range(0,20):
		#the player who is the first index of the pair
		if rankingList[i] in relevantPlayers: 
			entryOne = rankingList[i]
			#now iterate through and generate a list of pairs for this ranking
			for j in range(i+1,20):
				if rankingList[j] in relevantPlayers:
					#the player who is the second index of the pair
					entryTwo = rankingList[j]
					#separate the 2 player names by a comma so we can distinguish who is who
					pair = entryOne + "," + entryTwo
					pairs.append(pair)

	return pairs

#this function will calculate the kendall tau score between 2 lists of pairs.
#each of these pairs holds two names of a top 20 player from our top 20 lists.
def calculateKendallTau(listControl, listGenerated):
	#the amount of pairs that match between the two lists
	agreements = 0.0
	#the amount of pairs that disagree between the two lists
	disagreements = 0.0

	for pair in listControl:
		if pair in listGenerated:
			agreements += 1
		else:
			disagreements += 1

	kendallTauScore = (agreements - disagreements) / (agreements + disagreements)
	return kendallTauScore

#this function removes spaces and lowercases names so there are not player duplicates
def cleanName(playerName):
	#get rid of spaces in names
	nameCleaned = playerName.replace(" ", "")
	#get rid of tabs in names
	nameCleaned = nameCleaned.replace("\t", "")
	#lowercase the name
	nameCleaned = nameCleaned.lower()
	return nameCleaned


#this is the file that contains the 20 names we will use as our baseline for
#comparing the ranking we generate to see how accurate our results are.
top20PlayersControl = []
top20PlayersGenerated = []
with open("top20Baseline.txt", "r") as controlRankingFile:
	for name in controlRankingFile:
		#sanitize name input
		cleanedName = cleanName(name)
		top20PlayersControl.append(cleanedName)

with open("top20Calculated.txt", "r") as generatedRankingFile:
	for name in generatedRankingFile:
		cleanedName = cleanName(name)
		top20PlayersGenerated.append(cleanedName)

#calculate the MAP for our generated ranking
meanAveragePrecisionScore = calculatePrecision()
#output the recall at each iteration and get the recalled players as a list
relevantPlayerRecallList = calculateRecall()
#the number of players out of 20 that were recalled
totalRecalled = len(relevantPlayerRecallList)
#give us the list of pairs for the control list of top 20
top20ControlList = generatePairs(top20PlayersControl, relevantPlayerRecallList)
#give us the list of pairs for the generated list of top 20
top20GeneratedList = generatePairs(top20PlayersGenerated, relevantPlayerRecallList)

#now that we have the pairs we can calculate the kendall tau score between these pairs.
kendallTauValue = calculateKendallTau(top20ControlList, top20GeneratedList)

print "Mean Average Precision Score:",meanAveragePrecisionScore
print "Total amount of relevant players recalled out of 20",totalRecalled
print "Kendall Tau Distance between the two lists",kendallTauValue