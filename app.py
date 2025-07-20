import sqlite3
from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Set a secret key for session management

# Initialize SQLite database and create tables if they don't exist
def init_db():
    conn = sqlite3.connect('adherence_data.db')
    c = conn.cursor()
    # Table for prediction data
    c.execute('''CREATE TABLE IF NOT EXISTS adherence_data
                 (mid TEXT, age INTEGER, sex TEXT,
                  feature1 INTEGER, feature2 INTEGER, feature3 INTEGER,
                  feature4 INTEGER, feature5 INTEGER, feature6 INTEGER,
                  feature7 INTEGER, feature8 INTEGER, feature9 INTEGER,
                  feature10 INTEGER, feature11 INTEGER, feature12 TEXT)''')
    # Table for account details
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT,
                 email TEXT,
                 password TEXT
                 )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def login_redirect():
    return redirect(url_for('login'))

# Render login page (GET) and process login form (POST)
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('adherence_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM accounts WHERE username=? AND password=?", (username, password))
    account = c.fetchone()
    conn.close()
    if account:
        session['user_id'] = account[0]
        session['username'] = account[1]
        return redirect(url_for('home'))
    else:
        message = "Invalid credentials. Please try again."
        return render_template('login.html', message=message)

@app.route('/create', methods=['GET'])
def create():
    return render_template('create.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('adherence_data.db')
        c = conn.cursor()
        c.execute("INSERT INTO accounts (username, email, password) VALUES (?, ?, ?)",
                  (username, email, password))
        conn.commit()
        conn.close()
        
        message = "Account created successfully."
    except Exception as e:
        message = f"Error: {str(e)}"
    
    return render_template('create.html', message=message)

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Optionally, you can fetch and display account details here using session['user_id']
    return render_template('index.html', username=session.get('username'))

@app.route('/about')
def about():
    return render_template('about.html')

def predict_class(features):
    # Dummy prediction logic (replace with actual ML model)
    return 'high' if sum(features) > 15 else 'low'

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Validate and parse form fields
        age = request.form.get('age')
        sex = request.form.get('sex')
        features = []
        for i in range(1, 12):
            feature_value = request.form.get(f'feature{i}')
            if feature_value is None:
                raise ValueError(f'Missing feature{i}')
            features.append(int(feature_value))

        if not age or not age.isdigit():
            raise ValueError('Invalid age')
        age = int(age)

        if sex not in ['male', 'female', 'other']:
            raise ValueError('Invalid sex')

        # Auto-increment mid by finding max existing mid in database
        conn = sqlite3.connect('adherence_data.db')
        c = conn.cursor()
        c.execute("SELECT mid FROM adherence_data ORDER BY CAST(mid AS INTEGER) DESC LIMIT 1")
        row = c.fetchone()
        if row is None:
            new_mid = 1
        else:
            try:
                new_mid = int(row[0]) + 1
            except ValueError:
                # If mid is not numeric, fallback to 1
                new_mid = 1

        # Predict the adherence class based on features
        predicted_class = predict_class(features)

        # Insert prediction data into the database (with predicted_class as feature12)
        c.execute('''INSERT INTO adherence_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (str(new_mid), age, sex) + tuple(features) + (predicted_class,))
        conn.commit()
        conn.close()

        prediction_text = f'Predicted Class is: {predicted_class}. Data saved to database successfully. Medical Record Number (mid): {new_mid}'
    except Exception as e:
        prediction_text = f'Error: {str(e)}'

    return render_template('index.html', prediction_text=prediction_text)

@app.route('/view_data')
def view_data():
    conn = sqlite3.connect('adherence_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM adherence_data")
    data = c.fetchall()
    conn.close()
    return render_template('view_data.html', data=data)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Process contact form submission here if needed
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # For now, just render the page with a thank you message or similar
        thank_you_message = f"Thank you, {name}, for contacting us. We will get back to you shortly."
        return render_template('contact.html', message=thank_you_message)
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
