import os, psycopg2, random
from dotenv import load_dotenv
load_dotenv()

def seed():
    url = os.environ.get("DATABASE_URL")
    conn = psycopg2.connect(url)
    c = conn.cursor()
    filieres = ["Informatique", "IA & Data", "Cybersécurité"]
    niveaux = ["Licence 1", "Licence 2", "Licence 3"]
    
    print("Injection de 100 étudiants dans PostgreSQL...")
    for i in range(100):
        c.execute("INSERT INTO students (nom, age, niveau, filiere, note_maths, note_info, note_anglais) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                  (f"Etudiant_{i}", random.randint(18,25), random.choice(niveaux), random.choice(filieres), 
                   random.randint(8,18), random.randint(8,19), random.randint(10,17)))
    conn.commit()
    c.close()
    conn.close()
    print("✅ Base de données PostgreSQL remplie !")

if __name__ == "__main__":
    seed()
