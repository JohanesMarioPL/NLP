from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import os
from werkzeug.utils import secure_filename 


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ganti dengan kunci rahasia Anda

UPLOAD_FOLDER = 'static/pdfs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}
PDFS_FOLDER = 'static/pdfs'
os.makedirs(PDFS_FOLDER, exist_ok=True)  # Membuat folder jika belum ada

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        flash('File tidak ditemukan!', 'danger')
        return redirect(url_for('user_dashboard'))

# Dummy username dan password
USERS = {
    'admin': {'password': 'password', 'role': 'admin'},
    'user': {'password': 'password123', 'role': 'user'}
}

@app.route('/')
def home():
    if 'logged_in' in session:
        role = session['role']
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'user':
            return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/resources')
def admin_dashboard():
    if 'logged_in' in session and session['role'] == 'admin':
        resources = [
        {'name': 'Resource1.pdf', 'source': 'https://www.resource1.com'},
        {'name': 'Resource2.pdf', 'source': 'https://www.resource2.com'},
        {'name': 'Resource3.pdf', 'source': 'https://www.resource3.com'}
        ]   
        return render_template('admin_dashboard.html', resources=resources)
    return redirect(url_for('login'))

@app.route('/upload_new_resource')
def upload_new_resource():
    if 'logged_in' in session and session['role'] == 'admin':
        return render_template('upload_resource.html')
    return redirect(url_for('login'))

@app.route('/upload_resource')
def upload_resource():
    if request.method == 'POST':
        # Cek apakah ada file yang diunggah
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # Cek apakah file telah dipilih
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        # Simpan file
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File uploaded successfully')
            return redirect(url_for('upload_resource'))
    return render_template('upload_resource.html')

@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    if 'logged_in' in session and session['role'] == 'user':
        if request.method == 'POST':
            # Cek apakah ada file dalam request
            if 'file' not in request.files:
                flash('Tidak ada file yang diunggah!', 'danger')
                return redirect(request.url)

            file = request.files['file']
            # Cek apakah file memiliki nama dan format yang benar
            if file.filename == '':
                flash('File tidak memiliki nama!', 'danger')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('Input berhasil!', 'success')
                return redirect(request.url)

            flash('Hanya file PDF yang diizinkan!', 'danger')
            return redirect(request.url)

        return render_template('user_dashboard.html')
    return redirect(url_for('login'))

@app.route('/history')
def history():
    if 'logged_in' in session and session['role'] == 'user':
        # Ambil daftar file PDF di folder PDFS_FOLDER
        pdf_files = [f for f in os.listdir(PDFS_FOLDER) if f.endswith('.pdf')]
        return render_template('history.html', pdf_files=pdf_files)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = USERS.get(username)
        if user and user['password'] == password:
            session['logged_in'] = True
            session['role'] = user['role']
            session['username'] = username
            flash('Login berhasil!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Username atau password salah!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('role', None)
    session.pop('username', None)
    flash('Anda telah logout.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/download/<filename>')
def download_file(filename):
    # Logika untuk mengunduh file
    return send_from_directory(PDFS_FOLDER, filename)
