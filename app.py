import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Tennis Analyzer Pro", layout="wide", page_icon="🎾")

if 'match_data' not in st.session_state: st.session_state.match_data = []
if 'score' not in st.session_state: st.session_state.score = {"pA_points": 0, "pB_points": 0, "pA_jeux": 0, "pB_jeux": 0, "pA_sets": 0, "pB_sets": 0}
if 'score_history' not in st.session_state: st.session_state.score_history = []

st.sidebar.header("⚙️ Configuration")
player_a = st.sidebar.text_input("Joueur A", value="Joueur A")
player_b = st.sidebar.text_input("Joueur B", value="Joueur B")

if st.sidebar.button("🗑️ Réinitialiser le match", type="primary"):
    st.session_state.match_data, st.session_state.score_history = [], []
    st.session_state.score = {"pA_points": 0, "pB_points": 0, "pA_jeux": 0, "pB_jeux": 0, "pA_sets": 0, "pB_sets": 0}
    st.rerun()

def update_score(winner):
    sc = st.session_state.score
    st.session_state.score_history.append(sc.copy())
    if winner == player_a: sc["pA_points"] += 1
    else: sc["pB_points"] += 1
    if sc["pA_points"] >= 4 and (sc["pA_points"] - sc["pB_points"]) >= 2: sc["pA_jeux"] += 1; sc["pA_points"], sc["pB_points"] = 0, 0
    elif sc["pB_points"] >= 4 and (sc["pB_points"] - sc["pA_points"]) >= 2: sc["pB_jeux"] += 1; sc["pA_points"], sc["pB_points"] = 0, 0
    if (sc["pA_jeux"] >= 6 and (sc["pA_jeux"] - sc["pB_jeux"]) >= 2) or (sc["pA_jeux"] == 7 and sc["pB_jeux"] == 6): sc["pA_sets"] += 1; sc["pA_jeux"], sc["pB_jeux"] = 0, 0
    elif (sc["pB_jeux"] >= 6 and (sc["pB_jeux"] - sc["pA_jeux"]) >= 2) or (sc["pB_jeux"] == 7 and sc["pA_jeux"] == 6): sc["pB_sets"] += 1; sc["pA_jeux"], sc["pB_jeux"] = 0, 0

def undo_last_point():
    if st.session_state.match_data and st.session_state.score_history:
        st.session_state.match_data.pop()
        st.session_state.score = st.session_state.score_history.pop()
        st.toast("↩️ Dernier point annulé !", icon="✅")

def get_pts(pa, pb):
    if pa >= 3 and pb >= 3:
        if pa == pb: return "40", "40"
        return ("Avantage", "40") if pa > pb else ("40", "Avantage")
    return {0:"0", 1:"15", 2:"30", 3:"40"}[pa], {0:"0", 1:"15", 2:"30", 3:"40"}[pb]

st.title("🎾 Tennis Match Analyzer Pro")
score_placeholder = st.empty()

def render_score_board():
    sc = st.session_state.score
    pt_a, pt_b = get_pts(sc["pA_points"], sc["pB_points"])
    with score_placeholder.container():
        c1, c2 = st.columns(2)
        c1.markdown(f"**🔴 {player_a}** | Sets: `{sc['pA_sets']}` | Jeux: `{sc['pA_jeux']}` | Pts: `{pt_a}`")
        c2.markdown(f"**🔵 {player_b}** | Sets: `{sc['pB_sets']}` | Jeux: `{sc['pB_jeux']}` | Pts: `{pt_b}`")

render_score_board()

col_undo, _ = st.columns(2)
with col_undo:
    if st.button("↩️ Annuler le dernier point", use_container_width=True, disabled=len(st.session_state.match_data) == 0):
        undo_last_point(); render_score_board(); st.rerun()

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["🕹️ Enregistrement En Direct", "📊 Analyse Technique", "📋 Journal & Export Excel"])

with tab1:
    st.write("Sélectionnez l'action pour enregistrer le point :")
    def log_event(winner_of_point, player_who_erred, type_action, side="N/A"):
        update_score(winner_of_point)
        st.session_state.match_data.append({"Gagnant du point": winner_of_point, "Joueur ayant fait l'action/erreur": player_who_erred, "Type d'action": type_action, "Côté du coup": side})
        render_score_board(); st.rerun()
    
    colA, colB = st.columns(2)
    with colA:
        st.write(f"**Actions de {player_a}**")
        if st.button("🔥 Winner CD", key="w_cd_a"): log_event(player_a, player_a, "Winner", "Coup Droit")
        if st.button("🔥 Winner REV", key="w_rev_a"): log_event(player_a, player_a, "Winner", "Revers")
        if st.button("📉 Faute Directe CD", key="ue_cd_a"): log_event(player_b, player_a, "Faute Directe", "Coup Droit")
        if st.button("📉 Faute Directe REV", key="ue_rev_a"): log_event(player_b, player_a, "Faute Directe", "Revers")
        if st.button("🛡️ Faute Prov. CD", key="fe_cd_a"): log_event(player_b, player_a, "Faute Provoquée", "Coup Droit")
        if st.button("🛡️ Faute Prov. REV", key="fe_rev_a"): log_event(player_b, player_a, "Faute Provoquée", "Revers")
        if st.button("🎯 Ace", key="ace_a"): log_event(player_a, player_a, "Ace", "Service")
        if st.button("❌ Double Faute", key="df_a"): log_event(player_b, player_a, "Double Faute", "Service")
    with colB:
        st.write(f"**Actions de {player_b}**")
        if st.button("🔥 Winner CD ", key="w_cd_b"): log_event(player_b, player_b, "Winner", "Coup Droit")
        if st.button("🔥 Winner REV ", key="w_rev_b"): log_event(player_b, player_b, "Winner", "Revers")
        if st.button("📉 Faute Directe CD ", key="ue_cd_b"): log_event(player_a, player_b, "Faute Directe", "Coup Droit")
        if st.button("📉 Faute Directe REV ", key="ue_rev_b"): log_event(player_a, player_b, "Faute Directe", "Revers")
        if st.button("🛡️ Faute Prov. CD ", key="fe_cd_b"): log_event(player_a, player_b, "Faute Provoquée", "Coup Droit")
        if st.button("🛡️ Faute Prov. REV ", key="fe_rev_b"): log_event(player_a, player_b, "Faute Provoquée", "Revers")
        if st.button("🎯 Ace ", key="ace_b"): log_event(player_b, player_b, "Ace", "Service")
        if st.button("❌ Double Faute ", key="df_b"): log_event(player_a, player_b, "Double Faute", "Service")

df = pd.DataFrame(st.session_state.match_data)
with tab2:
    if df.empty: st.info("Enregistrez des points pour générer le radar.")
    else:
        def calc(p, t, c): return len(df[(df["Joueur ayant fait l'action/erreur"] == p) & (df["Type d'action"] == t) & (df["Côté du coup"] == c)])
        w_cd_a, w_rev_a = calc(player_a, "Winner", "Coup Droit"), calc(player_a, "Winner", "Revers")
        ue_cd_a, ue_rev_a = calc(player_a, "Faute Directe", "Coup Droit"), calc(player_a, "Faute Directe", "Revers")
        fe_cd_a, fe_rev_a = calc(player_a, "Faute Provoquée", "Coup Droit"), calc(player_a, "Faute Provoquée", "Revers")
        w_cd_b, w_rev_b = calc(player_b, "Winner", "Coup Droit"), calc(player_b, "Winner", "Revers")
        ue_cd_b, ue_rev_b = calc(player_b, "Faute Directe", "Coup Droit"), calc(player_b, "Faute Directe", "Revers")
        fe_cd_b, fe_rev_b = calc(player_b, "Faute Provoquée", "Coup Droit"), calc(player_b, "Faute Provoquée", "Revers")
        categories = ['Win CD', 'Win REV', 'Faute CD', 'Faute REV', 'Prov CD', 'Prov REV']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[w_cd_a, w_rev_a, ue_cd_a, ue_rev_a, fe_cd_a, fe_rev_a], theta=categories, fill='toself', name=player_a, line_color="#ef553b"))
        fig.add_trace(go.Scatterpolar(r=[w_cd_b, w_rev_b, ue_cd_b, ue_rev_b, fe_cd_b, fe_rev_b], theta=categories, fill='toself', name=player_b, line_color="#636efa"))
        st.plotly_chart(fig, key="stable_radar_chart")

with tab3:
    if df.empty: st.info("Aucun point collecté. Saisissez vos données dans le premier onglet pour activer l'export.")
    else:
        st.subheader("📋 Historique complet des points")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("### 💾 Exporter les Statistiques du Match")
        
        ace_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Ace")])
        df_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Double Faute")])
        ace_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Ace")])
        df_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Double Faute")])
        
        w_cd_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Winner") & (df["Côté du coup"] == "Coup Droit")])
        w_rev_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Winner") & (df["Côté du coup"] == "Revers")])
        ue_cd_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Faute Directe") & (df["Côté du coup"] == "Coup Droit")])
        ue_rev_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Faute Directe") & (df["Côté du coup"] == "Revers")])
        fe_cd_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Faute Provoquée") & (df["Côté du coup"] == "Coup Droit")])
        fe_rev_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Faute Provoquée") & (df["Côté du coup"] == "Revers")])
        w_cd_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Winner") & (df["Côté du coup"] == "Coup Droit")])
        w_rev_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Winner") & (df["Côté du coup"] == "Revers")])
        ue_cd_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Faute Directe") & (df["Côté du coup"] == "Coup Droit")])
        ue_rev_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Faute Directe") & (df["Côté du coup"] == "Revers")])
        fe_cd_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Faute Provoquée") & (df["Côté du coup"] == "Coup Droit")])
        fe_rev_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Faute Provoquée") & (df["Côté du coup"] == "Revers")])

        summary_data = {
            "Indicateur Metrique": [
                "Aces", "Double Fautes", "Winners Coup Droit", "Winners Revers",
                "Fautes Directes Coup Droit", "Fautes Directes Revers",
                "Fautes Provoquees Coup Droit", "Fautes Provoquees Revers"
            ],
            player_a: [ace_a, df_a, w_cd_a, w_rev_a, ue_cd_a, ue_rev_a, fe_cd_a, fe_rev_a],
            player_b: [ace_b, df_b, w_cd_b, w_rev_b, ue_cd_b, ue_rev_b, fe_cd_b, fe_rev_b]
        }
        df_summary_excel = pd.DataFrame(summary_data)
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_summary_excel.to_excel(writer, sheet_name='Synthese Globale', index=False)
            df.to_excel(writer, sheet_name='Journal Point par Point', index=False)
            
        st.write("Générez un rapport propre téléchargeable directement sur votre ordinateur ou mobile :")
        st.download_button(
            label="📥 Télécharger le rapport Excel complet (.xlsx)",
            data=excel_buffer.getvalue(),
            file_name=f"rapport_tennis_{player_a}vs{player_b}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
