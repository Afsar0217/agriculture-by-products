from flask import Flask, render_template, request, jsonify
import os, json, requests
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Load byproduct DB
with open('data/byproducts.json') as f:
    BYPRODUCT_DB = json.load(f)

# Load sample input/output data
with open('static/sample_inputs.json') as f:
    SAMPLE_INPUTS = json.load(f)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        file = request.files['image']
        process = request.form['process']
        if file:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)

            if 'orange' in filename.lower():
                product_key = "orange_peel"
            elif 'banana' in filename.lower():
                product_key = "banana_peel"
            else:
                product_key = None

            if product_key and process in BYPRODUCT_DB.get(product_key, {}):
                result = BYPRODUCT_DB[product_key][process]
            else:
                result = ["No data available for selected inputs."]
    return render_template('index.html', result=result, samples=SAMPLE_INPUTS)

@app.route('/info')
def get_info():
    name = request.args.get('name', '')
    data = fetch_wikipedia_summary(name)
    return jsonify(data)

def fetch_wikipedia_summary(query):
    try:
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'format': 'json'
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, params=params, headers=headers)
        data = response.json()

        if not data['query']['search']:
            return {"info": "No information found.", "image": None}

        title = data['query']['search'][0]['title']
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        summary_resp = requests.get(summary_url, headers=headers)
        summary_data = summary_resp.json()

        info = summary_data.get('extract', 'No summary available.')
        image = summary_data.get('thumbnail', {}).get('source', None)

        return {"info": info, "image": image}

    except Exception as e:
        return {"info": "Error fetching info.", "image": None}

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
