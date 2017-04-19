# Smash-Crawler

Smash-Crawler is a Python program with the goal of gathering data from challonge.com and smash.gg to objectify rankings for competitive Super Smash Bros. Melee players in Michigan. Specific tournaments under the domain of michigansmash.challonge.com and smash.gg were selected for this prototype. 

## Usage

* All necessary files are included in this repository
* Download repo and run with "python SmashRater.py"
* Top 100 ranked players in this state will be printed to the console

## Software/Data

* https://api.challonge.com/v1
* https://help.smash.gg/hc/en-us/articles/217471947-API-Access
* http://michigansmash.challonge.com/
* https://smash.gg/tournaments?per_page=100&filter=%7B%22upcoming%22%3Afalse%2C%22countryCode%22%3A%22US%22%2C%22addrState%22%3A%22MI%22%2C%22past%22%3Atrue%7D&page=1


## Authors

* **Daniel Faghihnia**
* **Eric Kwon**
* **Neeral Desai**
* **Steven Olthoff**

## Acknowledgments

* SmashGG API
* Challonge API
* Mark Glickman for glicko2