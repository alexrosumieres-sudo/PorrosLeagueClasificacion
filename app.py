import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURACIÓN DE LAS JORNADAS ---
JORNADAS = {
    "Jornada 25": [
        ("Athletic", "Elche"), ("R. Sociedad", "Oviedo"), ("Betis", "Rayo"),
        ("Osasuna", "Real Madrid"), ("Atlético", "Espanyol"), ("Getafe", "Sevilla"),
        ("Barcelona", "Levante"), ("Celta", "Mallorca"), ("Villarreal", "Valencia"),
        ("Alavés", "Girona")  # ÚLTIMO PARTIDO
    ],
    "Jornada 26": [
        ("Levante", "Alavés"), ("Rayo", "Athletic"), ("Barcelona", "Villarreal"),
        ("Mallorca", "R. Sociedad"), ("Oviedo", "Atlético"), ("Elche", "Espanyol"),
        ("Valencia", "Osasuna"), ("Betis", "Sevilla"), ("Girona", "Celta"),
        ("Real Madrid", "Getafe")  # ÚLTIMO PARTIDO
    ],
    "Jornada 27": [
        ("Osasuna", "Mallorca"), ("Getafe", "Betis"), ("Levante", "Girona"),
        ("Atlético", "R. Sociedad"), ("Celta", "Real Madrid"), ("Villarreal", "Elche"),
        ("Athletic", "Barcelona"), ("Sevilla", "Rayo"), ("Valencia", "Alavés"),
        ("Espanyol", "Oviedo")  # ÚLTIMO PARTIDO
    ]
}

# --- LÓGICA DE PUNTUACIÓN ---
def calcular_puntos(p_l, p_v, r_l, r_v, es_ultimo=False):
    # Si no hay resultado real todavía, 0 puntos
    if pd.isna(r_l) or pd.isna(r_v): return 0
    
    m = 3.0 if es_ultimo else 1.0  # Multiplicador resultado exacto
    m_diff = 1.5 if es_ultimo else 0.75 # Multiplicador diferencia
    m_win = 1.0 if es_ultimo else 0.5  # Multiplicador acierto simple

    # 1. Resultado exacto
    if p_l == r_l and p_v == r_v:
        return m
    
    # Calcular signos (1: gana local, 0: empate, -1: gana visitante)
    signo_p = (p_l > p_v) - (p_l < p_v)
    signo_r = (r_l > r_v) - (r_l < r_v)
    
    if signo_p == signo_r:
        # 2. Diferencia de goles (incluye empates no exactos)
        if (p_l - p_v) == (r_l - r_v):
            return m_diff
        # 3. Solo acierto de quién gana
        else:
            return m_win
            
    return 0.0

# --- INTERFAZ Y CONEXIÓN ---
st.set_page_config(page_title="Liga de Fútbol", page_icon="⚽")
st.title("🏆 Mi Liga de Predicciones")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Sidebar para usuario y jornada
usuario = st.sidebar.text_input("Tu Nombre/ID").strip().capitalize()
jornada_sel = st.sidebar.selectbox("Selecciona Jornada", list(JORNADAS.keys()))

if not usuario:
    st.info("👈 Introduce tu nombre en la barra lateral para empezar.")
else:
    tab1, tab2, tab3 = st.tabs(["✍️ Mis Apuestas", "📊 Clasificación", "⚙️ Admin"])

    # --- TAB 1: MIS APUESTAS ---
    with tab1:
        st.header(f"Predicciones de {usuario}")
        partidos = JORNADAS[jornada_sel]
        
        # Leer datos actuales de Google Sheets para ver si ya apostó
        df_preds = conn.read(worksheet="Predicciones")
        
        preds_actuales = []
        for i, (loc, vis) in enumerate(partidos):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1: st.write(f"**{loc}** vs **{vis}**")
            with col2: pl = st.number_input("Local", min_value=0, step=1, key=f"l_{i}")
            with col3: pv = st.number_input("Visitante", min_value=0, step=1, key=f"v_{i}")
            preds_actuales.append({"Usuario": usuario, "Jornada": jornada_sel, "Partido": f"{loc}-{vis}", "P_L": pl, "P_V": pv})

        if st.button("Guardar Predicciones"):
            # Filtrar para no duplicar (borrar anteriores del mismo usuario y jornada)
            df_final = df_preds[~((df_preds['Usuario'] == usuario) & (df_preds['Jornada'] == jornada_sel))]
            df_final = pd.concat([df_final, pd.DataFrame(preds_actuales)], ignore_index=True)
            
            conn.update(worksheet="Predicciones", data=df_final)
            st.success("¡Tus resultados se han guardado en Google Sheets!")

    # --- TAB 2: CLASIFICACIÓN ---
    with tab2:
        st.header(f"Ranking {jornada_sel}")
        
        df_p = conn.read(worksheet="Predicciones")
        df_r = conn.read(worksheet="Resultados")
        
        # Filtrar por jornada actual
        df_p_j = df_p[df_p['Jornada'] == jornada_sel]
        df_r_j = df_r[df_r['Jornada'] == jornada_sel]
        
        if df_r_j.empty:
            st.warning("El administrador aún no ha subido los resultados reales.")
        else:
            puntos_totales = []
            for user in df_p_j['Usuario'].unique():
                u_preds = df_p_j[df_p_j['Usuario'] == user]
                puntos_usuario = 0
                
                for idx, (loc, vis) in enumerate(partidos):
                    match_name = f"{loc}-{vis}"
                    es_ultimo = (idx == len(partidos)-1)
                    
                    # Buscar predicción y resultado real
                    p_row = u_preds[u_preds['Partido'] == match_name]
                    r_row = df_r_j[df_r_j['Partido'] == match_name]
                    
                    if not p_row.empty and not r_row.empty:
                        puntos_usuario += calcular_puntos(
                            p_row.iloc[0]['P_L'], p_row.iloc[0]['P_V'],
                            r_row.iloc[0]['R_L'], r_row.iloc[0]['R_V'],
                            es_ultimo
                        )
                
                puntos_totales.append({"Usuario": user, "Puntos": puntos_usuario})
            
            ranking = pd.DataFrame(puntos_totales).sort_values(by="Puntos", ascending=False)
            st.table(ranking)

    # --- TAB 3: ADMIN (SUBIR RESULTADOS REALES) ---
    with tab3:
        pass_admin = st.text_input("Contraseña Admin", type="password")
        if pass_admin == "1234": # Cambia esto por lo que quieras
            st.write("Introduce los resultados reales de la jornada:")
            res_reales = []
            for i, (loc, vis) in enumerate(partidos):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1: st.write(f"{loc}-{vis}")
                with col2: rl = st.number_input("R.Local", min_value=0, step=1, key=f"rl_{i}")
                with col3: rv = st.number_input("R.Vis", min_value=0, step=1, key=f"rv_{i}")
                res_reales.append({"Jornada": jornada_sel, "Partido": f"{loc}-{vis}", "R_L": rl, "R_V": rv})
            
            if st.button("Actualizar Resultados Reales"):
                df_res_all = conn.read(worksheet="Resultados")
                # Limpiar anteriores de esta jornada
                df_res_all = df_res_all[df_res_all['Jornada'] != jornada_sel]
                df_res_all = pd.concat([df_res_all, pd.DataFrame(res_reales)], ignore_index=True)
                conn.update(worksheet="Resultados", data=df_res_all)
                st.success("Resultados reales actualizados.")