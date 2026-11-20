"""FoodShare: simple Flask + MongoDB CRUD app; HTML and CSS in one file."""
import os
from flask import Flask, request, redirect, render_template_string, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'),
                     serverSelectionTimeoutMS=2500)
db = client['FoodShareDB']

# Collection: {field: input type}. All four collections support CRUD.
FIELDS = {
    'donors': {'name': 'text', 'type': 'text', 'phone': 'text', 'city': 'text'},
    'receivers': {'name': 'text', 'type': 'text', 'peopleServed': 'number', 'phone': 'text'},
    'food_listings': {'donorId': 'text', 'item': 'text', 'category': 'text',
                      'quantityKg': 'number', 'servings': 'number', 'status': 'text'},
    'pickups': {'listingId': 'text', 'receiverId': 'text', 'volunteer': 'text',
                'status': 'text', 'servingsDelivered': 'number'},
}
PREFIX = {'donors': 'D', 'receivers': 'R', 'food_listings': 'L', 'pickups': 'P'}

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FoodShare - MongoDB CRUD</title>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; background: #f3f7f4; color: #1c362c; font: 16px Arial, sans-serif; }
    header { background: #14583c; color: white; padding: 23px 5%; }
    header h1 { margin: 0 0 5px; }
    nav { background: #e5f1e9; padding: 15px 5%; display: flex; flex-wrap: wrap; gap: 10px; }
    nav a { text-decoration: none; background: white; color: #14583c; padding: 10px 15px; border-radius: 7px; font-weight: bold; }
    nav a.active { background: #14583c; color: white; }
    main { max-width: 1100px; margin: 25px auto; padding: 0 18px; }
    .panel { background: white; border-radius: 12px; padding: 23px; margin-bottom: 20px; box-shadow: 0 2px 12px #193c2512; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; }
    .stat { background: #edf7ef; border-radius: 10px; padding: 20px; }
    .stat strong { font-size: 30px; display: block; margin-top: 7px; }
    label { display: block; font-weight: bold; margin: 14px 0 5px; }
    input { width: 100%; padding: 12px; border: 1px solid #cbd8cd; border-radius: 7px; font: inherit; }
    button, .btn { display: inline-block; background: #168454; color: white; border: 0; border-radius: 7px; padding: 11px 16px; text-decoration: none; cursor: pointer; font: inherit; }
    .danger { background: #b53b35; }
    .secondary { background: #547769; }
    .actions { display: flex; gap: 7px; align-items: center; flex-wrap: wrap; }
    .actions form { margin: 0; }
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; min-width: 560px; }
    th, td { padding: 12px; border-bottom: 1px solid #e1eae3; text-align: left; }
    th { background: #edf7ef; }
    .notice { background: #fff3ce; padding: 16px; border-radius: 8px; }
  </style>
</head>
<body>
  <header>
    <h1>FoodShare</h1>
    <div>Community Food Surplus Redistribution System</div>
  </header>
  <nav>
    <a href="/" class="{{ 'active' if not section else '' }}">Dashboard</a>
    {% for item in collections %}
      <a class="{{ 'active' if section == item else '' }}" href="{{ url_for('records', section=item) }}">{{ item.replace('_',' ').title() }}</a>
    {% endfor %}
  </nav>
  <main>
    {% if error %}
      <div class="panel notice"><h2>MongoDB connection error</h2>
        <p>MongoDB Server must be installed and running on localhost:27017.</p>
        <code>{{ error }}</code>
      </div>
    {% elif not section %}
      <div class="panel"><h2>Dashboard</h2><p>Choose a section to add, view, edit or delete data.</p>
        <div class="grid">
          {% for name, count in counts.items() %}
            <a class="stat" href="{{ url_for('records',section=name) }}" style="color:inherit;text-decoration:none">
              {{ name.replace('_',' ').title() }} <strong>{{ count }}</strong>
            </a>
          {% endfor %}
        </div>
      </div>
    {% else %}
      <div class="panel">
        <h2>{{ 'Edit' if editing else 'Add' }} {{ section.replace('_',' ').title() }}</h2>
        <form method="post" action="{{ url_for('save', section=section, record_id=editing or 'new') }}">
          <div class="grid">
            {% for field, kind in fields.items() %}
              <div><label for="{{field}}">{{field}}</label>
                <input id="{{field}}" name="{{field}}" type="{{kind}}" step="any"
                       value="{{ current.get(field, '') }}" required></div>
            {% endfor %}
          </div>
          <p><button type="submit">{{ 'Save Changes' if editing else 'Add Record' }}</button>
          {% if editing %}<a class="btn secondary" href="{{ url_for('records',section=section) }}">Cancel</a>{% endif %}</p>
        </form>
      </div>
      <div class="panel"><h2>All Records ({{ rows|length }})</h2>
        <div class="table-wrap"><table><thead><tr><th>ID</th>
          {% for field in fields %}<th>{{field}}</th>{% endfor %}<th>Actions</th></tr></thead>
          <tbody>
          {% for row in rows %}<tr>
            <td>{{row['_id']}}</td>
            {% for field in fields %}<td>{{row.get(field, '')}}</td>{% endfor %}
            <td><div class="actions">
              <a class="btn secondary" href="{{ url_for('records',section=section,edit=row['_id']) }}">Edit</a>
              <form method="post" action="{{ url_for('delete',section=section,record_id=row['_id']) }}"
                    onsubmit="return confirm('Delete this record?')">
                <button class="danger">Delete</button>
              </form>
            </div></td>
          </tr>{% else %}<tr><td colspan="10">No records yet. Use the form above.</td></tr>{% endfor %}
          </tbody></table></div>
      </div>
    {% endif %}
  </main>
</body>
</html>"""


def show(section=None, error=None, edit=None):
    rows, current, counts = [], {}, {}
    fields = FIELDS.get(section, {})
    if not error:
        try:
            client.admin.command('ping')
            if section:
                rows = list(db[section].find().sort('_id', 1))
                current = db[section].find_one({'_id': edit}) or {} if edit else {}
            else:
                counts = {name: db[name].count_documents({}) for name in FIELDS}
        except PyMongoError as exc:
            error = str(exc)
    return render_template_string(PAGE, collections=FIELDS, section=section,
                                  fields=fields, rows=rows, current=current,
                                  counts=counts, editing=edit, error=error)


@app.get('/')
def home():
    return show()


@app.get('/<section>')
def records(section):
    if section not in FIELDS:
        return 'Page not found', 404
    return show(section, edit=request.args.get('edit'))


@app.post('/<section>/save/<record_id>')
def save(section, record_id):
    if section not in FIELDS:
        return 'Page not found', 404
    data = {}
    for field, kind in FIELDS[section].items():
        raw = request.form.get(field, '').strip()
        if not raw:
            return 'Every field is required', 400
        try:
            data[field] = float(raw) if kind == 'number' and field == 'quantityKg' else (int(raw) if kind == 'number' else raw)
        except ValueError:
            return 'Invalid number: ' + field, 400
    try:
        if record_id == 'new':
            # Small classroom project: generate readable IDs D1, R1, L1, P1.
            n = 1
            while db[section].find_one({'_id': f'{PREFIX[section]}{n}'}, {'_id': 1}):
                n += 1
            data['_id'] = f'{PREFIX[section]}{n}'
            db[section].insert_one(data)
        else:
            db[section].update_one({'_id': record_id}, {'$set': data})
    except PyMongoError as exc:
        return show(section, error=str(exc)), 503
    return redirect(url_for('records', section=section))


@app.post('/<section>/delete/<record_id>')
def delete(section, record_id):
    if section not in FIELDS:
        return 'Page not found', 404
    try:
        db[section].delete_one({'_id': record_id})
    except PyMongoError as exc:
        return show(section, error=str(exc)), 503
    return redirect(url_for('records', section=section))


if __name__ == '__main__':
    print('Open: http://127.0.0.1:5000')
    app.run(host='127.0.0.1', port=5000, debug=False)
