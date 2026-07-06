"""
app_web.py — Interface web Streamlit pour explorer le catalogue.

Lancement (dans un terminal, en parallèle de l'API) :
    python api.py            # terminal 1
    streamlit run app_web.py # terminal 2
"""
import streamlit as st
import pandas as pd
import requests
import plotly.express as px

API_URL = "http://localhost:5000/api"

st.set_page_config(
    page_title="Catalogue Produits NoSQL",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# STYLE — palette + cartes + tableaux
# ------------------------------------------------------------------
PRIMARY = "#4F6BFF"
PRIMARY_DARK = "#2C3E8A"
BG_CARD = "#F7F8FC"

st.markdown(f"""
<style>
    .stApp {{
        background: #FAFBFF;
    }}
    /* Titre principal */
    .hero {{
        background: linear-gradient(135deg, {PRIMARY} 0%, {PRIMARY_DARK} 100%);
        padding: 2rem 2.2rem;
        border-radius: 18px;
        margin-bottom: 1.6rem;
        box-shadow: 0 8px 24px rgba(79,107,255,0.25);
    }}
    .hero h1 {{
        color: white;
        font-size: 2rem;
        margin: 0;
    }}
    .hero p {{
        color: #E4E9FF;
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
    }}
    /* Cartes metric */
    div[data-testid="stMetric"] {{
        background: {BG_CARD};
        border: 1px solid #E6E9F5;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(30,40,90,0.05);
    }}
    div[data-testid="stMetricLabel"] {{
        color: #6B7290;
        font-weight: 600;
    }}
    div[data-testid="stMetricValue"] {{
        color: {PRIMARY_DARK};
    }}
    /* Sous-titres de section */
    .section-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: {PRIMARY_DARK};
        margin: 1.2rem 0 0.6rem 0;
        border-left: 4px solid {PRIMARY};
        padding-left: 0.6rem;
    }}
    /* Onglets */
    button[data-baseweb="tab"] {{
        font-weight: 600;
        font-size: 0.95rem;
    }}
    /* Dataframes */
    div[data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #E6E9F5;
    }}
    /* Cacher le menu/footer par défaut de Streamlit */
    #MainMenu, footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

CHART_COLORS = ["#4F6BFF", "#7C9CFF", "#FFB020", "#FF6B6B", "#2CC5A5"]


def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


@st.cache_data(ttl=30)
def get(endpoint, params=None):
    return requests.get(f"{API_URL}/{endpoint}", params=params).json()


# ------------------------------------------------------------------
# EN-TÊTE
# ------------------------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>🛍️ Catalogue de produits — Tableau de bord</h1>
    <p>Démo NoSQL : MongoDB (simulé) · API Flask · Interface Streamlit</p>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "📊  Vue d'ensemble", "🏷️  Par catégorie", "📦  Produits",
    "👥  Utilisateurs", "⭐  Avis",
])

# ---------- Vue d'ensemble ----------
with tabs[0]:
    sat = get("satisfaction-globale")
    marques = pd.DataFrame(get("marques/populaires"))
    rupture = get("produits/rupture-stock")

    c1, c2, c3 = st.columns(3)
    c1.metric("⭐ Note moyenne globale", f"{sat.get('note_moyenne_globale', 0):.2f} / 5")
    c2.metric("💬 Total des avis", sat.get("nb_avis_total", 0))
    c3.metric("🚫 Produits en rupture", len(rupture))

    col1, col2 = st.columns(2)
    with col1:
        section("Prix moyen par catégorie")
        df = pd.DataFrame(get("produits/prix-moyen-categorie")).rename(columns={"_id": "catégorie"})
        fig = px.bar(df, x="catégorie", y="prix_moyen", text_auto=".2s",
                     color="catégorie", color_discrete_sequence=CHART_COLORS)
        fig.update_layout(showlegend=False, margin=dict(t=10, l=0, r=0, b=0),
                           plot_bgcolor="white", yaxis_title="Prix moyen (€)", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        section("Nombre de produits par catégorie")
        df = pd.DataFrame(get("categories/populaires")).rename(columns={"_id": "catégorie"})
        fig = px.pie(df, names="catégorie", values="nb_produits", hole=0.55,
                     color_discrete_sequence=CHART_COLORS)
        fig.update_layout(margin=dict(t=10, l=0, r=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    section("Top marques du catalogue")
    st.dataframe(marques.rename(columns={"_id": "Marque", "nb_produits": "Nb produits"}),
                 use_container_width=True, hide_index=True)

# ---------- Par catégorie ----------
with tabs[1]:
    cats = get("categories")
    noms = {c["nom"]: c["_id"] for c in cats}
    choix = st.selectbox("Choisir une catégorie", list(noms.keys()))
    cat_id = noms[choix]

    section(f"🏆 Produits les mieux notés — {choix}")
    top = pd.DataFrame(get(f"categories/{cat_id}/top-produits"))
    if not top.empty:
        st.dataframe(
            top.rename(columns={"nom": "Produit", "prix": "Prix (€)",
                                 "note_moyenne": "Note moyenne", "nb_avis": "Nb avis"}),
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("Aucun produit noté dans cette catégorie pour le moment.")

    section("💰 Extrêmes de prix par catégorie")
    extremes = get("categories/extremes-prix")
    ex_rows = [{
        "Catégorie": e["_id"],
        "Moins cher": f"{e['moins_cher']['nom']} — {e['moins_cher']['prix']} €",
        "Plus cher": f"{e['plus_cher']['nom']} — {e['plus_cher']['prix']} €",
    } for e in extremes]
    st.dataframe(pd.DataFrame(ex_rows), use_container_width=True, hide_index=True)

# ---------- Produits ----------
with tabs[2]:
    section("🔍 Filtrer par fourchette de prix")
    c1, c2 = st.columns(2)
    prix_min = c1.number_input("Prix minimum (€)", value=0.0, step=5.0)
    prix_max = c2.number_input("Prix maximum (€)", value=500.0, step=5.0)
    resultats = pd.DataFrame(get("produits/prix", {"min": prix_min, "max": prix_max}))
    st.dataframe(resultats.rename(columns={"nom": "Produit", "prix": "Prix (€)"}),
                 use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        section("🚫 Produits en rupture de stock")
        st.dataframe(pd.DataFrame(get("produits/rupture-stock")).rename(
            columns={"nom": "Produit", "categorie_id": "Catégorie"}),
            use_container_width=True, hide_index=True)
    with col2:
        section("🕵️ Produits sans aucun avis")
        st.dataframe(pd.DataFrame(get("produits/sans-avis")).rename(
            columns={"nom": "Produit", "categorie_id": "Catégorie"}),
            use_container_width=True, hide_index=True)

    section("🆕 Derniers produits ajoutés")
    st.dataframe(pd.DataFrame(get("produits/derniers")).rename(
        columns={"nom": "Produit", "date_ajout": "Date d'ajout"}),
        use_container_width=True, hide_index=True)

# ---------- Utilisateurs ----------
with tabs[3]:
    col1, col2 = st.columns(2)
    with col1:
        section("🏅 Utilisateurs les plus actifs")
        st.dataframe(pd.DataFrame(get("utilisateurs/plus-actifs")).rename(
            columns={"pseudo": "Utilisateur", "nb_avis": "Nb avis"}),
            use_container_width=True, hide_index=True)
    with col2:
        section("🌐 Utilisateurs actifs sur plusieurs catégories")
        multi = pd.DataFrame(get("utilisateurs/multi-categories"))
        if not multi.empty:
            multi["categories"] = multi["categories"].apply(lambda l: ", ".join(l))
            st.dataframe(multi.rename(
                columns={"_id": "Utilisateur", "categories": "Catégories", "nb_categories": "Nb"}),
                use_container_width=True, hide_index=True)

# ---------- Avis ----------
with tabs[4]:
    section("⚠️ Produits avec au moins un avis négatif")
    st.dataframe(pd.DataFrame(get("produits/avis-negatifs")).rename(
        columns={"nom": "Produit", "nb_avis_negatifs": "Avis négatifs"}),
        use_container_width=True, hide_index=True)

    section("📈 Évolution du nombre d'avis par mois")
    data = get("avis/evolution-mensuelle")
    df = pd.DataFrame(data)
    if not df.empty:
        df["periode"] = df["_id"].apply(lambda d: f"{d['annee']}-{d['mois']:02d}")
        fig = px.line(df, x="periode", y="nb_avis", markers=True,
                       color_discrete_sequence=[PRIMARY])
        fig.update_layout(margin=dict(t=10, l=0, r=0, b=0), plot_bgcolor="white",
                           xaxis_title="", yaxis_title="Nombre d'avis")
        st.plotly_chart(fig, use_container_width=True)
