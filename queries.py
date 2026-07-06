# queries.py
# ---------------------------------------------------------------
# 15 requêtes / pipelines d'agrégation MongoDB.
# Chaque fonction correspond à un besoin utilisateur du rapport
# (voir rapport_projet.docx, section "Besoins utilisateurs").
# ---------------------------------------------------------------

def q1_produits_mieux_notes_par_categorie(db, categorie_id, limite=5):
    """Besoin 1 : quels sont les produits les mieux notés dans une catégorie ?"""
    pipeline = [
        {"$match": {"categorie_id": categorie_id}},
        {"$lookup": {
            "from": "reviews", "localField": "_id",
            "foreignField": "produit_id", "as": "avis"}},
        {"$addFields": {"note_moyenne": {"$avg": "$avis.note"},
                         "nb_avis": {"$size": "$avis"}}},
        {"$match": {"nb_avis": {"$gt": 0}}},
        {"$sort": {"note_moyenne": -1}},
        {"$limit": limite},
        {"$project": {"nom": 1, "prix": 1, "note_moyenne": 1, "nb_avis": 1, "_id": 0}},
    ]
    return list(db.products.aggregate(pipeline))


def q2_prix_moyen_par_categorie(db):
    """Besoin 2 : quel est le prix moyen des produits par catégorie ?"""
    pipeline = [
        {"$group": {"_id": "$categorie_id", "prix_moyen": {"$avg": "$prix"},
                     "nb_produits": {"$sum": 1}}},
        {"$sort": {"prix_moyen": -1}},
    ]
    return list(db.products.aggregate(pipeline))


def q3_produits_rupture_stock(db):
    """Besoin 3 : quels produits sont en rupture de stock ?"""
    return list(db.products.find({"stock": 0}, {"nom": 1, "categorie_id": 1, "_id": 0}))


def q4_derniers_produits_ajoutes(db, limite=10):
    """Besoin 4 : quels sont les 10 produits les plus récemment ajoutés ?"""
    return list(db.products.find({}, {"nom": 1, "date_ajout": 1, "_id": 0})
                .sort("date_ajout", -1).limit(limite))


def q5_utilisateurs_plus_actifs(db, limite=5):
    """Besoin 5 : quels utilisateurs ont laissé le plus d'avis ?"""
    pipeline = [
        {"$group": {"_id": "$utilisateur_id", "nb_avis": {"$sum": 1}}},
        {"$sort": {"nb_avis": -1}},
        {"$limit": limite},
        {"$lookup": {"from": "users", "localField": "_id",
                     "foreignField": "_id", "as": "utilisateur"}},
        {"$unwind": "$utilisateur"},
        {"$project": {"pseudo": "$utilisateur.pseudo", "nb_avis": 1, "_id": 0}},
    ]
    return list(db.reviews.aggregate(pipeline))


def q6_repartition_notes_produit(db, produit_id):
    """Besoin 6 : répartition des notes (1 à 5) pour un produit donné."""
    pipeline = [
        {"$match": {"produit_id": produit_id}},
        {"$group": {"_id": "$note", "nb": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    return list(db.reviews.aggregate(pipeline))


def q7_produits_par_fourchette_prix(db, prix_min, prix_max):
    """Besoin 7 : quels produits ont un prix compris entre X et Y ?"""
    return list(db.products.find(
        {"prix": {"$gte": prix_min, "$lte": prix_max}},
        {"nom": 1, "prix": 1, "_id": 0}).sort("prix", 1))


def q8_categories_plus_populaires(db):
    """Besoin 8 : quelles catégories comptent le plus de produits ?"""
    pipeline = [
        {"$group": {"_id": "$categorie_id", "nb_produits": {"$sum": 1}}},
        {"$sort": {"nb_produits": -1}},
    ]
    return list(db.products.aggregate(pipeline))


def q9_produits_avis_negatifs(db):
    """Besoin 9 : quels produits ont reçu au moins un avis négatif (note <= 2) ?"""
    pipeline = [
        {"$match": {"note": {"$lte": 2}}},
        {"$group": {"_id": "$produit_id", "nb_avis_negatifs": {"$sum": 1}}},
        {"$lookup": {"from": "products", "localField": "_id",
                     "foreignField": "_id", "as": "produit"}},
        {"$unwind": "$produit"},
        {"$project": {"nom": "$produit.nom", "nb_avis_negatifs": 1, "_id": 0}},
        {"$sort": {"nb_avis_negatifs": -1}},
    ]
    return list(db.reviews.aggregate(pipeline))


def q10_produit_extreme_par_categorie(db):
    """Besoin 10 : produit le plus cher et le moins cher par catégorie."""
    pipeline = [
        {"$sort": {"prix": 1}},
        {"$group": {
            "_id": "$categorie_id",
            "moins_cher": {"$first": {"nom": "$nom", "prix": "$prix"}},
            "plus_cher": {"$last": {"nom": "$nom", "prix": "$prix"}},
        }},
    ]
    return list(db.products.aggregate(pipeline))


def q11_utilisateurs_multi_categories(db, min_categories=2):
    """Besoin 11 : utilisateurs ayant évalué des produits dans plusieurs catégories."""
    pipeline = [
        {"$lookup": {"from": "products", "localField": "produit_id",
                     "foreignField": "_id", "as": "produit"}},
        {"$unwind": "$produit"},
        {"$group": {"_id": "$utilisateur_id",
                     "categories": {"$addToSet": "$produit.categorie_id"}}},
        {"$addFields": {"nb_categories": {"$size": "$categories"}}},
        {"$match": {"nb_categories": {"$gte": min_categories}}},
        {"$sort": {"nb_categories": -1}},
    ]
    return list(db.reviews.aggregate(pipeline))


def q12_evolution_avis_par_mois(db):
    """Besoin 12 : évolution du nombre d'avis déposés, par mois."""
    pipeline = [
        {"$group": {
            "_id": {"annee": {"$year": "$date"}, "mois": {"$month": "$date"}},
            "nb_avis": {"$sum": 1}}},
        {"$sort": {"_id.annee": 1, "_id.mois": 1}},
    ]
    return list(db.reviews.aggregate(pipeline))


def q13_produits_sans_avis(db):
    """Besoin 13 : quels produits n'ont reçu aucun avis ?"""
    pipeline = [
        {"$lookup": {"from": "reviews", "localField": "_id",
                     "foreignField": "produit_id", "as": "avis"}},
        {"$match": {"avis": {"$size": 0}}},
        {"$project": {"nom": 1, "categorie_id": 1, "_id": 0}},
    ]
    return list(db.products.aggregate(pipeline))


def q14_marques_les_plus_representees(db, limite=5):
    """Besoin 14 : quelles marques sont les plus représentées dans le catalogue ?"""
    pipeline = [
        {"$group": {"_id": "$marque", "nb_produits": {"$sum": 1}}},
        {"$sort": {"nb_produits": -1}},
        {"$limit": limite},
    ]
    return list(db.products.aggregate(pipeline))


def q15_satisfaction_moyenne_globale(db):
    """Besoin 15 : quel est le taux de satisfaction moyen, tous produits confondus ?"""
    pipeline = [
        {"$group": {"_id": None, "note_moyenne_globale": {"$avg": "$note"},
                     "nb_avis_total": {"$sum": 1}}},
        {"$project": {"_id": 0}},
    ]
    result = list(db.reviews.aggregate(pipeline))
    return result[0] if result else {}
