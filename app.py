from flask import Flask, render_template, request, redirect, url_for, session
import language_tool_python
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Use free LanguageTool public API
tool = language_tool_python.LanguageToolPublicAPI('en-US')

# In-memory user data
users = {}

# Load user data from file
def load_users():
    global users
    try:
        with open('users.json', 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}

# Save user data to file
def save_users():
    with open('users.json', 'w') as f:
        json.dump(users, f)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    load_users()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['user'] = username
            return redirect(url_for('main'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    load_users()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            users[username] = password
            save_users()
            return redirect(url_for('login'))
        return render_template('signup.html', error="Username already exists")
    return render_template('signup.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
    if 'user' not in session:
        return redirect(url_for('login'))

    corrected_text = None
    corrections = []

    if request.method == 'POST':
        text = request.form['text']
        matches = tool.check(text)
        corrected_text = language_tool_python.utils.correct(text, matches)
        corrections = [{
            'error': m.context,  # ✅ FIXED: m.context is a string
            'message': m.message,
            'suggestions': m.replacements
        } for m in matches]

    return render_template('main.html', corrected_text=corrected_text, corrections=corrections)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
