"""
api.py — API REST Flask exposant le catalogue de produits.

Lancement :
    python api.py
Puis par exemple :
    GET http://localhost:5000/api/categories/cat_electronique/top-produits
    GET http://localhost:5000/api/produits/prix?min=20&max=60
"""
from flask import Flask, jsonify, request
from bson.json_util import dumps
import json

from db import get_db
import queries as q

app = Flask(__name__)
db = get_db()


def ok(data):
    # bson.json_util gère la sérialisation des dates/ObjectId
    return app.response_class(dumps(data, ensure_ascii=False), mimetype="application/json")


@app.route("/api/categories")
def liste_categories():
    return ok(list(db.categories.find({}, {"_id": 1, "nom": 1})))


@app.route("/api/categories/<categorie_id>/top-produits")
def top_produits(categorie_id):
    limite = int(request.args.get("limite", 5))
    return ok(q.q1_produits_mieux_notes_par_categorie(db, categorie_id, limite))


@app.route("/api/produits/prix-moyen-categorie")
def prix_moyen_categorie():
    return ok(q.q2_prix_moyen_par_categorie(db))


@app.route("/api/produits/rupture-stock")
def rupture_stock():
    return ok(q.q3_produits_rupture_stock(db))


@app.route("/api/produits/derniers")
def derniers_produits():
    limite = int(request.args.get("limite", 10))
    return ok(q.q4_derniers_produits_ajoutes(db, limite))


@app.route("/api/utilisateurs/plus-actifs")
def utilisateurs_actifs():
    limite = int(request.args.get("limite", 5))
    return ok(q.q5_utilisateurs_plus_actifs(db, limite))


@app.route("/api/produits/<produit_id>/repartition-notes")
def repartition_notes(produit_id):
    return ok(q.q6_repartition_notes_produit(db, produit_id))


@app.route("/api/produits/prix")
def produits_par_prix():
    prix_min = float(request.args.get("min", 0))
    prix_max = float(request.args.get("max", 1_000_000))
    return ok(q.q7_produits_par_fourchette_prix(db, prix_min, prix_max))


@app.route("/api/categories/populaires")
def categories_populaires():
    return ok(q.q8_categories_plus_populaires(db))


@app.route("/api/produits/avis-negatifs")
def avis_negatifs():
    return ok(q.q9_produits_avis_negatifs(db))


@app.route("/api/categories/extremes-prix")
def extremes_prix():
    return ok(q.q10_produit_extreme_par_categorie(db))


@app.route("/api/utilisateurs/multi-categories")
def utilisateurs_multi_categories():
    return ok(q.q11_utilisateurs_multi_categories(db))


@app.route("/api/avis/evolution-mensuelle")
def evolution_avis():
    return ok(q.q12_evolution_avis_par_mois(db))


@app.route("/api/produits/sans-avis")
def produits_sans_avis():
    return ok(q.q13_produits_sans_avis(db))


@app.route("/api/marques/populaires")
def marques_populaires():
    limite = int(request.args.get("limite", 5))
    return ok(q.q14_marques_les_plus_representees(db, limite))


@app.route("/api/satisfaction-globale")
def satisfaction_globale():
    return ok(q.q15_satisfaction_moyenne_globale(db))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
