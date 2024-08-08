import os
from flask import Flask, render_template, request, jsonify
import requests
import markdown
from flask_mde import Mde

if os.path.exists('env.py'):
    import env

app = Flask(__name__)
mde = Mde(app)

# Replace with your OpenAI API key
OPENAI_API_KEY = os.environ['OpenAI']

# In-memory cache for markdown content
markdown_cache = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    prompt = data['prompt']
    extra_instructions = data['extra_instructions']
    response = call_openai_api(prompt, extra_instructions)
    return jsonify({'response': response})


@app.route('/save_markdown', methods=['POST'])
def save_markdown():
    markdown_content = request.form['markdown_content']
    markdown_cache.append(markdown_content)
    markdown_payload = ""
    for item in markdown_cache:
        markdown_payload += '\n' + item
    html_content = markdown.markdown(markdown_payload)
    return jsonify({'html_content': html_content})


@app.route('/get_cached_markdown', methods=['GET'])
def get_cached_markdown():
    concatenated_markdown = '\n'.join(markdown_cache)
    return jsonify({'cached_markdown': concatenated_markdown})

def get_markdown_internal():
    markdown_list = markdown_cache
    markdown_payload = ""
    for item in markdown_list:
        markdown_payload += '\n' + item
    return markdown_payload

def call_openai_api(prompt, extra_instructions):
    markdown = get_markdown_internal()
    print(markdown)
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': f'{prompt}\n\n{extra_instructions}'}
        ]
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
    return 'Error contacting OpenAI API'


if __name__ == '__main__':
    app.run(debug=True)
