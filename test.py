import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="WellBeing AI - Advanced", layout="wide")

st.title("🧠 WellBeing AI : Analyse Comportementale & Charge Réelle")
st.markdown("""
Analyse avancée incluant : 
1. **Présence réelle** (Statut Teams).
2. **Qualité des échanges** (Détection de toxicité/stress dans le langage).
3. **Charge cachée** (Identification automatique des demandes de tâches dans les emails).
""")
st.divider()

# --- 1. GÉNÉRATION DE DONNÉES AVANCÉES (SIMULATION) ---
def get_advanced_mock_data():
    employees = ['Alice Dupont', 'Marc Martin', 'Sophie Leroi', 'Jean Durand', 'Claire Petit', 'Thomas Bernard']
    data = []
    
    for emp in employees:
        # Métriques de base
        meeting_hours = np.random.randint(5, 35)
        
        # 1. Présence Teams (Souvent plus élevée que les heures de contrat)
        # Simulation : Des gens connectés de 8h30 à 19h30 = 11h de présence/jour
        teams_active_hours = np.random.normal(40, 8) # Moyenne 40h, écart type 8h
        teams_active_hours = max(teams_active_hours, meeting_hours + 5) # On ne peut pas être moins là que ses réunions
        
        # 2. Score de Sentiment / Toxicité (De -10 à +10)
        # -10 = Très toxique/Stressé, +10 = Très positif
        sentiment_score = np.random.normal(2, 3) 
        if meeting_hours > 30: sentiment_score -= 4 # Trop de réunions rend grognon
        
        # 3. Charge cachée (Extraction NLP des demandes)
        # Nombre de phrases du type "Peux-tu faire ça ?" détectées
        task_requests_received = np.random.randint(5, 25)
        avg_time_per_task = np.random.randint(15, 60) # Minutes estimées par l'IA
        hidden_workload_hours = (task_requests_received * avg_time_per_task) / 60
        
        data.append({
            "Employé": emp,
            "Heures Réunion /sem": meeting_hours,
            "Présence Teams (h)": round(teams_active_hours, 1),
            "Score Ambiance": round(sentiment_score, 1),
            "Tâches Demandées (NLP)": task_requests_received,
            "Charge Cachée (h)": round(hidden_workload_hours, 1)
        })
    return pd.DataFrame(data)

df = get_advanced_mock_data()

# --- 2. CALCUL DU RISQUE (ALGORITHME V2) ---
def calculate_advanced_risk(row):
    score = 0
    alerts = []
    
    # Règle 1 : Présentéisme Digital (Teams)
    # Si présence > 45h ou écart énorme avec le contrat théorique (35h)
    if row['Présence Teams (h)'] > 48:
        score += 35
        alerts.append("Hyper-connexion Teams")
    elif row['Présence Teams (h)'] > 42:
        score += 15
        
    # Règle 2 : Toxicité / Stress détecté dans le texte
    if row['Score Ambiance'] < -2:
        score += 40 # C'est un signal très fort
        alerts.append("Langage Stressé/Toxique")
    elif row['Score Ambiance'] < 0:
        score += 15
        alerts.append("Sentiment Négatif")

    # Règle 3 : La charge totale réelle (Réunions + Tâches demandées)
    total_work_load = row['Heures Réunion /sem'] + row['Charge Cachée (h)']
    if total_work_load > 40:
        score += 30
        alerts.append("Surcharge Tâches + Réunions")
        
    final_score = min(score, 100)
    
    if final_score < 40: level = "🟢 Sain"
    elif final_score < 75: level = "🟡 Risque Modéré"
    else: level = "🔴 Critique"
        
    return pd.Series([final_score, level, ", ".join(alerts), total_work_load])

df[['Score Risque', 'Niveau', 'Alertes', 'Charge Totale Estimée']] = df.apply(calculate_advanced_risk, axis=1)

# --- 3. DASHBOARD ---

# KPIs Globaux
col1, col2, col3, col4 = st.columns(4)
col1.metric("Présence Moyenne Teams", f"{df['Présence Teams (h)'].mean():.1f} h")
col2.metric("Charge Cachée (Demandes)", f"{df['Charge Cachée (h)'].mean():.1f} h", help="Temps estimé pour traiter les demandes reçues par mail/chat")
# Calcul couleur sentiment
avg_sentiment = df['Score Ambiance'].mean()
sent_color = "normal" if avg_sentiment > 0 else "inverse"
col3.metric("Index Ambiance Équipe", f"{avg_sentiment:.1f}", delta="Positif" if avg_sentiment > 0 else "Négatif", delta_color=sent_color)
col4.metric("Employés en Burnout", f"{len(df[df['Niveau']=='🔴 Critique'])}")

st.divider()

# Vue Graphique Avancée
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("🔍 Analyse : Présence vs Charge Cachée")
    # On compare le temps passé connecté vs le travail réel estimé
    fig = px.scatter(df, 
                     x="Présence Teams (h)", 
                     y="Charge Totale Estimée", 
                     color="Niveau",
                     size="Tâches Demandées (NLP)",
                     text="Employé",
                     color_discrete_map={"🟢 Sain": "green", "🟡 Risque Modéré": "orange", "🔴 Critique": "red"},
                     title="Taille de la bulle = Nombre de tâches demandées par email")
    
    # Ligne de référence : Si on est connecté plus longtemps que sa charge de travail, c'est du présentéisme ou de l'inefficacité
    fig.add_shape(type="line", x0=0, y0=0, x1=60, y1=60, line=dict(color="Gray", dash="dashdot"))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Au-dessus de la ligne pointillée : Surcharge réelle. En dessous : Présentéisme potentiel.")

with c2:
    st.subheader("💬 Analyse Sémantique")
    # Bar chart des sentiments
    fig2 = px.bar(df, x='Employé', y='Score Ambiance', 
                  color='Score Ambiance',
                  color_continuous_scale=['red', 'yellow', 'green'],
                  title="Positivité des échanges")
    st.plotly_chart(fig2, use_container_width=True)

# --- 4. FOCUS INDIVIDUEL ET NLP ---
st.divider()
st.subheader("🧠 Analyseur de Charge Cognitive (NLP Simulation)")

selected_emp = st.selectbox("Analyser le détail pour :", df['Employé'])
emp_row = df[df['Employé'] == selected_emp].iloc[0]

c_info1, c_info2 = st.columns(2)

with c_info1:
    st.info(f"**Statut Actuel : {emp_row['Niveau']}**")
    st.write(f"Alertes détectées : **{emp_row['Alertes'] if emp_row['Alertes'] else 'Aucune'}**")
    st.progress(int(emp_row['Score Risque']))

with c_info2:
    st.write("### 📥 Dernières demandes détectées (Exemple IA)")
    # Simulation de ce que l'IA aurait extrait des emails
    if emp_row['Tâches Demandées (NLP)'] > 15:
        mock_tasks = [
            "⚠️ 'Peux-tu me livrer le rapport financier pour demain 8h ?' (Urgent, Est: 2h)",
            "📅 'Merci de préparer la présentation client pour lundi.' (Moyen, Est: 3h)",
            "🔄 'Revois tous les calculs du fichier Excel v3.' (Complexe, Est: 4h)"
        ]
        for task in mock_tasks:
            st.warning(task)
        st.write(f"*+ {int(emp_row['Tâches Demandées (NLP)'] - 3)} autres demandes mineures...*")
    else:
        st.success("Volume de demandes entrant raisonnable cette semaine.")
