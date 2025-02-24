import os
import sqlite3
from flask import jsonify
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

app = Flask(__name__, template_folder="templates", static_folder="static")

load_dotenv()
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")

DB_PATH = "database.db"

UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS family_details (
        family_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nearest_city TEXT,
        details TEXT,
        num_children INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS interests (
        interest_id INTEGER PRIMARY KEY AUTOINCREMENT,
        family_id INTEGER NOT NULL,
        interest TEXT NOT NULL,
        FOREIGN KEY (family_id) REFERENCES family_details(family_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        file_path TEXT NOT NULL,
        category TEXT CHECK(category IN ('upcoming', 'past')) NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS event_registrations (
        registration_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        num_people INTEGER NOT NULL,
        adults INTEGER NOT NULL,
        children INTEGER NOT NULL,
        FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS admins (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    ''')
    # Insert admin user if not exists
    cursor.execute("SELECT * FROM admins WHERE email = ?", ("info@karavalkonkans.org.au",))
    if not cursor.fetchone():
        hashed_password = generate_password_hash("karavalkonkans@2025", method="pbkdf2:sha256")
        cursor.execute("INSERT INTO admins (email, password) VALUES (?, ?)",
                       ("info@karavalkonkans.org.au", hashed_password))
    conn.commit()
    conn.close()

init_db()

# Function to add a new user to the database
def add_user(name, email, password, phone, city, details, num_children, interests):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Hash password before storing
    hashed_password = generate_password_hash(password)

    # Insert user details
    cursor.execute('''
        INSERT INTO users (name, email, password, phone) 
        VALUES (?, ?, ?, ?)
    ''', (name, email, hashed_password, phone))
    
    user_id = cursor.lastrowid  # Get the user ID of the newly inserted user

    # Insert family details
    cursor.execute('''
        INSERT INTO family_details (user_id, nearest_city, details, num_children) 
        VALUES (?, ?, ?, ?)
    ''', (user_id, city, details, int(num_children or 0)))  # Ensure num_children is an integer

    family_id = cursor.lastrowid  # Get family ID

    # Insert interests
    if interests:
        for interest in interests.split(","):  # Assuming interests are comma-separated
            cursor.execute('''
                INSERT INTO interests (family_id, interest) 
                VALUES (?, ?)
            ''', (family_id, interest.strip()))

    conn.commit()
    conn.close()


@app.route('/')
def home():
    return render_template('index.html')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            stored_hashed_password = user[1]  # Retrieve hashed password
            if check_password_hash(stored_hashed_password, password):
                session['user_id'] = user[0]  # Store user ID in session
                flash("Login successful!", "success")
                return redirect(url_for('home'))  # Redirect to home page
            else:
                flash("Incorrect email or password!", "danger")
        else:
            flash("Incorrect email or password!", "danger")

    return render_template('login.html')



# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        city = request.form['city']
        details = request.form.get('family_details', '')
        num_children = request.form.get('children_count', 0)
        interests = request.form.get('interests', '')

        # Check if the email already exists
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
        conn.close()

        if existing_user:
            flash("Email already exists! Please use a different email.", "danger")
            return redirect(url_for('register'))  # Redirect back to registration page

        # Add user to the database
        add_user(name, email, password, phone, city, details, num_children, interests)

        flash("Registration successful!", "success")
        return redirect(url_for('home'))  # Redirect to home after successful registration

    return render_template('JoinFamReg.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         password = generate_password_hash(request.form['password'])
#         phone = request.form['phone']

#         conn = sqlite3.connect(DB_PATH)
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
#         existing_user = cursor.fetchone()

#         if existing_user:
#             flash("Email already exists!", "danger")
#             return redirect(url_for('register'))

#         cursor.execute("INSERT INTO users (name, email, password, phone) VALUES (?, ?, ?, ?)", 
#                        (name, email, password, phone))
#         conn.commit()
#         conn.close()

#         flash("Admin registered successfully!", "success")
#         return redirect(url_for('login'))

#     return render_template('JoinFamReg.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']

#         conn = sqlite3.connect(DB_PATH)
#         cursor = conn.cursor()
#         cursor.execute("SELECT user_id, password FROM users WHERE email = ?", (email,))
#         user = cursor.fetchone()
#         conn.close()

#         if user and check_password_hash(user[1], password):
#             session['user_id'] = user[0]
#             flash("Login successful!", "success")
#             return redirect(url_for('home'))
#         else:
#             flash("Incorrect email or password!", "danger")

#     return render_template('login.html')
@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('home'))

@app.route('/upload-content', methods=['POST'])
def upload_content():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        file = request.files['file']

        if not title or not category or not file:
            flash("Please fill in all fields!", "danger")
            return redirect(url_for('admin_panel'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO events (title, description, file_path, category) VALUES (?, ?, ?, ?)",
                           (title, description, f"uploads/{filename}", category))
            conn.commit()
            conn.close()

            flash("Content uploaded successfully!", "success")
        else:
            flash("Invalid file type!", "danger")

    return redirect(url_for('admin_panel'))

# @app.route('/upcoming-events')
# def upcoming_events():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("SELECT event_id, title, description, file_path ,category, uploaded_at FROM events")
#     events = cursor.fetchall()
#     conn.close()
#     return render_template('upevents.html', events=events)
@app.route('/upcoming-events')
def upcoming_events():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT event_id, title, description, file_path ,category, uploaded_at FROM events")
    events = cursor.fetchall()
    conn.close()
    return render_template('upevents.html', events=events)


@app.route('/past-events')
def past_events():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, file_path FROM events WHERE category='past' ORDER BY uploaded_at DESC")
    events = cursor.fetchall()
    conn.close()
    return render_template('Past_Events.html', events=events)

# @app.route('/EventReg/<int:event_id>', methods=['GET', 'POST'])
# def event_register(event_id):
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         phone = request.form['phone']
#         num_people = request.form['people']
#         num_adults = request.form['adults']
#         num_children = request.form['children']

#         # Establish DB Connection
#         conn = sqlite3.connect(DB_PATH)
#         cursor = conn.cursor()

#         # Save registration to database
#         query = """
#         INSERT INTO event_registrations (event_id, name, email, phone, num_people, adults, children)
#         VALUES (?, ?, ?, ?, ?, ?, ?)
#         """
#         cursor.execute(query, (event_id, name, email, phone, num_people, num_adults, num_children))

#         # Commit and Close
#         conn.commit()
#         conn.close()

#         return redirect(url_for('home'))  # Redirect after successful registration

#     return render_template('EventReg.html', event_id=event_id)

# @app.route('/EventReg/<int:event_id>', methods=['GET', 'POST'])
# def event_register(event_id):
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         phone = request.form['phone']
#         num_people = request.form['people']
#         num_adults = request.form['adults']
#         num_children = request.form['children']

#         # Establish DB Connection
#         conn = sqlite3.connect(DB_PATH)
#         cursor = conn.cursor()

#         # Check if user exists in users table
#         cursor.execute("SELECT name, email, phone FROM users WHERE email = ?", (email,))
#         user = cursor.fetchone()

#         if not user:
#             flash("You must be a registered user to sign up for events!", "danger")
#             conn.close()
#             return redirect(url_for('event_register', event_id=event_id))

#         # Ensure entered details match database
#         db_name, db_email, db_phone = user
#         if db_name != name or db_email != email or db_phone != phone:
#             flash("Entered details do not match our records!", "danger")
#             conn.close()
#             return redirect(url_for('event_register', event_id=event_id))

#         # Save registration to database
#         query = """
#         INSERT INTO event_registrations (event_id, name, email, phone, num_people, adults, children)
#         VALUES (?, ?, ?, ?, ?, ?, ?)
#         """
#         cursor.execute(query, (event_id, name, email, phone, num_people, num_adults, num_children))

#         # Commit and Close
#         conn.commit()
#         conn.close()

#         flash("Registration successful!", "success")
#         return redirect(url_for('home'))  # Redirect after successful registration

#     return render_template('EventReg.html', event_id=event_id)

@app.route('/EventReg/<int:event_id>', methods=['GET', 'POST'])  #  Ensure both GET & POST are allowed
def event_register(event_id):
    if request.method == 'POST':  #  Ensure POST request is handled
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        num_people = request.form['people']
        num_adults = request.form['adults']
        num_children = request.form['children']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT name, email, phone FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({"success": False, "message": "You must be a registered user to sign up for events."}), 400

        db_name, db_email, db_phone = user
        if db_name != name or db_email != email or db_phone != phone:
            conn.close()
            return jsonify({"success": False, "message": "Entered details do not match our records."}), 400

        # Save registration
        try:
            query = """
            INSERT INTO event_registrations (event_id, name, email, phone, num_people, adults, children)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (event_id, name, email, phone, num_people, num_adults, num_children))
            conn.commit()
            conn.close()

            return jsonify({"success": True, "message": "Registration successful!"}), 200  #  Return JSON response

        except Exception as e:
            conn.close()
            return jsonify({"success": False, "message": "Registration failed. Please try again later."}), 500

    #  Ensure GET requests return the registration form
    return render_template('EventReg.html', event_id=event_id)


# @app.route('/EventReg/<int:event_id>', methods=['GET', 'POST'])  #  Ensure POST is allowed
# def event_register(event_id):
#     if request.method == 'POST':  # Ensure it handles POST requests
#         name = request.form['name']
#         email = request.form['email']
#         phone = request.form['phone']
#         num_people = request.form['people']
#         num_adults = request.form['adults']
#         num_children = request.form['children']

#         conn = sqlite3.connect(DB_PATH)
#         cursor = conn.cursor()

#         # Check if user exists
#         cursor.execute("SELECT name, email, phone FROM users WHERE email = ?", (email,))
#         user = cursor.fetchone()

#         if not user:
#             conn.close()
#             return jsonify({"success": False, "message": "You must be a registered user to sign up for events."}), 400

#         db_name, db_email, db_phone = user
#         if db_name != name or db_email != email or db_phone != phone:
#             conn.close()
#             return jsonify({"success": False, "message": "Entered details do not match our records."}), 400

#         # Save registration
#         try:
#             query = """
#             INSERT INTO event_registrations (event_id, name, email, phone, num_people, adults, children)
#             VALUES (?, ?, ?, ?, ?, ?, ?)
#             """
#             cursor.execute(query, (event_id, name, email, phone, num_people, num_adults, num_children))
#             conn.commit()
#             conn.close()
#             return jsonify({"success": True, "message": "Registration successful!"}), 200

#         except Exception as e:
#             conn.close()
#             return jsonify({"success": False, "message": "Registration failed. Please try again later."}), 500

#     return render_template('EventReg.html', event_id=event_id)


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Restrict access to only the predefined admin email
        if email != "info@karavalkonkans.org.au":
            flash("Access denied!", "danger")
            return redirect(url_for('admin_login'))

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT admin_id, password FROM admins WHERE email = ?", (email,))
            admin = cursor.fetchone()

        if admin and check_password_hash(admin[1], password):
            session['admin_id'] = admin[0]
            flash("Admin login successful!", "success")
            return redirect(url_for('admin_panel'))
        else:
            flash("Incorrect admin email or password!", "danger")

    return render_template('admin-login.html')



# Admin Panel Route
@app.route('/admin')
def admin_panel():
    if 'admin_id' not in session:
        flash("Please log in as an admin to access this page.", "danger")
        return redirect(url_for('admin_login'))

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Fetch user registrations with family details and interests
        query = '''
        SELECT 
            u.user_id, u.name, u.email, u.phone,
            f.family_id, f.nearest_city, f.details, f.num_children,
            COALESCE(GROUP_CONCAT(i.interest, ', '), 'None') AS interests
        FROM users u
        LEFT JOIN family_details f ON u.user_id = f.user_id
        LEFT JOIN interests i ON f.family_id = i.family_id
        GROUP BY u.user_id, f.family_id;
        '''
        cursor.execute(query)
        registrations = cursor.fetchall()

        # Fetch upcoming events
        cursor.execute("SELECT title, description, file_path FROM events WHERE category='upcoming' ORDER BY uploaded_at DESC")
        upcoming_events = cursor.fetchall()

        # Fetch past events
        cursor.execute("SELECT title, description, file_path FROM events WHERE category='past' ORDER BY uploaded_at DESC")
        past_events = cursor.fetchall()

    return render_template(
        "admin.html",
        registrations=registrations,
        upcoming_events=upcoming_events,
        past_events=past_events
    )


# Admin Logout Route
@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_id', None)
    flash("Admin logged out successfully!", "info")
    return redirect(url_for('admin_login'))

@app.route('/fetch-event-registrations')
def fetch_event_registrations():
    if 'admin_id' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT er.registration_id, er.name, er.email, er.phone, er.num_people, er.adults, er.children, 
           e.event_id, e.title
    FROM event_registrations er
    JOIN events e ON er.event_id = e.event_id
    '''
    
    cursor.execute(query)
    event_registrations = cursor.fetchall()
    
    conn.close()

    return jsonify(event_registrations)
@app.route('/get-event-registrations')
def get_event_registrations():
    if 'admin_id' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch all event registrations with event details
    query = '''
    SELECT er.registration_id, er.name, er.email, er.phone, er.num_people, er.adults, er.children, 
           e.event_id, e.title
    FROM event_registrations er
    JOIN events e ON er.event_id = e.event_id
    ORDER BY er.registration_id DESC
    '''
    
    cursor.execute(query)
    event_registrations = cursor.fetchall()
    
    conn.close()

    # Convert list of tuples into JSON format
    return jsonify([
        {
            "registration_id": reg[0],
            "name": reg[1],
            "email": reg[2],
            "phone": reg[3],
            "num_people": reg[4],
            "adults": reg[5],
            "children": reg[6],
            "event_id": reg[7],
            "event_title": reg[8]
        } 
        for reg in event_registrations
    ])


@app.route('/admin/data')
def get_admin_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events")
    data = cursor.fetchall()
    conn.close()
    
    print("Admin data fetched:", data)  # Debugging
    return jsonify(data)


# Home Page
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)