from pydblite.pydblite import Base
from flask import Flask, render_template, jsonify


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
    db = Base('db/matches.pdl', save_to_file=True)
    db.create('match_key', 'player_id', mode="open")
    return db


def create_match_details():
    db = Base('db/match_details.pdl', save_to_file=True)
    db.create('match_key', 'json', mode="open")
    return db


matches = create_matches()
match_details = create_match_details()


def summarize(details):
    summary = []
    for rec in details:
        data_array = rec['json']['included']
        for data in data_array:
            if data['type'] == 'participant':
                player_id = data['attributes']['stats']['playerId'][8:]
                if player_id in PLAYER_IDS.values():
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
