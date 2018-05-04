from pydblite.pydblite import Base
from flask import Flask, render_template, jsonify, request, abort
import json

app = Flask(__name__)

DAN = 'BigGoof20'
ALEX = 'UCBananaboy'
JASON = 'Honkieharris'
JUSTIN = 'WTJ22'

PLAYER_IDS = {
    JUSTIN: "80c75a49a4e84eccadd3e2db4c1fcfc4",
    ALEX: "e281626d08ee461fb6edbc7477e188c3",
    JASON: "00712b32939442e6a6b8b118e006d099",
    DAN: "9606b28ee9cc4354befc293713d3d8c0",
}


def create_matches():
    db = Base('stats/db/matches.pdl', save_to_file=True)
    db.create('match_key', 'player_id', mode="open")
    return db


def create_match_details():
    db = Base('stats/db/match_details.pdl', save_to_file=True)
    db.create('match_key', 'json', mode="open")
    return db


matches = create_matches()
match_details = create_match_details()


def summarize(details, player_name=None):
    summary = []
    for rec in details:
        data_array = rec['json']['included']
        for data in data_array:
            if data['type'] == 'participant':
                player_id = data['attributes']['stats']['playerId'][8:]

                if player_name is not None and player_id != PLAYER_IDS[player_name]:
                    continue
                if player_name is None and player_id not in PLAYER_IDS.values():
                    continue

                name = data['attributes']['stats']['name']
                kills = data['attributes']['stats']['kills']
                dmg = data['attributes']['stats']['damageDealt']
                survive = data['attributes']['stats']['timeSurvived']
                dbno = data['attributes']['stats']['DBNOs']
                revives = data['attributes']['stats']['revives']
                deaths = 0 if data['attributes']['stats']['deathType'] == 'alive' else 1
                p = next((item for item in summary if item["name"] == name), None)
                if p:
                    p['kills'] = p['kills'] + kills
                    p['deaths'] = p['deaths'] + deaths
                    p['rounds'] = p['rounds'] + 1
                    p['dmg'] = p['dmg'] + dmg
                    p['survive'] = p['survive'] + survive
                    p['dbno'] = p['dbno'] + dbno
                    p['revives'] = p['revives'] + revives

                else:
                    summary.append({
                        'name': name,
                        'kills': kills,
                        'deaths': deaths,
                        'rounds': 1,
                        'dmg': dmg,
                        'survive': survive,
                        'dbno': dbno,
                        'revives': revives
                    })
    return summary


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/stats")
def get_stats():
    summary = summarize(match_details())
    return jsonify(summary)


@app.route("/api/stats/<player_name>")
def get_player_stats(player_name):
    summary = summarize(match_details(), player_name=player_name)
    return jsonify(summary[0])


@app.route("/api/match/<match_id>")
def get_single_match(match_id):
    results = match_details('match_key') == match_id
    if results:
        for rec in results:
            return jsonify(rec['json'])
    else:
        return []


@app.route("/api/player/<player_name>")
def get_player(player_name):
    pid = PLAYER_IDS[player_name]
    results = []
    for rec in matches('player_id') == pid:
        date = None
        stats = []
        for detail_rec in match_details('match_key') == rec['match_key']:
            date = detail_rec['json']['data']['attributes']['createdAt']
        if date:
            for data in detail_rec['json']['included']:
                if data['type'] == 'participant':
                    player_id = data['attributes']['stats']['playerId'][8:]
                    if player_id in PLAYER_IDS.values():
                        stats.append(data['attributes']['stats'])
            results.append({'key': rec['match_key'], 'date': date, 'stats': stats})

    return jsonify(results)


@app.route("/api/match/<match_id>/<player_name>")
def get_player_match(match_id, player_name):
    results = match_details('match_key') == match_id
    if results:
        for rec in results:
            data_array = rec['json']['included']
            for data in data_array:
                if data['type'] == 'participant':
                    player_id = data['attributes']['stats']['playerId'][8:]
                    if player_id == PLAYER_IDS[player_name]:
                        return jsonify(data['attributes']['stats'])
    else:
        return []


@app.route("/api/match", methods=['POST'])
def insert_match():
    data = request.get_json()

    if 'match_key' not in data or 'player_id' not in data:
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}

    m = data['match_key']
    pid = data['player_id']

    if matches(match_key=m, player_id=pid):
        return json.dumps({'success': False}), 409, {'ContentType': 'application/json'}

    matches.insert(match_key=m, player_id=pid)
    matches.commit()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/api/match_details", methods=['POST'])
def insert_match_details():
    data = request.get_json()

    if 'match_key' not in data or 'data' not in data:
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}

    m = data['match_key']
    json_data = data['data']

    if match_details(match_key=m):
        return json.dumps({'success': False}), 409, {'ContentType': 'application/json'}

    match_details.insert(match_key=m, json=json_data)
    match_details.commit()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/api/all_matches")
def get_all_matches():
    result = []
    for rec in matches():
        result.append({'match_key': rec['match_key'], 'player_id': rec['player_id']})

    return jsonify(result)


@app.route("/api/all_details")
def get_all_details():
    result = []
    for rec in match_details():
        result.append(rec['match_key'])

    return jsonify({'count': len(result), 'matches': result})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

