from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secret_key'

# Database initialization
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
''')

# Students table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        
        username TEXT,
        password TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        
        title TEXT,
        author TEXT,
        quantity INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS borrowed_books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        student_name TEXT,
        book_id INTEGER,
        book_name TEXT,
        FOREIGN KEY (student_id) REFERENCES students (id),
        FOREIGN KEY (book_id) REFERENCES books (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS returned_books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        student_name TEXT,
        book_id INTEGER,
        book_name TEXT,
        FOREIGN KEY (student_id) REFERENCES students (id),
        FOREIGN KEY (book_id) REFERENCES books (id)
    )
''')

conn.commit()
conn.close()

@app.route('/')
def landing_page():
    return render_template('landing_page.html')

# Admin Signup route
@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        admin_id = request.form['id']
        admin_username = request.form['username']
        admin_password = request.form['password']

        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE id = ?', (admin_id,))
        existing_admin = cursor.fetchone()

        if existing_admin:
            flash('Admin ID already taken. Please choose a different one.', 'error')
            render_template('admin_signup.html')
        else:
            hashed_password = generate_password_hash(admin_password)
            cursor.execute('INSERT INTO admins (id, username, password) VALUES (?, ?, ?)', (admin_id, admin_username, hashed_password))
            conn.commit()
            conn.close()

            flash('Admin signup successful! Please login.', 'success')
            return redirect(url_for('admin_login'))

    return render_template('admin_signup.html')

# Student Signup route
@app.route('/student_signup', methods=['GET', 'POST'])
def student_signup():
    if request.method == 'POST':
        student_id = request.form['id']
        student_username = request.form['username']
        student_password = request.form['password']

        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        existing_student = cursor.fetchone()

        if existing_student:
            flash('Student ID already taken. Please choose a different one.', 'error')
            render_template('student_signup.html')
        else:
            hashed_password = generate_password_hash(student_password)
            cursor.execute('INSERT INTO students (id, username, password) VALUES (?, ?, ?)', (student_id, student_username, hashed_password))
            conn.commit()
            conn.close()

            flash('Student signup successful! Please login.', 'success')
            return redirect(url_for('student_login'))

    return render_template('student_signup.html')
# Admin Login route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_id = request.form['id']
        admin_username = request.form['username']
        admin_password = request.form['password']

        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE id = ? AND username = ?', (admin_id, admin_username,))
        admin = cursor.fetchone()
        conn.close()

        if admin and check_password_hash(admin[2], admin_password):
            session['admin_id'] = admin[0]
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin ID, username, or password. Please try again.', 'error')

    return render_template('admin_login.html')

# Student Login route
@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        student_id = request.form['id']
        student_username = request.form['username']
        student_password = request.form['password']

        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE id = ? AND username = ?', (student_id, student_username,))
        student = cursor.fetchone()
        conn.close()

        if student and check_password_hash(student[2], student_password):
            session['student_id'] = student[0]
            flash('Student login successful!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid student ID, username, or password. Please try again.', 'error')

    return render_template('student_login.html')




@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Add book route
@app.route('/add_book', methods=['POST'])
def add_book():
    
    title = request.form['title']
    author = request.form['author']
    quantity = int(request.form['quantity'])
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO books (title, author, quantity) VALUES (?, ?, ?)', (title, author, quantity))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

# Delete book route
@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

# Show books route
@app.route('/show_books')
def show_books():
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    conn.close()

    return render_template('show_books.html', books=books)

@app.route('/stu_show_books')
def stu_show_books():
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    conn.close()

    return render_template('stu_show_books.html', books=books)

# Search books route
@app.route('/search_books', methods=['POST'])
def search_books():
    
    search_title = request.form['search_title']
    
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books WHERE title LIKE ?', ('%' + search_title + '%',))
    books = cursor.fetchall()
    conn.close()

    return render_template('show_books.html', books=books)


@app.route('/student_dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')


# Borrow Book route
@app.route('/borrow_book', methods=['POST'])
def borrow_book():
    student_id = session.get('student_id')

    if student_id is None:
        flash('Please log in to borrow books.', 'error')
        return redirect(url_for('student_login'))

    book_title = request.form['book_title']

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM books WHERE title = ? AND quantity > 0', (book_title,))
        available_book = cursor.fetchone()

        if not available_book:
            flash('Book not available for borrowing.', 'error')
        else:
            # Get the student's name
            cursor.execute('SELECT username FROM students WHERE id = ?', (student_id,))
            student_name = cursor.fetchone()[0]

            # Insert the borrowed book into borrowed_books table
            cursor.execute('INSERT INTO borrowed_books (student_id, student_name, book_id, book_name) VALUES (?, ?, ?, ?)', (student_id, student_name, available_book[0], book_title))

            # Update the quantity of the book in the books table
            cursor.execute('UPDATE books SET quantity = quantity - 1 WHERE id = ?', (available_book[0],))

            flash(f'You have successfully borrowed "{book_title}".', 'success')

    except Exception as e:
        print(f"Error: {e}")
        flash('An error occurred while borrowing the book. Please try again.', 'error')

    conn.commit()
    conn.close()

    return redirect(url_for('student_dashboard'))



# Return Book route
@app.route('/return_book', methods=['POST'])
def return_book():
    student_id = session.get('student_id')

    if student_id is None:
        flash('Please log in to return books.', 'error')
        return redirect(url_for('student_login'))

    returned_book_title = request.form['returned_book_title']

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute('SELECT borrowed_books.id, students.username, books.id, books.title FROM borrowed_books JOIN students ON borrowed_books.student_id = students.id JOIN books ON borrowed_books.book_id = books.id WHERE student_id = ? AND title = ?', (student_id, returned_book_title))
    returned_book = cursor.fetchone()

    if not returned_book:
        flash('Book not found or not borrowed by you.', 'error')
    else:
        # Update returned_books table
        cursor.execute('INSERT INTO returned_books (student_id, student_name, book_id, book_name) VALUES (?, ?, ?, ?)', (returned_book[0], returned_book[1], returned_book[2], returned_book[3]))

        # Update books table
        cursor.execute('UPDATE books SET quantity = quantity + 1 WHERE id = ?', (returned_book[2],))

        # Delete from borrowed_books table
        cursor.execute('DELETE FROM borrowed_books WHERE id = ?', (returned_book[0],))

        flash(f'You have successfully returned "{returned_book[3]}".', 'success')

    conn.commit()
    conn.close()

    return redirect(url_for('student_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)




