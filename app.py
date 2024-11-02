from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'some_secret_key'

# Adatbázis inicializálása
def init_db():
    conn = sqlite3.connect('regisztracio.db')
    c = conn.cursor()
    
    # Diákok táblázat létrehozása
    c.execute('''CREATE TABLE IF NOT EXISTS diakok
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, nev TEXT, osztaly TEXT,
                  elso_idosav TEXT, masodik_idosav TEXT, harmadik_idosav TEXT)''')
    
    # Előadások táblázat létrehozása
    c.execute('''CREATE TABLE IF NOT EXISTS eloadasok
                 (idosav TEXT, eloadas TEXT, max_letszam INTEGER, jelenlegi_letszam INTEGER)''')
    
    # Előadások feltöltése, ha még nincsenek az adatbázisban
    c.execute('SELECT COUNT(*) FROM eloadasok')
    if c.fetchone()[0] == 0:
        eloadasok = [
            ('1. idősáv', '1.1', 100, 0), ('1. idősáv', '1.2', 28, 0), ('1. idősáv', '1.3', 26, 0),
            ('2. idősáv', '2.1', 50, 0), ('2. idősáv', '2.2', 25, 0), ('2. idősáv', '2.3', 30, 0),
            ('3. idősáv', '3.1', 50, 0), ('3. idősáv', '3.2', 40, 0), ('3. idősáv', '3.3', 50, 0)
        ]
        c.executemany('INSERT INTO eloadasok VALUES (?, ?, ?, ?)', eloadasok)
    
    conn.commit()
    conn.close()

# Főoldal, diák regisztrációs űrlap
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        nev = request.form['nev']
        osztaly = request.form['osztaly']
        elso_idosav = request.form['elso_idosav']
        masodik_idosav = request.form['masodik_idosav']
        harmadik_idosav = request.form['harmadik_idosav']
        
        conn = sqlite3.connect('regisztracio.db')
        c = conn.cursor()
        try:
            # Diák regisztráció
            c.execute('INSERT INTO diakok (email, nev, osztaly, elso_idosav, masodik_idosav, harmadik_idosav) VALUES (?, ?, ?, ?, ?, ?)', 
                      (email, nev, osztaly, elso_idosav, masodik_idosav, harmadik_idosav))
            conn.commit()
            flash('Sikeres regisztráció!', 'success')
        except sqlite3.IntegrityError:
            flash('Ezzel az email címmel már regisztráltak!', 'error')
        conn.close()
        return redirect(url_for('register'))
    
    return render_template('register.html')

# Admin oldal a diákok megtekintéséhez
@app.route('/admin')
def admin_dashboard():
    conn = sqlite3.connect('regisztracio.db')
    c = conn.cursor()

    # Diákok lekérdezése
    c.execute('SELECT * FROM diakok')
    diakok = c.fetchall()

    # Előadások regisztrált diákjainak száma
    eloadasok_diakok = {}
    c.execute('SELECT elso_idosav, COUNT(*) FROM diakok GROUP BY elso_idosav')
    for eloadas, count in c.fetchall():
        eloadasok_diakok[eloadas] = count

    conn.close()
    
    return render_template('admin_dashboard.html', diakok=diakok, eloadasok_diakok=eloadasok_diakok)

if __name__ == '__main__':
    init_db()  # Adatbázis inicializálás
    app.run(host='0.0.0.0', port=5000, debug=True)
