from flask import Flask, render_template, json, jsonify, request
import re
import collections

DEFAULT_SETTINGS = {
    'mode': 'donations',  # [donations, closed, custom]
    'customMessage': 'Nothing to see, move on',
    'goalMessage': 'Time Extension',
    'showProgress': False,   # Show progress bar under totals
    'showGoalAlerts': False, # Show GOAL, etc when goal met
    'incrementHoursBy': .5,
    'amounts': [50, 150, 300, 400, 600, 800, 1000, 1500],
    'defaultStatus': {
        'currentHours': 1.5,
        'goalHours': 2,
        'amount': 50,
    }
}

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/donations')
def donations():
    return render_template('donations.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/api/settings', methods=['GET'])
def get_settings():
    return jsonify(_load_settings())

@app.route('/api/settings', methods=['PUT'])
def update_settings():
    update = request.get_json()
    settings = _load_settings()
    _deepmerge(settings, update)
    _save_settings(settings)

    return jsonify(settings)

@app.route('/api/goal', methods=['PUT'])
def update_goal():
    update = request.get_json()
    session = _load_session()
    _deepmerge(session, update)
    _save_session(session)

    return jsonify(session)

@app.route('/api/goal/extend', methods=['PUT'])
def extend_session():
    settings = _load_settings();
    session = _load_session()

    session['goalHours'] = float(session['goalHours']) + float(settings['incrementHoursBy'])

    _save_session(session)

    return jsonify(session)

@app.route('/api/goal/reset', methods=['PUT'])
def reset_session_status():
    _save_session(DEFAULT_SETTINGS['defaultStatus'])

    return jsonify(_load_session())

@app.route('/api/status', methods=['GET'])
def get_status():
    # Read the bits and donations files
    # format numbers as $$ values
    donations = _load_donations()
    settings = _load_settings()
    goal = _load_session()

    response = {
        'donations': donations,
        'goal': goal,
        'settings': settings,
        'display': {
            'percentage': 0,
            'total': 0,
            'hours': 0,
            'amount': 0,
        }
    }

    # Fill in current (reached) goal
    if donations['total'] >= 0:
        response['display']['percentage'] = int(100 * donations['total'] / goal['amount'])
        response['display']['total'] = int(donations['total'])
        response['display']['hours'] = goal['goalHours']
        response['display']['amount'] = goal['amount']

    return jsonify(response)

def _load_session():
    # Load current status
    try:
        with open('session_halodono_status.json') as f:
            status = json.load(f)
    except IOError as e:
        # No session info
        status = DEFAULT_SETTINGS['defaultStatus']

    return status

def _save_session(status):
    # Save settings file
    try:
        with open('session_halodono_status.json', 'w+') as f:
            json.dump(status, f)
    except IOError as e:
        print("wat? {}".format(e))

def _load_settings():
    # Load settings file
    try:
        with open('halodono.json', 'r') as f:
            settings = json.load(f)
    except IOError as e:
        # No settings file
        settings = DEFAULT_SETTINGS

    return settings

def _save_settings(settings):
    # Save settings file
    try:
        with open('halodono.json', 'w+') as f:
            json.dump(settings, f)
    except IOError as e:
        print("wat? {}".format(e))

def _load_donations():
    money = 0.0
    cheers = 0

    try:
        with open('session_donation_amount.txt', 'r') as f:
            line = f.readline()

        # Extract donations as float
        m = re.search(r'\d+(\.\d+)?', line)

        if m:
            money = float(m[0])
    except IOError as e:
        # Error
        print("Problem opening donations file: {}".format(e))
        print(e)

    try:
        with open('session_cheer_amount.txt', 'r') as f:
            line = f.readline()

        # Extract cheers as int
        m = re.search(r'\d+', line)
    
        if m:
            cheers = int(m[0])
    except IOError as e:
        # Error
        print("Problem opening cheers file: {}".format(e))
        print(e)

    total = money + cheers / 100

    return {
        'money': money,
        'cheers': cheers,
        'total': total,
    }

def _deepmerge(current, update):
    for k, v in update.items():
        if isinstance(v, collections.Mapping):
            current = _deepmerge(current.get(k, {}), v)
        else:
            current[k] = v

    return current
