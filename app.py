import requests
import json
from flask import Flask, render_template, request, session
from flask_session import Session
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

API_KEY = os.getenv('OPENAI_API_KEY')
API_ENDPOINT = "https://api.openai.com/v1/chat/completions"


def generate_chat_completion(messages, model="gpt-4", temperature=0.5, max_tokens=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    if max_tokens is not None:
        data["max_tokens"] = max_tokens

    response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        system_content = request.form['system_content']
        user_content = request.form['user_content']
        temperature = float(request.form['temperature'])
        max_tokens = int(request.form['max_tokens'])

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]

        response_text = generate_chat_completion(messages, temperature=temperature, max_tokens=max_tokens)

        if 'history' not in session:
            session['history'] = []

        session['history'].append({
            'user_content': user_content,
            'response_text': response_text,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })

        session['system_content'] = system_content
        session.modified = True

        # Reverse the history for display
        reversed_history = list(reversed(session['history']))

        return render_template('index.html', response_text=response_text, user_content=user_content, history=reversed_history, system_content=system_content, temperature=temperature, max_tokens=max_tokens)

    # Reverse the history for display
    reversed_history = list(reversed(session.get('history', [])))

    return render_template('index.html', history=reversed_history, system_content=session.get('system_content', 'You are a helpful assistant.'), temperature=0.5, max_tokens=2050)


if __name__ == '__main__':
    app.run(debug=False, port=5001)