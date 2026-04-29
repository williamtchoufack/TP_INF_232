"""
charts.py — Génère des graphiques depuis la base SQLite students.db
Usage : python charts.py
"""

import sqlite3
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

DB = "students.db"
OUTPUT_DIR = "charts_output"

# Palette sombre cohérente avec le dashboard
BG       = "#0d0f14"
CARD     = "#1a1e29"
ACCENT   = "#f0c040"
ACCENT2  = "#4fd1c5"
GOOD     = "#22c55e"
OK       = "#f59e0b"
BAD      = "#ef4444"
TEXT     = "#e8eaf0"
MUTED    = "#6b7280"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.facecolor": CARD,
    "figure.facecolor": BG,
    "text.color": TEXT,
    "axes.labelcolor": TEXT,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.edgecolor": "#252a38",
    "axes.grid": True,
    "grid.color": "#1e2333",
    "grid.linewidth": 0.7,
})

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    if not os.path.exists(DB):
        print(f"[ERREUR] Base de données '{DB}' introuvable.")
        print("Lance d'abord app.py et ajoute des étudiants.")
        return []
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return rows

def compute_moyenne(s):
    return round((s["note_maths"] + s["note_info"] + s["note_anglais"]) / 3, 2)

def chart_moyennes_par_etudiant(students):
    """Barres : moyenne de chaque étudiant"""
    noms = [s["nom"].split()[0] for s in students]
    moys = [compute_moyenne(s) for s in students]
    colors = [GOOD if m >= 14 else (OK if m >= 10 else BAD) for m in moys]

    fig, ax = plt.subplots(figsize=(max(8, len(students) * 1.2), 5))
    bars = ax.bar(noms, moys, color=colors, width=0.55, zorder=3)
    ax.set_ylim(0, 22)
    ax.set_title("Moyenne par étudiant", color=TEXT, fontsize=14, fontweight="bold", pad=16)
    ax.set_xlabel("Étudiant", labelpad=10)
    ax.set_ylabel("Moyenne /20", labelpad=10)

    for bar, val in zip(bars, moys):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                f"{val:.2f}", ha="center", va="bottom", color=TEXT, fontsize=9)

    legend_elements = [
        mpatches.Patch(color=GOOD, label="≥ 14 (Bien)"),
        mpatches.Patch(color=OK,   label="≥ 10 (Passable)"),
        mpatches.Patch(color=BAD,  label="< 10 (Insuffisant)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", facecolor=CARD,
              edgecolor="#252a38", labelcolor=TEXT, fontsize=9)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "01_moyennes_etudiants.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ {path}")

def chart_notes_par_matiere(students):
    """Barres groupées : Maths / Info / Anglais par étudiant"""
    noms = [s["nom"].split()[0] for s in students]
    maths   = [s["note_maths"]   for s in students]
    info    = [s["note_info"]    for s in students]
    anglais = [s["note_anglais"] for s in students]

    x = np.arange(len(noms))
    w = 0.26

    fig, ax = plt.subplots(figsize=(max(9, len(students) * 1.5), 5))
    ax.bar(x - w, maths,   width=w, label="Maths",   color=ACCENT,  zorder=3)
    ax.bar(x,     info,    width=w, label="Info",    color=ACCENT2, zorder=3)
    ax.bar(x + w, anglais, width=w, label="Anglais", color="#a78bfa", zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(noms)
    ax.set_ylim(0, 22)
    ax.set_title("Notes par matière", color=TEXT, fontsize=14, fontweight="bold", pad=16)
    ax.legend(facecolor=CARD, edgecolor="#252a38", labelcolor=TEXT, fontsize=9)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "02_notes_matieres.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ {path}")

def chart_repartition_filieres(students):
    """Camembert : répartition par filière"""
    from collections import Counter
    filieres = Counter(s["filiere"] for s in students)
    labels = list(filieres.keys())
    sizes  = list(filieres.values())
    palette = [ACCENT, ACCENT2, "#a78bfa", GOOD, OK, BAD]

    fig, ax = plt.subplots(figsize=(7, 5))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct="%1.0f%%",
        colors=palette[:len(labels)],
        startangle=90,
        wedgeprops={"edgecolor": BG, "linewidth": 2},
        textprops={"color": TEXT}
    )
    for at in autotexts:
        at.set_color("#000")
        at.set_fontweight("bold")

    ax.set_title("Répartition par filière", color=TEXT, fontsize=14, fontweight="bold", pad=16)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "03_repartition_filieres.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ {path}")

def chart_distribution_moyennes(students):
    """Histogramme : distribution des moyennes"""
    moys = [compute_moyenne(s) for s in students]

    fig, ax = plt.subplots(figsize=(8, 5))
    n, bins, patches = ax.hist(moys, bins=10, range=(0, 20), color=ACCENT, edgecolor=BG, zorder=3)

    # Colorier selon seuils
    for patch, left in zip(patches, bins[:-1]):
        if left >= 14:   patch.set_facecolor(GOOD)
        elif left >= 10: patch.set_facecolor(OK)
        else:            patch.set_facecolor(BAD)

    ax.axvline(x=10, color=TEXT, linestyle="--", linewidth=1, alpha=0.5, label="Seuil 10")
    ax.set_title("Distribution des moyennes", color=TEXT, fontsize=14, fontweight="bold", pad=16)
    ax.set_xlabel("Moyenne /20")
    ax.set_ylabel("Nombre d'étudiants")
    ax.legend(facecolor=CARD, edgecolor="#252a38", labelcolor=TEXT, fontsize=9)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "04_distribution.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ {path}")

def main():
    print("\n📊 Génération des graphiques INF232")
    print("=" * 40)

    students = load_data()
    if not students:
        return

    print(f"  → {len(students)} étudiant(s) trouvé(s)\n")

    chart_moyennes_par_etudiant(students)
    chart_notes_par_matiere(students)
    chart_repartition_filieres(students)
    chart_distribution_moyennes(students)

    print(f"\n✅ Tous les graphiques sont dans : ./{OUTPUT_DIR}/")
    print("=" * 40)

if __name__ == "__main__":
    main()
