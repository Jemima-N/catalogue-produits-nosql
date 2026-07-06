from db import get_db
import queries as q

db = get_db()

print("=== Peuplement de la base ===")
print(f"Produits   : {db.products.count_documents({})}")
print(f"Catégories : {db.categories.count_documents({})}")
print(f"Utilisateurs: {db.users.count_documents({})}")
print(f"Avis       : {db.reviews.count_documents({})}")

print("\n1) Meilleurs produits (Électronique) :", q.q1_produits_mieux_notes_par_categorie(db, "cat_electronique"))
print("\n2) Prix moyen par catégorie :", q.q2_prix_moyen_par_categorie(db))
print("\n3) Ruptures de stock :", q.q3_produits_rupture_stock(db))
print("\n4) 5 derniers produits ajoutés :", q.q4_derniers_produits_ajoutes(db, 5))
print("\n5) Utilisateurs les plus actifs :", q.q5_utilisateurs_plus_actifs(db))
print("\n6) Répartition notes (prod_001) :", q.q6_repartition_notes_produit(db, "prod_001"))
print("\n7) Produits entre 20 et 60€ :", q.q7_produits_par_fourchette_prix(db, 20, 60))
print("\n8) Catégories les plus fournies :", q.q8_categories_plus_populaires(db))
print("\n9) Produits avec avis négatifs :", q.q9_produits_avis_negatifs(db))
print("\n10) Extrêmes prix par catégorie :", q.q10_produit_extreme_par_categorie(db))
print("\n11) Utilisateurs multi-catégories :", q.q11_utilisateurs_multi_categories(db))
print("\n12) Évolution avis par mois :", q.q12_evolution_avis_par_mois(db))
print("\n13) Produits sans avis :", q.q13_produits_sans_avis(db))
print("\n14) Marques les plus représentées :", q.q14_marques_les_plus_representees(db))
print("\n15) Satisfaction moyenne globale :", q.q15_satisfaction_moyenne_globale(db))
