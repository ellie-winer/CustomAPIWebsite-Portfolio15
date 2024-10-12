from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

API_URL = 'https://api.football-data.org/v4/competitions/CL/matches'
API_KEY = '0309c305716e4b089916acb303aece7f'


@app.route('/', methods=['GET'])
def home():
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(API_URL, headers=headers)

    matches_data = []

    if response.status_code == 200:
        matches_data = response.json().get('matches', [])
    else:
        matches_data = {'error': 'Failed to fetch match data'}

    matches_data.sort(key=lambda x: x['season']['startDate'])

    filtered_matches_data = [
        match for match in matches_data
        if match.get('homeTeam', {}).get('name') and
           match.get('awayTeam', {}).get('name') and
           match['homeTeam']['name'].lower() != "none" and
           match['awayTeam']['name'].lower() != "none"
    ]

    return render_template('index.html', matches=filtered_matches_data)


@app.route('/search', methods=['POST'])
def search():
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(API_URL, headers=headers)
    matches_data = []

    if response.status_code == 200:
        matches_data = response.json().get('matches', [])
    else:
        matches_data = {'error': 'Failed to fetch match data'}

    team_query = request.form.get('team', '').lower()
    matchday_query = request.form.get('matchday')

    filtered_matches = []

    if not team_query and not matchday_query:
        return redirect(url_for('home'))

    for match in matches_data:
        home_team = match.get('homeTeam', {}).get('name')
        away_team = match.get('awayTeam', {}).get('name')
        matchday_value = match.get('matchday')

        home_team_lower = home_team.lower() if home_team else ''
        away_team_lower = away_team.lower() if away_team else ''

        if (team_query and (team_query in home_team_lower or team_query in away_team_lower)) or \
           (matchday_query and matchday_value == int(matchday_query)):
            filtered_matches.append(match)

    return render_template('index.html', matches=filtered_matches, team_query=team_query, matchday_query=matchday_query)



if __name__ == '__main__':
    app.run(debug=True, port=5002)
