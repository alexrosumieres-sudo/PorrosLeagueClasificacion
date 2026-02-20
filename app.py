import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time
import os
import plotly.express as px

# --- 1. CONFIGURACIONES GENERALES ---
PERFILES_DIR = "perfiles/"
LOGOS_DIR = "logos/"

NIVEL_EQUIPOS = {
    "Real Madrid": 1, "Barcelona": 1, "Villarreal": 1, "Atlético": 1,
    "Betis": 2, "Espanyol": 2, "Celta": 2, "R. Sociedad": 2, "Athletic": 2,
    "Osasuna": 3, "Getafe": 3, "Girona": 3, "Sevilla": 3, "Alavés": 3, "Valencia": 3, "Elche": 3, "Rayo": 3,
    "Mallorca": 4, "Levante": 4, "Oviedo": 4
}

# Datos base oficiales de la Jornada 24
STATS_LALIGA_BASE = {
    "Real Madrid": {"PJ": 24, "V": 19, "E": 3, "D": 2, "GF": 53, "GC": 19, "Pts": 60},
    "Barcelona": {"PJ": 24, "V": 19, "E": 1, "D": 4, "GF": 64, "GC": 25, "Pts": 58},
    "Villarreal": {"PJ": 24, "V": 15, "E": 3, "D": 6, "GF": 45, "GC": 26, "Pts": 48},
    "Atlético": {"PJ": 24, "V": 13, "E": 6, "D": 5, "GF": 38, "GC": 21, "Pts": 45},
    "Betis": {"PJ": 24, "V": 11, "E": 8, "D": 5, "GF": 39, "GC": 29, "Pts": 41},
    "Espanyol": {"PJ": 24, "V": 10, "E": 5, "D": 9, "GF": 29, "GC": 33, "Pts": 35},
    "Celta": {"PJ": 24, "V": 8, "E": 10, "D": 6, "GF": 32, "GC": 27, "Pts": 34},
    "R. Sociedad": {"PJ": 24, "V": 8, "E": 7, "D": 9, "GF": 34, "GC": 35, "Pts": 31},
    "Athletic": {"PJ": 24, "V": 9, "E": 4, "D": 11, "GF": 27, "GC": 34, "Pts": 31},
    "Osasuna": {"PJ": 24, "V": 8, "E": 6, "D": 10, "GF": 28, "GC": 28, "Pts": 30},
    "Getafe": {"PJ": 24, "V": 8, "E": 5, "D": 11, "GF": 20, "GC": 28, "Pts": 29},
    "Girona": {"PJ": 24, "V": 7, "E": 8, "D": 9, "GF": 24, "GC": 38, "Pts": 29},
    "Sevilla": {"PJ": 24, "V": 7, "E": 5, "D": 12, "GF": 31, "GC": 39, "Pts": 26},
    "Alavés": {"PJ": 24, "V": 7, "E": 5, "D": 12, "GF": 21, "GC": 30, "Pts": 26},
    "Valencia": {"PJ": 24, "V": 6, "E": 8, "D": 10, "GF": 25, "GC": 37, "Pts": 26},
    "Elche": {"PJ": 24, "V": 5, "E": 10, "D": 9, "GF": 31, "GC": 35, "Pts": 25},
    "Rayo": {"PJ": 23, "V": 6, "E": 7, "D": 10, "GF": 21, "GC": 30, "Pts": 25},
    "Mallorca": {"PJ": 24, "V": 6, "E": 6, "D": 12, "GF": 29, "GC": 39, "Pts": 24},
    "Levante": {"PJ": 24, "V": 4, "E": 6, "D": 14, "GF": 26, "GC": 41, "Pts": 18},
    "Oviedo": {"PJ": 23, "V": 3, "E": 7, "D": 13, "GF": 13, "GC": 36, "Pts": 16},
}

JORNADAS = {
    "Jornada 25": [("Athletic", "Elche"), ("R. Sociedad", "Oviedo"), ("Betis", "Rayo"), ("Osasuna", "Real Madrid"), ("Atlético", "Espanyol"), ("Getafe", "Sevilla"), ("Barcelona", "Levante"), ("Celta", "Mallorca"), ("Villarreal", "Valencia"), ("Alavés", "Girona")],
    "Jornada 26": [("Levante", "Alavés"), ("Rayo", "Athletic"), ("Barcelona", "Villarreal"), ("Mallorca", "R. Sociedad"), ("Oviedo", "Atlético"), ("Elche", "Espanyol"), ("Valencia", "Osasuna"), ("Betis", "Sevilla"), ("Girona", "Celta"), ("Real Madrid", "Getafe")],
    "Jornada 27": [("Osasuna", "Mallorca"), ("Getafe", "Betis"), ("Levante", "Girona"), ("Atlético", "R. Sociedad"), ("Celta", "Real Madrid"), ("Villarreal", "Elche"), ("Athletic", "Barcelona"), ("Sevilla", "Rayo"), ("Valencia", "Alavés"), ("Espanyol", "Oviedo")],
    "Jornada 28": [("Alavés", "Villarreal"), ("Girona", "Athletic"), ("Atlético", "Getafe"), ("Oviedo", "Valencia"), ("Real Madrid", "Elche"), ("Mallorca", "Espanyol"), ("Barcelona", "Sevilla"), ("Betis", "Celta"), ("Osasuna", "Rayo"), ("Levante", "R. Sociedad")],
    "Jornada 29": [("Athletic", "Betis"), ("Barcelona", "Rayo"), ("Celta", "Alavés"), ("Elche", "Mallorca"), ("Espanyol", "Getafe"), ("Levante", "Oviedo"), ("Osasuna", "Girona"), ("Real Madrid", "Atlético"), ("Sevilla", "Valencia"), ("Villarreal", "R. Sociedad")],
    "Jornada 30": [("Alavés", "Osasuna"), ("Atlético", "Barcelona"), ("Getafe", "Athletic"), ("Girona", "Villarreal"), ("Mallorca", "Real Madrid"), ("Rayo", "Elche"), ("Betis", "Espanyol"), ("Oviedo", "Sevilla"), ("R. Sociedad", "Levante"), ("Valencia", "Celta")],
    "Jornada 31": [("Athletic", "Villarreal"), ("Barcelona", "Espanyol"), ("Celta", "Oviedo"), ("Elche", "Valencia"), ("Levante", "Getafe"), ("Mallorca", "Rayo"), ("Osasuna", "Betis"), ("Real Madrid", "Girona"), ("R. Sociedad", "Alavés"), ("Sevilla", "Atlético")],
    "Jornada 32": [("Alavés", "Mallorca"), ("Atlético", "Athletic"), ("Espanyol", "Levante"), ("Getafe", "Barcelona"), ("Osasuna", "Sevilla"), ("Rayo", "R. Sociedad"), ("Betis", "Real Madrid"), ("Oviedo", "Elche"), ("Valencia", "Girona"), ("Villarreal", "Celta")],
    "Jornada 33": [("Athletic", "Osasuna"), ("Barcelona", "Celta"), ("Elche", "Atlético"), ("Girona", "Betis"), ("Levante", "Sevilla"), ("Mallorca", "Valencia"), ("Rayo", "Espanyol"), ("Real Madrid", "Alavés"), ("Oviedo", "Villarreal"), ("R. Sociedad", "Getafe")],
    "Jornada 34": [("Alavés", "Athletic"), ("Celta", "Elche"), ("Espanyol", "Real Madrid"), ("Getafe", "Rayo"), ("Girona", "Mallorca"), ("Osasuna", "Barcelona"), ("Betis", "Oviedo"), ("Sevilla", "R. Sociedad"), ("Valencia", "Atlético"), ("Villarreal", "Levante")],
    "Jornada 35": [("Athletic", "Valencia"), ("Atlético", "Celta"), ("Barcelona", "Real Madrid"), ("Elche", "Alavés"), ("Levante", "Osasuna"), ("Mallorca", "Villarreal"), ("Rayo", "Girona"), ("Oviedo", "Getafe"), ("R. Sociedad", "Betis"), ("Sevilla", "Espanyol")],
    "Jornada 36": [("Alavés", "Barcelona"), ("Celta", "Levante"), ("Espanyol", "Athletic"), ("Getafe", "Mallorca"), ("Girona", "R. Sociedad"), ("Osasuna", "Atlético"), ("Betis", "Elche"), ("Real Madrid", "Oviedo"), ("Valencia", "Rayo"), ("Villarreal", "Sevilla")],
    "Jornada 37": [("Athletic", "Celta"), ("Atlético", "Girona"), ("Barcelona", "Betis"), ("Elche", "Getafe"), ("Levante", "Mallorca"), ("Osasuna", "Espanyol"), ("Rayo", "Villarreal"), ("Oviedo", "Alavés"), ("R. Sociedad", "Valencia"), ("Sevilla", "Real Madrid")],
    "Jornada 38": [("Alavés", "Rayo"), ("Celta", "Sevilla"), ("Espanyol", "R. Sociedad"), ("Getafe", "Osasuna"), ("Girona", "Elche"), ("Mallorca", "Oviedo"), ("Betis", "Levante"), ("Real Madrid", "Athletic"), ("Valencia", "Barcelona"), ("Villarreal", "Atlético")]
}

LOGOS = {
    "Athletic": f"{LOGOS_DIR}athletic.jpeg", "Elche": f"{LOGOS_DIR}elche.jpeg", "R. Sociedad": f"{LOGOS_DIR}sociedad.jpeg",
    "Real Madrid": f"{LOGOS_DIR}madrid.jpeg", "Barcelona": f"{LOGOS_DIR}barca.jpeg", "Atlético": f"{LOGOS_DIR}atletico.jpeg",
    "Rayo": f"{LOGOS_DIR}rayo.jpeg", "Sevilla": f"{LOGOS_DIR}sevilla.jpeg", "Valencia": f"{LOGOS_DIR}valencia.jpeg",
    "Girona": f"{LOGOS_DIR}girona.jpeg", "Osasuna": f"{LOGOS_DIR}osasuna.jpeg", "Getafe": f"{LOGOS_DIR}getafe.jpeg",
    "Celta": f"{LOGOS_DIR}celta.jpeg", "Mallorca": f"{LOGOS_DIR}mallorca.jpeg", "Villarreal": f"{LOGOS_DIR}villarreal.jpeg",
    "Alavés": f"{LOGOS_DIR}alaves.jpeg", "Espanyol": f"{LOGOS_DIR}espanyol.jpeg", "Betis": f"{LOGOS_DIR}betis.jpeg",
    "Levante": f"{LOGOS_DIR}levante.jpeg", "Oviedo": f"{LOGOS_DIR}oviedo.jpeg"
}

SCORING = {"Normal": (0.5, 0.75, 1.0), "Doble": (1.0, 1.5, 2.0), "Esquizo": (1.0, 1.5, 3.0)}

# --- DEFINICIÓN DE TODOS LOS LOGROS ---
LOGROS_DATA = {
    "guru": {"icon": "🔮", "name": "El Gurú", "desc": "Acierto exacto en un partido tipo Esquizo."},
    "hattrick": {"icon": "🎯", "name": "Hat-Trick de Plenos", "desc": "3 o más resultados exactos en una sola jornada."},
    "cazagigantes": {"icon": "⚔️", "name": "Cazagigantes", "desc": "Acierto exacto de un Nivel 4 ganando a un Nivel 1."},
    "halcon": {"icon": "🦅", "name": "Ojo de Halcón", "desc": "Único usuario en acertar el ganador de un partido."},
    "pleno": {"icon": "💯", "name": "Pleno de Jornada", "desc": "Puntuar en los 10 partidos de la jornada."},
    "cima": {"icon": "🏔️", "name": "En la Cima", "desc": "Líder actual de la clasificación general."},
    "amarrategui": {"icon": "🧱", "name": "Amarrategui de Oro", "desc": "5+ aciertos usando resultados 1-0, 0-1 o 0-0."},
    "empate": {"icon": "🤝", "name": "Rey del Empate", "desc": "Acierto exacto en un empate que no sea 0-0."},
    "kamikaze": {"icon": "🎰", "name": "Kamikaze Responsable", "desc": "Acertar ganador con diferencia de 2 niveles contra pronóstico."},
    "gafe": {"icon": "🕯️", "name": "Gafe Oficial", "desc": "0 puntos en una jornada completa habiendo apostado todo."},
    "casi": {"icon": "🤏", "name": "Casi, pero No", "desc": "5+ veces fallando el pleno por solo un gol."},
    "estrellado": {"icon": "🤡", "name": "Visionario Estrellado", "desc": "Apostar por el humilde y recibir una goleada (+3)."}
}

# --- 2. FUNCIONES DE APOYO ---

def safe_float(valor):
    try:
        if pd.isna(valor) or str(valor).strip() == "": return 0.0
        return float(str(valor).replace(',', '.'))
    except: return 0.0

def get_logo(equipo):
    path = LOGOS.get(equipo)
    return path if path and os.path.exists(path) else None

def calcular_puntos(p_l, p_v, r_l, r_v, tipo="Normal"):
    p_ganador, p_diff, p_exacto = SCORING.get(tipo, SCORING["Normal"])
    if p_l == r_l and p_v == r_v: return p_exacto
    signo_p = (p_l > p_v) - (p_l < p_v)
    signo_r = (r_l > r_v) - (r_l < r_v)
    if signo_p == signo_r: return p_diff if (p_l - p_v) == (r_l - r_v) else p_ganador
    return 0.0

def calcular_logros_completo(usuario, df_p_all, df_r_all, jornada_sel, ranking_actual):
    logros = []
    if df_p_all.empty or df_r_all.empty: return logros
    
    u_p = df_p_all[(df_p_all['Usuario'] == usuario) & (df_p_all['Jornada'] == jornada_sel)]
    res_j = df_r_all[(df_r_all['Jornada'] == jornada_sel) & (df_r_all['Finalizado'] == "SI")]
    
    if u_p.empty or res_j.empty: return logros

    # Lógica de posición
    if not ranking_actual.empty and ranking_actual.iloc[0]['Usuario'] == usuario: logros.append("cima")

    pts_jornada = []
    exactos = 0
    amarrategui = 0
    casi_no = 0

    for row in u_p.itertuples():
        m = res_j[res_j['Partido'] == row.Partido]
        if not m.empty:
            inf = m.iloc[0]
            pts = calcular_puntos(row.P_L, row.P_V, inf['R_L'], inf['R_V'], inf['Tipo'])
            pts_jornada.append(pts)
            
            eq_l, eq_v = row.Partido.split('-')
            lv_l, lv_v = NIVEL_EQUIPOS.get(eq_l, 3), NIVEL_EQUIPOS.get(eq_v, 3)

            # Guru & Cazagigantes
            if pts == SCORING.get(inf['Tipo'], SCORING["Normal"])[2]:
                exactos += 1
                if inf['Tipo'] == "Esquizo": logros.append("guru")
                if (lv_l == 4 and lv_v == 1 and inf['R_L'] > inf['R_V']) or (lv_v == 4 and lv_l == 1 and inf['R_V'] > inf['R_L']):
                    logros.append("cazagigantes")
                if inf['R_L'] == inf['R_V'] and inf['R_L'] > 0: logros.append("empate")

            # Amarrategui
            if pts > 0 and sorted([row.P_L, row.P_V]) in [[0,0], [0,1]]: amarrategui += 1

            # Casi pero no (Mismo signo, diferencia de 1 gol total)
            signo_p = (row.P_L > row.P_V) - (row.P_L < row.P_V)
            signo_r = (inf['R_L'] > inf['R_V']) - (inf['R_L'] < inf['R_V'])
            if signo_p == signo_r and pts < SCORING.get(inf['Tipo'], SCORING["Normal"])[2]:
                if abs(row.P_L - inf['R_L']) + abs(row.P_V - inf['R_V']) == 1: casi_no += 1

            # Visionario Estrellado
            if (row.P_L > row.P_V and lv_l == 4 and lv_v == 1) or (row.P_V > row.P_L and lv_v == 4 and lv_l == 1):
                if (inf['R_V'] - inf['R_L'] >= 3 and lv_v == 1) or (inf['R_L'] - inf['R_V'] >= 3 and lv_l == 1):
                    logros.append("estrellado")

    # Condicionales de fin de jornada (10 partidos)
    if len(pts_jornada) == 10:
        if all(p > 0 for p in pts_jornada): logros.append("pleno")
        if sum(pts_jornada) == 0: logros.append("gafe")
        if exactos >= 3: logros.append("hattrick")
        if amarrategui >= 5: logros.append("amarrategui")
        if casi_no >= 5: logros.append("casi")

    return list(set(logros))

# --- 3. INICIO APP ---
st.set_page_config(page_title="Porra League 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos(pestaña):
    try:
        sheet_id = "1vFgccrCqmGrs9QfP8kxY_cESbRaJ_VxpsoAz-ZyL14E"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={pestaña}"
        return pd.read_csv(url)
    except: return pd.DataFrame()

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    # Bloque de Login... (Se mantiene igual que el anterior)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>🏆 Porra League</h1>", unsafe_allow_html=True)
        modo = st.radio("Selecciona", ["Iniciar Sesión", "Registrarse"], horizontal=True)
        u_in, p_in = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            df_u = leer_datos("Usuarios")
            user_db = df_u[(df_u['Usuario'].astype(str) == str(u_in)) & (df_u['Password'].astype(str) == str(p_in))]
            if not user_db.empty:
                st.session_state.autenticado, st.session_state.user, st.session_state.rol = True, u_in, user_db.iloc[0]['Rol']
                st.rerun()
            else: st.error("❌ Error")
else:
    df_perfiles = leer_datos("ImagenesPerfil")
    df_r_all = leer_datos("Resultados")
    df_p_all = leer_datos("Predicciones")
    df_u_all = leer_datos("Usuarios")
    df_base = leer_datos("PuntosBase")
    
    foto_dict = df_perfiles.set_index('Usuario')['ImagenPath'].to_dict() if not df_perfiles.empty else {}
    admins = df_u_all[df_u_all['Rol'] == 'admin']['Usuario'].tolist() if not df_u_all.empty else []

    # Header
    c_h1, c_h2, c_h3 = st.columns([1, 5, 1])
    with c_h1:
        mi_f = foto_dict.get(st.session_state.user)
        if mi_f and pd.notna(mi_f) and os.path.exists(str(mi_f)): st.image(str(mi_f), width=75)
        else: st.subheader("👤")
    with c_h2: st.title(f"Hola, {st.session_state.user} 👋")
    with c_h3: 
        if st.button("Salir"): st.session_state.autenticado = False; st.rerun()

    j_global = st.selectbox("📅 Jornada:", list(JORNADAS.keys()), key="global_j")
    st.divider()

    tabs = st.tabs(["✍️ Apuestas", "👀 Otros", "📊 Clasificación", "🏆 Detalles", "🔮 Simulador", "⚙️ Admin"])

    with tabs[2]: # Clasificación con LOGROS
        st.header("📊 Ranking y Medallero")
        if not df_u_all.empty:
            j_fin = sorted(df_r_all[df_r_all['Finalizado'] == "SI"]['Jornada'].unique()) if not df_r_all.empty else []
            u_jug = [u for u in df_u_all['Usuario'].unique() if u not in admins]
            
            # Cálculo de Ranking para determinar quién está en la Cima
            hist = []
            for u in u_jug:
                pts = safe_float(df_base[df_base['Usuario'] == u].iloc[0]['Puntos']) if not df_base.empty and u in df_base['Usuario'].values else 0.0
                if not df_r_all.empty:
                    for r in df_p_all[df_p_all['Usuario'] == u].itertuples():
                        m_k = df_r_all[(df_r_all['Jornada'] == r.Jornada) & (df_r_all['Partido'] == r.Partido) & (df_r_all['Finalizado'] == "SI")]
                        if not m_k.empty: pts += calcular_puntos(r.P_L, r.P_V, m_k.iloc[0]['R_L'], m_k.iloc[0]['R_V'], m_k.iloc[0]['Tipo'])
                hist.append({"Usuario": u, "Puntos": pts})
            
            df_act = pd.DataFrame(hist).sort_values("Puntos", ascending=False)
            df_act['Posicion'] = range(1, len(df_act) + 1)

            logros_ganados_total = {}
            for _, row in df_act.iterrows():
                # Calculamos logros
                l_u = calcular_logros_completo(row['Usuario'], df_p_all, df_r_all, j_global, df_act)
                logros_ganados_total[row['Usuario']] = l_u
                icons = "".join([LOGROS_DATA[lid]['icon'] for lid in l_u])

                c1, c2, c3, c4 = st.columns([0.5, 1.2, 4, 1.5])
                with c1: st.markdown(f"### #{row['Posicion']}")
                with c2:
                    fp = foto_dict.get(row['Usuario'])
                    if fp and pd.notna(fp) and os.path.exists(str(fp)): st.image(str(fp), width=85)
                    else: st.subheader("👤")
                with c3:
                    st.markdown(f"**{row['Usuario']}** {icons}")
                    st.caption(f"Puntos totales: {row['Puntos']:.2f}")
                with c4:
                    if l_u: st.write("🏅 Logros activos")
                st.divider()

            # Desplegable de explicación de logros conseguidos
            vistos = set([item for sublist in logros_ganados_total.values() for item in sublist])
            if vistos:
                with st.expander("🎖️ Guía de Trofeos de esta Jornada"):
                    for lid in vistos:
                        st.write(f"{LOGROS_DATA[lid]['icon']} **{LOGROS_DATA[lid]['name']}**: {LOGROS_DATA[lid]['desc']}")

    with tabs[4]: # Simulador
        st.header("🔮 Simulador de LaLiga")
        u_sim = [u for u in df_u_all['Usuario'].unique() if u not in admins]
        if u_sim:
            usr_s = st.selectbox("Simular según:", u_sim)
            if st.button("🚀 Simular"):
                sim_d = {k: v.copy() for k, v in STATS_LALIGA_BASE.items()} #
                for p in df_p_all[df_p_all['Usuario'] == usr_s].itertuples():
                    try:
                        tl, tv = p.Partido.split('-')
                        if tl in sim_d and tv in sim_d:
                            sim_d[tl]["PJ"] += 1; sim_d[tv]["PJ"] += 1
                            sim_d[tl]["GF"] += p.P_L; sim_d[tl]["GC"] += p.P_V
                            sim_d[tv]["GF"] += p.P_V; sim_d[tv]["GC"] += p.P_L
                            if p.P_L > p.P_V: sim_d[tl]["V"] += 1; sim_d[tl]["Pts"] += 3; sim_d[tv]["D"] += 1
                            elif p.P_V > p.P_L: sim_d[tv]["V"] += 1; sim_d[tv]["Pts"] += 3; sim_d[tl]["D"] += 1
                            else: sim_d[tl]["E"] += 1; sim_d[tl]["Pts"] += 1; sim_d[tv]["E"] += 1; sim_d[tv]["Pts"] += 1
                    except: continue
                df_sim = pd.DataFrame.from_dict(sim_d, orient='index').reset_index()
                df_sim.columns = ['Equipo', 'PJ', 'V', 'E', 'D', 'GF', 'GC', 'Pts']
                df_sim['DG'] = df_sim['GF'] - df_sim['GC']
                df_sim = df_sim.sort_values(by=['Pts', 'DG', 'GF'], ascending=False).reset_index(drop=True)
                df_sim['Pos'] = range(1, 21)
                st.dataframe(df_sim[['Pos', 'Equipo', 'PJ', 'V', 'E', 'D', 'GF', 'GC', 'DG', 'Pts']], hide_index=True, use_container_width=True) #

    # ... (Resto de pestañas: Apuestas, Otros, Detalles, Admin se mantienen como en la versión funcional anterior)
