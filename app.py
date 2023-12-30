from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import sqlite3

app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.config['SECRET_KEY'] = 'your_secret_key_here'


# ====== SQLite DB =======

# con = sqlite3.connect('zoo.db')
# conn = sqlite3.connect('users.db')
# cur = con.cursor()
# curr = conn.cursor()


# cur.execute("""
#     CREATE TABLE animals (
#         animal_id INTEGER PRIMARY KEY AUTOINCREMENT,
#         name VARCHAR(45),
#         species VARCHAR(45),
#         age INTEGER,
#         is_predator BOOLEAN
#     )
# """)


# Create the 'users' table if it doesn't exist
# curr.execute("""
#     CREATE TABLE IF NOT EXISTS users (
#         user_id INTEGER PRIMARY KEY AUTOINCREMENT,
#         username VARCHAR(50) UNIQUE,
#         password VARCHAR(50)
#     )
# """)
# conn.commit()

# ======

# ==== User Class Flask Login ====
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

# Configure the login manager
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# ========


# ====== Flask Routes =======

# ==== Pages ====
@app.route('/')
@login_required  # Requires the user to be logged in
def index():

    # Category Filter Request
    diet_category_filter = request.args.get('diet_category')
    # Search Request
    search_term = request.args.get('search')

    # Move the connection and cursor creation inside the function
    with sqlite3.connect('zoo.db') as con:
        cur = con.cursor()

                # Construct the SQL query based on filters
        query = "SELECT animal_id, name, species, age, is_predator, image FROM animals"
        conditions = []

        if diet_category_filter:
            conditions.append("is_predator = {}".format(diet_category_filter == 'Predator'))

        if search_term:
            conditions.append("LOWER(name) LIKE '%{}%' OR LOWER(species) LIKE '%{}%'".format(search_term.lower(), search_term.lower()))

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cur.execute(query)
        data = cur.fetchall()

    # Convert data to JSON
    data_json = [{'animal_id': row[0], 'name': row[1], 'species': row[2], 'age': row[3], 'image': row[5],'diet_category': 'Predator' if row[4] else 'Herbivore'} for row in data]

    # Return JSON data
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify({'data': data_json})

    # Render the template with JSON data
    return render_template('index.html', data=data_json)



@app.route('/add', methods=['GET','POST'])
@login_required
def add():
    if request.headers.get('Content-Type') == 'application/json':
        # JSON request handling
        data = request.json
        name = data.get('name')
        species = data.get('species')
        age = data.get('age')
        image = data.get('image')
        diet_category = data.get('dietCategory')
        # Convert the selection to a boolean
        is_predator = (diet_category == 'Predator')

        with sqlite3.connect('zoo.db') as con:
            cur = con.cursor()
            cur.execute("INSERT INTO animals (name, species, age, is_predator, image) VALUES (?, ?, ?, ?, ?)", (name, species, age, is_predator, image))
            con.commit()

        return jsonify({'status': 'success', 'message': 'Animal added successfully'})

    elif request.method == 'POST':
        # Regular form submission handling
        name = request.form['name']
        species = request.form['species']
        age = request.form['age']
        image = request.form['image']
        diet_category = request.form['dietCategory']
        # Convert the selection to a boolean
        is_predator = (diet_category == 'Predator')

        with sqlite3.connect('zoo.db') as con:
            cur = con.cursor()
            cur.execute("INSERT INTO animals (name, species, age, is_predator, image) VALUES (?, ?, ?, ?, ?)", (name, species, age, is_predator, image))
            con.commit()

        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/delete/<int:animal_id>', methods=['POST'])
@login_required
def delete(animal_id):
    with sqlite3.connect('zoo.db') as con:
        cur = con.cursor()
        cur.execute("DELETE FROM animals WHERE animal_id = ?", (animal_id,))
        con.commit()
 
    return redirect(url_for('index'))


@app.route('/edit/<int:animal_id>', methods=['GET', 'POST'])
@login_required
def edit(animal_id):
    # Fetch the specific animal for editing
    with sqlite3.connect('zoo.db') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM animals WHERE animal_id = ?", (animal_id,))
        animal = cur.fetchone()

    if request.method == 'POST':
        # Handle form submission
        name = request.form['name']
        species = request.form['species']
        age = request.form['age']
        image = request.form['image']
        diet_category = request.form['dietCategory']
        is_predator = (diet_category == 'Predator')

        with sqlite3.connect('zoo.db') as con:
            cur = con.cursor()
            cur.execute("UPDATE animals SET name=?, species=?, age=?, is_predator=?, image=? WHERE animal_id=?",
                        (name, species, age, is_predator, image, animal_id))
            con.commit()

        # Redirect to the index page after editing
        return redirect(url_for('index'))

    return render_template('edit.html', animal=animal)

#=====

#==== Login ====


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.headers.get('Content-Type') == 'application/json':
        # JSON request handling
        data = request.json
        username = data.get('username')
        password = data.get('password')

        with sqlite3.connect('users.db') as conn:
            cur = conn.cursor()
            # Check if the username already exists
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cur.fetchone()
            if existing_user:
                return jsonify({'status': 'error', 'message': 'Username already exists. Please choose a different username.'})

            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()

        return jsonify({'status': 'success', 'message': 'User registered successfully'})
    elif request.method == 'POST':
        # Regular form submission handling
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('users.db') as conn:
            cur = conn.cursor()
            # Check if the username already exists
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cur.fetchone()
            if existing_user:
                flash('Username already exists. Please choose a different username.', 'error')
                return render_template('register.html')

            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()

        return redirect(url_for('index'))  # Redirect to a different page after successful registration

    return render_template('register.html')  # Render the register page for GET requests


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.headers.get('Content-Type') == 'application/json':
        # JSON request handling
        data = request.json
        username = data.get('username')
        password = data.get('password')

        with sqlite3.connect('users.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cur.fetchone()

        if user:
            return jsonify({'status': 'success', 'message': 'Login successful'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid username or password'})
    elif request.method == 'POST':
        # Regular form submission handling
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('users.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cur.fetchone()

        if user:
            login_user(User(user[0]))  # Log in the user
            return redirect(url_for('index'))  # Redirect to a different page after successful login
        else:
            return render_template('login.html', message='Invalid username or password')  # Render login page with an error message

    return render_template('login.html')  # Render the login page for GET requests

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Logs out the user
    return render_template('logout.html')




if __name__ == '__main__':
    app.run(debug=True)
