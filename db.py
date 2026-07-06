# db.py
# ---------------------------------------------------------------
# Connexion à la base et peuplement des données de démonstration.
#
# Pour la démo locale (sans serveur MongoDB), on utilise `mongomock`,
# une librairie qui simule fidèlement l'API de PyMongo en mémoire.
# En production, il suffit de remplacer la ligne `mongomock.MongoClient()`
# par `pymongo.MongoClient("mongodb+srv://.../catalogue")` : tout le
# reste du code (requêtes, agrégations) fonctionne à l'identique,
# car mongomock respecte l'API PyMongo.
# ---------------------------------------------------------------

import mongomock
from datetime import datetime, timedelta
import random

def get_db():
    client = mongomock.MongoClient()
    db = client["catalogue_produits"]
    if db.products.count_documents({}) == 0:
        _seed(db)
    return db


def _seed(db):
    random.seed(42)

    # ---------- Catégories ----------
    categories = [
        {"_id": "cat_electronique", "nom": "Électronique",
         "description": "Appareils électroniques et accessoires"},
        {"_id": "cat_vetements", "nom": "Vêtements",
         "description": "Vêtements pour tous les âges"},
        {"_id": "cat_livres", "nom": "Livres",
         "description": "Livres papier et numériques"},
        {"_id": "cat_maison", "nom": "Maison & Cuisine",
         "description": "Articles pour la maison et la cuisine"},
        {"_id": "cat_sport", "nom": "Sport & Loisirs",
         "description": "Équipements sportifs et de loisirs"},
    ]
    db.categories.insert_many(categories)

    # ---------- Utilisateurs ----------
    prenoms = ["Léa", "Hugo", "Chloé", "Nathan", "Emma", "Louis", "Manon",
               "Jules", "Camille", "Adam", "Sarah", "Théo", "Inès", "Noah", "Zoé"]
    users = []
    for i, p in enumerate(prenoms):
        users.append({
            "_id": f"user_{i+1:03d}",
            "pseudo": p,
            "email": f"{p.lower()}@example.com",
            "date_inscription": datetime(2024, 1, 1) + timedelta(days=random.randint(0, 500)),
            "ville": random.choice(["Paris", "Lyon", "Marseille", "Toulouse", "Lille", "Nantes"]),
        })
    db.users.insert_many(users)

    # ---------- Produits ----------
    # attributs volontairement hétérogènes selon la catégorie : c'est
    # précisément ce qui justifie un modèle NoSQL orienté document.
    produits_data = [
        # (nom, categorie, prix, stock, marque, attributs_specifiques, jours_ecoule)
        ("Casque Bluetooth NoiseAway", "cat_electronique", 89.99, 34, "Sonix",
         {"autonomie_h": 24, "reduction_bruit": True, "couleur": "noir"}, 5),
        ("Smartphone Pixel Lite", "cat_electronique", 449.00, 0, "Vega",
         {"stockage_go": 128, "ram_go": 6, "couleur": "bleu"}, 20),
        ("Enceinte portable BoomBox", "cat_electronique", 59.90, 12, "Sonix",
         {"autonomie_h": 10, "etancheite": "IPX7"}, 40),
        ("Clavier mécanique ClicPro", "cat_electronique", 74.50, 8, "KeyForge",
         {"switch": "rouge", "retroeclairage": True}, 90),
        ("T-shirt coton bio", "cat_vetements", 19.99, 120, "EcoWear",
         {"taille": "M", "couleur": "blanc", "matiere": "coton bio"}, 15),
        ("Jean slim stretch", "cat_vetements", 45.00, 0, "DenimCo",
         {"taille": "40", "couleur": "bleu foncé"}, 60),
        ("Veste imperméable", "cat_vetements", 89.00, 25, "RainGuard",
         {"taille": "L", "couleur": "kaki", "impermeable": True}, 10),
        ("Chaussettes pack x5", "cat_vetements", 12.50, 200, "EcoWear",
         {"taille": "unique", "couleur": "assorti"}, 200),
        ("Le Silence des Cimes", "cat_livres", 14.90, 45, "Éditions Aurore",
         {"auteur": "M. Lenoir", "pages": 320, "format": "broché"}, 30),
        ("Python pour les Nuls", "cat_livres", 24.90, 3, "TechPress",
         {"auteur": "J. Vidal", "pages": 480, "format": "broché"}, 100),
        ("Atlas Historique Illustré", "cat_livres", 34.00, 0, "CartoLivres",
         {"auteur": "Collectif", "pages": 210, "format": "relié"}, 300),
        ("Recueil de Nouvelles Nordiques", "cat_livres", 16.50, 18, "Éditions Aurore",
         {"auteur": "S. Holm", "pages": 190, "format": "poche"}, 5),
        ("Robot pâtissier MixMaster", "cat_maison", 199.00, 6, "CuisinePlus",
         {"puissance_w": 1000, "capacite_l": 5}, 25),
        ("Set de couteaux Damas", "cat_maison", 129.00, 14, "LameFine",
         {"pieces": 6, "materiau": "acier damas"}, 70),
        ("Lampe de bureau LED", "cat_maison", 39.90, 55, "Luminae",
         {"puissance_w": 8, "variateur": True}, 12),
        ("Tapis de yoga antidérapant", "cat_sport", 29.90, 40, "FlexFit",
         {"epaisseur_mm": 6, "couleur": "violet"}, 8),
        ("Vélo pliant UrbanRide", "cat_sport", 349.00, 2, "UrbanRide",
         {"poids_kg": 12, "vitesses": 7}, 150),
        ("Haltères ajustables 20kg", "cat_sport", 119.00, 0, "FlexFit",
         {"poids_max_kg": 20, "reglable": True}, 45),
        ("Montre connectée PulseFit", "cat_electronique", 129.00, 22, "Vega",
         {"autonomie_j": 7, "gps": True, "couleur": "noir"}, 3),
        ("Sac à dos randonnée 40L", "cat_sport", 79.90, 17, "TrailPro",
         {"capacite_l": 40, "impermeable": True}, 18),
    ]

    now = datetime(2026, 7, 3)
    products = []
    for i, (nom, cat, prix, stock, marque, attrs, jours) in enumerate(produits_data):
        products.append({
            "_id": f"prod_{i+1:03d}",
            "nom": nom,
            "categorie_id": cat,
            "prix": prix,
            "stock": stock,
            "marque": marque,
            "attributs": attrs,          # <-- schéma flexible, varie par produit
            "date_ajout": now - timedelta(days=jours),
        })
    db.products.insert_many(products)

    # ---------- Avis (reviews) ----------
    reviews = []
    review_id = 1
    for prod in products:
        # nombre d'avis variable, certains produits n'en ont aucun
        nb_avis = random.choice([0, 0, 1, 2, 3, 3, 4, 5])
        chosen_users = random.sample(users, k=min(nb_avis, len(users)))
        for u in chosen_users:
            note = random.choices([1, 2, 3, 4, 5], weights=[5, 8, 15, 35, 37])[0]
            reviews.append({
                "_id": f"rev_{review_id:04d}",
                "produit_id": prod["_id"],
                "utilisateur_id": u["_id"],
                "note": note,
                "commentaire": _commentaire_type(note),
                "date": prod["date_ajout"] + timedelta(days=random.randint(1, 60)),
                "votes_utiles": random.randint(0, 25),
            })
            review_id += 1
    db.reviews.insert_many(reviews)


def _commentaire_type(note):
    if note >= 4:
        return "Très satisfait de cet achat, je recommande."
    if note == 3:
        return "Correct, sans plus."
    return "Déçu par la qualité, ne recommande pas."
