from pydblite.pydblite import Base
from flask import Flask, render_template, jsonify, request, abort
import json
import sys
import operator
from datetime import datetime
from operator import itemgetter

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

KILL_COLORS = {
    DAN: '#008080',
    JUSTIN: '#DC143C',
    ALEX: '#f4c741',
    JASON: '#4286f4'
}

PLAYER_NAMES = {}
for k, v in PLAYER_IDS.items():
    PLAYER_NAMES[v] = k

WEAPON_MAP = {

    # Misc
    'PlayerMale_A_C': 'Melee',
    'PlayerFemale_A_C': 'Melee',
    'ProjGrenade_C': 'Grenade',
    'WeapCowbar_C': 'Crowbar',
    'ProjMolotov_DamageField_C': 'Molotov',
    'Buff_FireDOT_C': 'Molotov',
    'ProjMolotov_DamageFieldInWall_C': 'Molotov',
    'WeapPan_C': 'Pan',

    # ARs
    'WeapSCAR-L_C': 'SCAR-L',
    'WeapHK416_C': 'M4',
    'WeapAK47_C': 'AK47',
    'WeapM16A4_C': 'M16',
    'WeapGroza_C': 'Groza',
    'WeapAUG_C': 'AUG',

    # Snipers
    'WeapKar98k_C': 'Kar 98k',
    'WeapSKS_C': 'SKS',
    'WeapMini14_C': 'Mini 14',
    'WeapVSS_C': 'VSS',
    'WeapM24_C': 'M24',
    'WeapMK14_C': 'MK14',

    # SMGs
    'WeapThompson_C': 'Thompson',
    'WeapUMP_C': 'UMP',
    'WeapVector_C': 'Vector',
    'WeapUZI_C': 'Micro Uzi',

    # Shotguns
    'WeapBerreta686_C': 'S686',
    'WeapWinchester_C': 'S1987',
    'WeapSaiga12_C': 'S12k',

    # Pistols
    'WeapM9_C': 'M9',
    'WeapM1911_C': 'M1911',
    'WeapNagantM1895_C': 'R1895',
    'WeapG18_C': 'G18',

    'WeapDP28_C': 'DP28',
    'WeapM249_C': 'M249',
    'WeapCrossbow_1_C': 'Crossbow',

    # Vehicles
    'Buggy_A_03_C': 'Buggy',
    'Buggy_A_02_C': 'Buggy',
    'Dacia_A_02_v2_C': 'Dacia',
    'Dacia_A_01_v2_C': 'Dacia',
    'Dacia_A_03_v2_C': 'Dacia',
    'BP_Motorbike_04_C': 'Motorcycle',
    'BP_Motorbike_04_SideCar_C': 'Motorcycle',
    'Uaz_A_01_C': 'UAZ',
    'Uaz_C_01_C': 'UAZ',
    'Uaz_B_01_C': 'UAZ',
    'BP_PickupTruck_A_03_C': 'Pickup Truck',

    'BattleRoyaleModeController_Def_C': 'crap',
    'Buff_DecreaseBreathInApnea_C': 'crap'

}

MAPS = {
    'Erangel_Main': 'Erangel',
    'Desert_Main': 'Mirimar'
}

DB_DIR = 'stats/db/'


def create_matches():
    db = Base(DB_DIR + 'matches.pdl', save_to_file=True)
    db.create('match_key', 'player_id', mode="open")
    return db


def create_match_details():
    db = Base(DB_DIR + 'match_details.pdl', save_to_file=True)
    db.create('match_key', 'json', mode="open")
    return db


def create_seasons():
    db = Base(DB_DIR + 'seasons.pdl', save_to_file=True)
    db.create('player_id', 'season_id', 'json', mode="open")
    return db


def create_telemetry():
    db = Base(DB_DIR + 'telemetry.pdl', save_to_file=True)
    db.create('match_key', 'json', mode="open")
    return db


matches = create_matches()
match_details = create_match_details()
seasons = create_seasons()
telemetry = create_telemetry()


def summarize(details, player_name=None, game_type=None, limit=None, map_names=None):
    rounds = []
    summary = []
    for rec in details:
        attributes = rec['json']['data']['attributes']
        if game_type is not None and attributes['gameMode'] != game_type:
            continue
        if map_names is not None and len(map_names) > 0:
            if 'mapName' not in attributes.keys():
                if 'Erangel' not in map_names:
                    continue
            else:
                if MAPS[attributes['mapName']] not in map_names:
                    continue
        data_array = rec['json']['included']
        date = attributes['createdAt']
        rounds.append({'data': data_array, 'date': date})

    sorted_rounds = sorted(rounds, key=lambda x: x['date'], reverse=True)
    counter = 0

    for single_round in sorted_rounds:
        if limit and counter >= int(limit):
            break
        for data in single_round['data']:
            if data['type'] == 'participant':
                player_id = data['attributes']['stats']['playerId'][8:]

                if player_name is not None and player_id != PLAYER_IDS[player_name]:
                    continue
                if player_name is None and player_id not in PLAYER_IDS.values():
                    continue

                if limit is not None:
                    if player_name is None or player_id == PLAYER_IDS[player_name]:
                        counter += 1

                name = data['attributes']['stats']['name']
                kills = data['attributes']['stats']['kills']
                dmg = data['attributes']['stats']['damageDealt']
                survive = data['attributes']['stats']['timeSurvived']
                dbno = data['attributes']['stats']['DBNOs']
                revives = data['attributes']['stats']['revives']
                headshotKills = data['attributes']['stats']['headshotKills']
                assists = data['attributes']['stats']['assists']
                rideDistance = data['attributes']['stats']['rideDistance']
                walkDistance = data['attributes']['stats']['walkDistance']
                heals = data['attributes']['stats']['heals']
                boosts = data['attributes']['stats']['boosts']
                timeSurvived = data['attributes']['stats']['timeSurvived']
                longestKill = data['attributes']['stats']['longestKill']
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
                    p['headshotKills'] = p['headshotKills'] + headshotKills
                    p['assists'] = p['assists'] + assists
                    p['rideDistance'] = p['rideDistance'] + rideDistance
                    p['walkDistance'] = p['walkDistance'] + walkDistance
                    p['heals'] = p['heals'] + heals
                    p['boosts'] = p['boosts'] + boosts
                    p['timeSurvived'] = p['timeSurvived'] + timeSurvived
                    if longestKill > p['longestKill']:
                        p['longestKill'] = longestKill

                else:
                    summary.append({
                        'name': name,
                        'kills': kills,
                        'deaths': deaths,
                        'rounds': 1,
                        'dmg': dmg,
                        'survive': survive,
                        'dbno': dbno,
                        'revives': revives,
                        'headshotKills': headshotKills,
                        'assists': assists,
                        'rideDistance': rideDistance,
                        'walkDistance': walkDistance,
                        'heals': heals,
                        'boosts': boosts,
                        'timeSurvived': timeSurvived,
                        'longestKill': longestKill
                    })
    return summary


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/stats")
def get_stats():
    game_type = request.args.get('type')
    limit = request.args.get('limit')
    summary = summarize(match_details(), game_type=game_type, limit=limit)
    return jsonify(summary)


@app.route("/api/stats/<player_name>")
def get_player_stats(player_name):
    game_type = request.args.get('type')
    limit = request.args.get('limit')
    map_names = request.args.getlist('maps')
    summary = summarize(match_details(), player_name=player_name, game_type=game_type, limit=limit, map_names=map_names)
    return jsonify([]) if len(summary) == 0 else jsonify(summary[0])


@app.route("/api/match/<match_id>")
def get_single_match(match_id):
    results = match_details('match_key') == match_id
    if results:
        for rec in results:
            return jsonify(rec['json'])
    else:
        return jsonify([])


@app.route("/api/player/<player_name>")
def get_player(player_name):
    pid = PLAYER_IDS[player_name]
    results = []
    for rec in matches('player_id') == pid:
        date = None
        stats = {}
        team_count = 0
        for detail_rec in match_details(match_key=rec['match_key']):
            attributes = detail_rec['json']['data']['attributes']
            date = attributes['createdAt']
            game_mode = attributes['gameMode']
            map_title = 'Erangel' if 'mapName' not in attributes.keys() else MAPS[attributes['mapName']]
        if date:
            for data in detail_rec['json']['included']:
                if data['type'] == 'participant':
                    player_id = data['attributes']['stats']['playerId'][8:]
                    if player_id in PLAYER_IDS.values():
                        player_stats = data['attributes']['stats']
                        stats[data['attributes']['stats']['name']] = player_stats
                elif data['type'] == 'roster':
                    team_count += 1
            results.append(
                {
                    'key': rec['match_key'],
                    'date': date,
                    'stats': stats,
                    'teamCount': team_count,
                    'gameMode': game_mode,
                    'mapTitle': map_title
                }
            )

    return jsonify(results)


@app.route("/api/season/<player_name>")
def get_season_stats(player_name):
    p = PLAYER_IDS[player_name]
    results = []
    for rec in seasons('player_id') == p:
        results.append({'season_id': rec['season_id'], 'data': rec['json']})

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
        return jsonify([])


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


@app.route("/api/telemetry", methods=['POST'])
def insert_match_telemetry():
    data = request.get_json()

    if 'match_key' not in data or 'data' not in data:
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}

    m = data['match_key']
    json_data = data['data']

    if telemetry(match_key=m):
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}

    telemetry.insert(match_key=m, json=json_data)
    telemetry.commit()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/api/seasons", methods=['POST'])
def insert_season():
    data = request.get_json()

    if 'season_id' not in data or 'player_id' not in data or 'data' not in data:
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}

    season_id = data['season_id']
    player_id = data['player_id']
    json_data = data['data']

    rec = seasons(player_id=player_id, season_id=season_id)
    if rec:
        seasons.update(rec, json=json_data)
    else:
        seasons.insert(player_id=player_id, season_id=season_id, json=json_data)
    seasons.commit()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/api/all_matches")
def get_all_matches():
    result = []
    for rec in matches():
        result.append({'match_key': rec['match_key'], 'player_id': rec['player_id']})

    return jsonify(result)


@app.route("/api/all_telemetry")
def get_all_telemetry():
    result = []
    for rec in telemetry():
        result.append(rec['match_key'])

    return jsonify({'count': len(result), 'matches': result})


@app.route("/api/telemetry/<match_key>/events")
def get_telemetry_events(match_key):
    result = set()
    for rec in telemetry(match_key=match_key):
        for data in rec['json']:
            result.add(data['_T'])

    return jsonify(list(result))


@app.route("/api/telemetry/<match_key>/<num_results>")
def get_telemetry(match_key, num_results):
    event_type = request.args.get('type')
    page_parm = request.args.get('page')
    player_name = request.args.get('player')
    page = 0 if page_parm is None else int(page_parm)
    result = get_match_telemetry(match_key, int(num_results), event_type, page, player_name)
    return jsonify(result)


def get_match_telemetry(match_key=None, num_results=sys.maxsize, event_type=None, page=0, player_name=None):
    result = []
    skip_to = num_results * page
    row_count = 0
    records = telemetry() if match_key is None else telemetry(match_key=match_key)
    for rec in records:
        for data in rec['json']:
            if not event_match(player_name, event_type, data):
                continue
            row_count += 1
            if row_count <= skip_to:
                continue
            if len(result) < int(num_results):
                data['match_key'] = rec['match_key']
                result.append(data)
            else:
                break

    return result


def event_match(player_name, event_type, data):
    data_type = data['_T']
    if event_type and data_type != event_type:
        return False
    elif player_name:
        if data_type == 'LogPlayerAttack' and data['attacker']['name'] != player_name:
            return False
        elif data_type == 'LogPlayerPosition' and data['character']['name'] != player_name:
            return False
        elif data_type == 'LogPlayerTakeDamage' and data['attacker']['name'] != player_name:
            return False
    return True


@app.route("/api/all_details")
def get_all_details():
    result = []
    for rec in match_details():
        result.append(rec['match_key'])

    return jsonify({'count': len(result), 'matches': result})


@app.route("/api/match/dmg/<match_key>/<player_name>")
def get_damage_by_player(match_key, player_name):
    data = get_match_telemetry(match_key, player_name=player_name, event_type='LogPlayerTakeDamage')
    total = 0
    weapons = {}
    for event in data:
        damage = event['damage']
        weapon = event['damageCauserName']
        total += damage
        if weapon in weapons:
            weapons[weapon] += damage
        else:
            weapons[weapon] = damage

    return jsonify({'total_dmg': total, 'weapons': weapons})


@app.route("/api/match/kills/<match_key>/<player_name>")
def get_kills_by_player(match_key, player_name):
    kills = get_kills(match_key, player_name)
    return jsonify({'count': len(kills), 'kills': kills})


@app.route("/api/weapons")
def get_kills_by_weapon():
    player_name = request.args.get('name')
    result = []
    if player_name:
        weapons = get_player_kills_by_weapon(player_name)
        result = {'name': player_name, 'weapons': weapons}
    else:
        for p_name in PLAYER_IDS.keys():
            weapons = get_player_kills_by_weapon(p_name)
            result.append({'name': p_name, 'weapons': weapons})

    return jsonify(result)


def get_player_kills_by_weapon(player_name):
    data = get_match_telemetry(player_name=player_name, event_type='LogPlayerKill')
    weapons = {}
    result = []
    for event in data:
        killer = event['killer']['name']
        target = event['victim']['name']
        if killer != player_name or target == player_name:
            continue
        weapon = WEAPON_MAP.get(event['damageCauserName'], event['damageCauserName'])
        if weapon in ['crap', 'Melee']:
            damage_events = get_match_telemetry(event['match_key'], player_name=player_name, event_type='LogPlayerTakeDamage')
            weapon = find_murder_weapon(damage_events, event['victim']['name'])
        weapons[weapon] = weapons.get(weapon, 0) + 1

    for w_name, w_kills in weapons.items():
        result.append({'name': w_name, 'kills': w_kills})
    return result


def get_kills(match_key, player_name):
    kill_events = get_match_telemetry(match_key, player_name=player_name, event_type='LogPlayerKill')
    damage_events = get_match_telemetry(match_key, player_name=player_name, event_type='LogPlayerTakeDamage')
    kills = []
    match_date = None
    for detail_rec in match_details(match_key=match_key):
        match_date = datetime.strptime(detail_rec['json']['data']['attributes']['createdAt'], '%Y-%m-%dT%H:%M:%SZ')
    for event in kill_events:
        killer = event['killer']['name']
        target = event['victim']['name']
        if killer != player_name or target == player_name:
            continue
        weapon = WEAPON_MAP.get(event['damageCauserName'], event['damageCauserName'])
        time_str = event["_D"][:19] + 'Z'
        kill_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')
        time = kill_time - match_date
        if weapon == 'crap' or 'Melee':
            weapon = find_murder_weapon(damage_events, target)
        kills.append({'killer': killer, 'weapon': weapon, 'target': target, 'time': time.seconds})

    return kills


def find_murder_weapon(attack_events, target):
    filtered_attacks = [d for d in attack_events if d['victim']['name'] == target]
    sorted_attacks = sorted(filtered_attacks, key=itemgetter("_D"), reverse=True)
    weapon = sorted_attacks[0]['damageCauserName']
    for attack in sorted_attacks:
        if attack['victim']['health'] > 0:
            weapon = attack['damageCauserName']
            break
    return WEAPON_MAP.get(weapon, weapon)


@app.route("/api/dmg/types")
def get_damage_types():
    data = get_match_telemetry(event_type='LogPlayerTakeDamage')
    result = set()

    for event in data:
        result.add(event['damageReason'])

    return jsonify(list(result))


@app.route("/api/kills/<match_key>")
def get_damage_caused(match_key):
    result = {}
    if telemetry(match_key=match_key):
        all_kills = []
        for player_name, player_id in PLAYER_IDS.items():
            if not matches(match_key=match_key, player_id=player_id):
                continue
            kills = get_kills(match_key, PLAYER_NAMES[player_id])
            result[player_name] = {'kills': kills, 'color': KILL_COLORS[player_name] }
            all_kills.append(kills)

        for player_name, player_id in PLAYER_IDS.items():
            if not matches(match_key=match_key, player_id=player_id):
                continue
            player_dmg = {}
            match_date = None
            for detail_rec in match_details(match_key=match_key):
                match_date = datetime.strptime(detail_rec['json']['data']['attributes']['createdAt'],
                                               '%Y-%m-%dT%H:%M:%SZ')
            data = get_match_telemetry(match_key, player_name=player_name, event_type='LogPlayerTakeDamage')
            for event in data:
                weapon = event['damageCauserName']
                event['weapon'] = WEAPON_MAP.get(weapon, weapon)
                target = event['victim']['name']
                time_str = event["_D"][:19] + 'Z'
                kill_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')
                time = kill_time - match_date
                event['time'] = time.seconds
                if target not in player_dmg.keys():
                    killer = get_killer(target, all_kills)
                    player_dmg[target] = {
                        'target': target, 'attacks': [], 'time': time.seconds, 'total_dmg': 0, 'killer': killer
                    }
                player_dmg[target]['attacks'].append(event)
                player_dmg[target]['total_dmg'] = player_dmg[target]['total_dmg'] + event['damage']
                player_dmg[target]['time'] = time.seconds

            if 'dmg' not in result[player_name].keys():
                result[player_name]['dmg'] = []

            for attacks in player_dmg.values():
                result[player_name]['dmg'].append(attacks)

    return jsonify(result)


def get_killer(target, kills):
    for player_kills in kills:
        for kill in player_kills:
            if kill['target'] == target:
                return KILL_COLORS[kill['killer']]
    return 0


@app.route("/api/hits")
def get_dmg_by_loc():
    data = get_match_telemetry(event_type='LogPlayerTakeDamage')
    results = {}

    for p in PLAYER_IDS.keys():
        results[p] = {'hits': 0, 'shots': 0}

    for event in data:
        attacker = event['attacker']['name']
        shot_loc = event['damageReason']
        if event['damageTypeCategory'] == "Damage_Gun" and event['attacker']['name'] in PLAYER_IDS.keys():
            if shot_loc in results[attacker].keys():
                results[attacker][shot_loc] += 1
            else:
                results[attacker][shot_loc] = 1
            results[attacker]['hits'] += 1

    data = get_match_telemetry(event_type='LogPlayerAttack')
    for event in data:
        attacker = event['attacker']['name']
        weapon = event['weapon']['itemId']
        if event['AttackType'] == 'weapon' and event['attacker']['name'] in PLAYER_IDS.keys():
            if weapon in [
                "Item_Weapon_FlashBang_C",
                "Item_Weapon_Grenade_C",
                "Item_Weapon_Molotov_C",
                "Item_Weapon_SmokeBomb_C",
                "Item_Weapon_Sickle_C",
                "Item_Weapon_Pan_C"
            ]:
                continue

            weapon = WEAPON_MAP.get(weapon, weapon)

            if weapon in results[attacker].keys():
                results[attacker][weapon] += 1
            else:
                results[attacker][weapon] = 1
            results[attacker]['shots'] += 1

    for player in results.keys():
        results[player]['percent'] = results[player]['hits'] / results[player]['shots'] * 100

    return jsonify(results)


@app.route("/api/repeats")
def get_repeat_kills():
    names = {}
    for rec in telemetry():
        for data in rec['json']:
            data_type = data['_T']
            if data_type == 'LogPlayerKill' and data['victim']['name'] not in PLAYER_IDS.keys():
                victim = data['victim']['name']
                names[victim] = names.get(victim, 0) + 1

    sorted_names = sorted(names.items(), key=operator.itemgetter(1))
    return jsonify(sorted_names)


@app.route("/api/repeats/<player_name>")
def get_repeat_kills_for_player(player_name):
    result = []
    for rec in telemetry():
        for data in rec['json']:
            data_type = data['_T']
            if data_type == 'LogPlayerKill' and data['victim']['name'] == player_name:
                result.append(data)

    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

