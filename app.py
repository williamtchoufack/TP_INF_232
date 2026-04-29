import os, io, csv
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import dj_database_url
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from functools import wraps
from dotenv import load_dotenv

load_dotenv() # Charge les variables d'environnement depuis un fichier .env

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "une_cle_par_defaut_inf232")

# --- CONFIGURATION POSTGRESQL ---
# L'URL de la base de données sera fournie par Neon.tech
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            nom TEXT NOT NULL,
            age INTEGER NOT NULL,
            niveau TEXT NOT NULL,
            filiere TEXT NOT NULL,
            note_maths DECIMAL NOT NULL,
            note_info DECIMAL NOT NULL,
            note_anglais DECIMAL NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# Initialisation au démarrage
if DATABASE_URL:
    init_db()

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# --- Sécurité ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USER and request.form["password"] == ADMIN_PASS:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        flash("Identifiants incorrects", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("index"))

# --- Routes ---
@app.route("/")
def index():
    return render_template("formulaire.html")

@app.route("/submit", methods=["POST"])
def submit():
    d = request.form
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO students (nom, age, niveau, filiere, note_maths, note_info, note_anglais) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                 (d['nom'], d['age'], d['niveau'], d['filiere'], d['note_maths'], d['note_info'], d['note_anglais']))
    conn.commit()
    cur.close()
    conn.close()
    flash("Inscription réussie !", "success")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    cur.close()
    conn.close()
    
    total = len(students)
    moy_gen = 0
    meilleur = "Aucun"
    
    if total > 0:
        for s in students:
            s['moy'] = round((float(s['note_maths']) + float(s['note_info']) + float(s['note_anglais']))/3, 2)
        moy_gen = round(sum(s['moy'] for s in students)/total, 2)
        top = max(students, key=lambda x: x['moy'])
        meilleur = f"{top['nom']} ({top['moy']})"
        
    return render_template("dashboard.html", students=students, total=total, moy_gen=moy_gen, meilleur=meilleur)

@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/export/<type>")
@login_required
def export(type):
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    if type == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        return send_file(io.BytesIO(output.getvalue().encode()), mimetype="text/csv", as_attachment=True, download_name="data.csv")
    elif type == "excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return send_file(output, mimetype="application/vnd.ms-excel", as_attachment=True, download_name="data.xlsx")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
