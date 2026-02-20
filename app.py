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

# Datos base oficiales J24
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

LOGROS_DATA = {
    "guru": {"icon": "🔮", "name": "El Gurú", "desc": "Acierto exacto en un partido tipo Esquizo."},
    "hattrick": {"icon": "🎯", "name": "Hat-Trick", "desc": "3 o más resultados exactos en una sola jornada."},
    "cazagigantes": {"icon": "⚔️", "name": "Cazagigantes", "desc": "Acierto exacto de un Nivel 4 ganando a un Nivel 1."},
    "halcon": {"icon": "🦅", "name": "Ojo de Halcón", "desc": "Único usuario en acertar el ganador de un partido."},
    "pleno": {"icon": "💯", "name": "Pleno", "desc": "Puntuar en los 10 partidos de la jornada."},
    "cima": {"icon": "🏔️", "name": "En la Cima", "desc": "Líder de la clasificación general."},
    "amarrategui": {"icon": "🧱", "name": "Amarrategui de Oro", "desc": "5+ aciertos con resultados 1-0, 0-1 o 0-0."},
    "empate": {"icon": "🤝", "name": "Rey del Empate", "desc": "Acierto exacto en un empate que no sea 0-0."},
    "kamikaze": {"icon": "🎰", "name": "Kamikaze Responsable", "desc": "Acertar ganador con diferencia de 2 niveles contra pronóstico."},
    "gafe": {"icon": "🕯️", "name": "Gafe Oficial", "desc": "0 puntos en una jornada completa habiéndolo apostado todo."},
    "casi": {"icon": "🤏", "name": "Casi, pero No", "desc": "5+ veces fallando el pleno por solo un gol."},
    "estrellado": {"icon": "🤡", "name": "Estrellado", "desc": "Apostar por el humilde y recibir una goleada (+3)."}
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

def aplicar_color_estilo(valor, tipo_partido):
    if valor == 0: return 'background-color: #ff4b4b; color: black'
    if tipo_partido == "Normal":
        if valor == 0.5: return 'background-color: #ffd700; color: black'
        if valor == 0.75: return 'background-color: #ffa500; color: black'
        return 'background-color: #2baf2b; color: black'
    if tipo_partido in ["Doble", "Esquizo"]:
        color = '#a020f0' if tipo_partido == "Doble" else '#00f2ff'
        if valor in [1.0, 1.5]: return f'background-color: {color}; color: black'
        return 'background-color: #2baf2b; color: black'
    return ''

def obtener_perfil_apostador(df_u):
    if df_u is None or df_u.empty: return "Novato 🐣", "Sin datos aún.", 0.0
    avg_g = (df_u['P_L'] + df_u['P_V']).mean()
    riesgo = min(avg_g / 5.0, 1.0)
    if avg_g > 3.4: return "BUSCADOR DE PLENOS 🤪", "Busca el ataque total.", riesgo
    if avg_g < 2.1: return "CONSERVADOR / AMARRETE 🛡️", "Fiel al 1-0 y 0-0.", riesgo
    return "ESTRATEGA ⚖️", "Apuestas equilibradas con lógica.", riesgo

def calcular_logros_completo(usuario, df_p_all, df_r_all, jornada_sel, ranking_actual):
    logros = []
    if df_p_all.empty or df_r_all.empty: return logros
    u_p = df_p_all[(df_p_all['Usuario'] == usuario) & (df_p_all['Jornada'] == jornada_sel)]
    res_j = df_r_all[(df_r_all['Jornada'] == jornada_sel) & (df_r_all['Finalizado'] == "SI")]
    if not ranking_actual.empty and ranking_actual.iloc[0]['Usuario'] == usuario: logros.append("cima")
    if u_p.empty or res_j.empty: return logros
    
    pts_j, exactos, amarra, casi = [], 0, 0, 0
    for row in u_p.itertuples():
        m = res_j[res_j['Partido'] == row.Partido]
        if not m.empty:
            inf = m.iloc[0]
            pts = calcular_puntos(row.P_L, row.P_V, inf['R_L'], inf['R_V'], inf['Tipo'])
            pts_j.append(pts)
            eq_l, eq_v = row.Partido.split('-')
            lv_l, lv_v = NIVEL_EQUIPOS.get(eq_l, 3), NIVEL_EQUIPOS.get(eq_v, 3)
            if pts == SCORING.get(inf['Tipo'], SCORING["Normal"])[2]:
                exactos += 1
                if inf['Tipo'] == "Esquizo": logros.append("guru")
                if (lv_l==4 and lv_v==1 and inf['R_L']>inf['R_V']) or (lv_v==4 and lv_l==1 and inf['R_V']>inf['R_L']): logros.append("cazagigantes")
                if inf['R_L'] == inf['R_V'] and inf['R_L'] > 0: logros.append("empate")
            if pts > 0 and sorted([row.P_L, row.P_V]) in [[0,0], [0,1]]: amarra += 1
            if (row.P_L > row.P_V) == (inf['R_L'] > inf['R_V']) and pts < SCORING.get(inf['Tipo'])[2]:
                if abs(row.P_L - inf['R_L']) + abs(row.P_V - inf['R_V']) == 1: casi += 1
            if (row.P_L > row.P_V and lv_l==4 and lv_v==1) or (row.P_V > row.P_L and lv_v==4 and lv_l==1):
                if (inf['R_V']-inf['R_L']>=3 and lv_v==1) or (inf['R_L']-inf['R_V']>=3 and lv_l==1): logros.append("estrellado")

    if len(pts_j) == 10:
        if all(p > 0 for p in pts_j): logros.append("pleno")
        if sum(pts_j) == 0: logros.append("gafe")
        if exactos >= 3: logros.append("hattrick")
        if amarra >= 5: logros.append("amarrategui")
        if casi >= 5: logros.append("casi")
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
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>🏆 Porra League</h1>", unsafe_allow_html=True)
        modo = st.radio("Selecciona", ["Iniciar Sesión", "Registrarse"], horizontal=True)
        u_in, p_in = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            df_u = leer_datos("Usuarios")
            if not df_u.empty:
                user_db = df_u[(df_u['Usuario'].astype(str) == str(u_in)) & (df_u['Password'].astype(str) == str(p_in))]
                if not user_db.empty:
                    st.session_state.autenticado, st.session_state.user, st.session_state.rol = True, u_in, user_db.iloc[0]['Rol']
                    st.rerun()
                else: st.error("❌ Datos incorrectos")
        else:
            if st.button("Crear Cuenta"):
                df_u = leer_datos("Usuarios")
                nueva = pd.DataFrame([{"Usuario": u_in, "Password": p_in, "Rol": "user"}])
                conn.update(worksheet="Usuarios", data=pd.concat([df_u, nueva], ignore_index=True))
                st.success("✅ Registrado")
else:
    df_perfiles = leer_datos("ImagenesPerfil")
    df_r_all, df_p_all, df_u_all, df_base = leer_datos("Resultados"), leer_datos("Predicciones"), leer_datos("Usuarios"), leer_datos("PuntosBase")
    foto_dict = df_perfiles.set_index('Usuario')['ImagenPath'].to_dict() if not df_perfiles.empty else {}
    admins = df_u_all[df_u_all['Rol'] == 'admin']['Usuario'].tolist() if not df_u_all.empty else []

    c_h1, c_h2, c_h3 = st.columns([1, 5, 1])
    with c_h1:
        mi_foto = foto_dict.get(st.session_state.user)
        if mi_foto and pd.notna(mi_foto) and os.path.exists(str(mi_foto)):
            st.image(str(mi_foto), width=75)
        else:
            st.subheader("👤")
    with c_h2: st.title(f"Hola, {st.session_state.user} 👋")
    with c_h3: 
        if st.button("Salir"): st.session_state.autenticado = False; st.rerun()

    j_global = st.selectbox("📅 Jornada Seleccionada:", list(JORNADAS.keys()), key="global_j")
    st.divider()

    tabs = st.tabs(["✍️ Apuestas", "👀 Otros", "📊 Clasificación", "🏆 Detalles", "🔮 Simulador", "⚙️ Admin"])

    with tabs[2]: # CLASIFICACIÓN CON LOGROS Y PERFILES
        st.header("📊 Ranking General")
        if not df_u_all.empty:
            u_jug = [u for u in df_u_all['Usuario'].unique() if u not in admins]
            pts_hist = []
            for u in u_jug:
                pts = safe_float(df_base[df_base['Usuario'] == u].iloc[0]['Puntos']) if not df_base.empty and u in df_base['Usuario'].values else 0.0
                if not df_r_all.empty:
                    u_preds = df_p_all[df_p_all['Usuario'] == u]
                    for r in u_preds.itertuples():
                        m_k = df_r_all[(df_r_all['Jornada']==r.Jornada)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
                        if not m_k.empty: pts += calcular_puntos(r.P_L, r.P_V, m_k.iloc[0]['R_L'], m_k.iloc[0]['R_V'], m_k.iloc[0]['Tipo'])
                pts_hist.append({"Usuario": u, "Puntos": pts})
            
            df_rank = pd.DataFrame(pts_hist).sort_values("Puntos", ascending=False)
            df_rank['Posicion'] = range(1, len(df_rank) + 1)

            logros_temp = {}
            for _, row in df_rank.iterrows():
                l_u = calcular_logros_completo(row['Usuario'], df_p_all, df_r_all, j_global, df_rank)
                logros_temp[row['Usuario']] = l_u
                icons = "".join([LOGROS_DATA[lid]['icon'] for lid in l_u])
                u_apuestas = df_p_all[df_p_all['Usuario'] == row['Usuario']]
                n_perfil, d_perfil, riesgo_val = obtener_perfil_apostador(u_apuestas)

                c1, c2, c3, c4 = st.columns([0.5, 1.2, 4, 1.5])
                with c1: st.markdown(f"### #{row['Posicion']}")
                with c2:
                    fp = foto_dict.get(row['Usuario'])
                    if fp and pd.notna(fp) and os.path.exists(str(fp)): st.image(str(fp), width=85)
                    else: st.subheader("👤")
                with c3:
                    st.markdown(f"**{row['Usuario']}** {icons}")
                    st.progress(riesgo_val)
                    st.caption(f"{n_perfil} | {d_perfil}")
                with c4: st.markdown(f"#### {row['Puntos']:.2f} pts")
                st.divider()

            vistos = set([item for sublist in logros_temp.values() for item in sublist])
            if vistos:
                with st.expander("🎖️ Significado de los Logros Activos"):
                    for lid in vistos: st.write(f"{LOGROS_DATA[lid]['icon']} **{LOGROS_DATA[lid]['name']}**: {LOGROS_DATA[lid]['desc']}")

    with tabs[4]: # SIMULADOR PRO
        st.header("🔮 Simulador de LaLiga")
        u_sim = [u for u in df_u_all['Usuario'].unique() if u not in admins]
        if u_sim:
            usr_s = st.selectbox("Simular según predicciones de:", u_sim)
            if st.button("🚀 Ejecutar Simulación"):
                sim_d = {k: v.copy() for k, v in STATS_LALIGA_BASE.items()}
                for p in (df_p_all[df_p_all['Usuario'] == usr_s].itertuples() if not df_p_all.empty else []):
                    try:
                        tl, tv = p.Partido.split('-')
                        if tl in sim_d and tv in sim_d:
                            sim_d[tl]["PJ"]+=1; sim_d[tv]["PJ"]+=1
                            sim_d[tl]["GF"]+=p.P_L; sim_d[tl]["GC"]+=p.P_V
                            sim_d[tv]["GF"]+=p.P_V; sim_d[tv]["GC"]+=p.P_L
                            if p.P_L > p.P_V: sim_d[tl]["V"]+=1; sim_d[tl]["Pts"]+=3; sim_d[tv]["D"]+=1
                            elif p.P_V > p.P_L: sim_d[tv]["V"]+=1; sim_d[tv]["Pts"]+=3; sim_d[tl]["D"]+=1
                            else: sim_d[tl]["E"]+=1; sim_d[tl]["Pts"]+=1; sim_d[tv]["E"]+=1; sim_d[tv]["Pts"]+=1
                    except: continue
                df_sim = pd.DataFrame.from_dict(sim_d, orient='index').reset_index()
                df_sim.columns = ['Equipo','PJ','V','E','D','GF','GC','Pts']
                df_sim['DG'] = df_sim['GF'] - df_sim['GC']
                df_sim = df_sim.sort_values(by=['Pts','DG','GF'], ascending=False).reset_index(drop=True)
                df_sim['Pos'] = range(1, 21)
                st.dataframe(df_sim[['Pos','Equipo','PJ','V','E','D','GF','GC','DG','Pts']], hide_index=True, use_container_width=True)

    with tabs[0]: # APUESTAS
        if st.session_state.rol != "admin":
            mis_p = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)]
            df_rj = df_r_all[df_r_all['Jornada'] == j_global]
            preds_env = []
            for i, (loc, vis) in enumerate(JORNADAS[j_global]):
                m_id, bloq, t = f"{loc}-{vis}", False, "Normal"
                dl, dv, dp = 0, 0, False
                if not mis_p.empty:
                    prev = mis_p[mis_p['Partido'] == m_id]
                    if not prev.empty: dl, dv, dp = int(prev.iloc[0]['P_L']), int(prev.iloc[0]['P_V']), str(prev.iloc[0]['Publica']) == "SI"
                if not df_rj.empty and m_id in df_rj['Partido'].values:
                    inf = df_rj[df_rj['Partido'] == m_id].iloc[0]
                    t = inf['Tipo']
                    if datetime.now() > datetime.strptime(str(inf['Hora_Inicio']), "%Y-%m-%d %H:%M:%S"): bloq = True
                st.markdown(f"#### {t} {'🔒' if bloq else '🔓'}")
                c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 0.5, 2, 1, 2])
                with c1: 
                    l_logo = get_logo(loc)
                    if l_logo: st.image(l_logo, width=65)
                    else: st.markdown("⚽")
                with c2: pl = st.number_input(f"{loc}", 0, value=dl, key=f"l_{j_global}_{i}", disabled=bloq)
                with c3: st.markdown("<br>VS", unsafe_allow_html=True)
                with c4: pv = st.number_input(f"{vis}", 0, value=dv, key=f"v_{j_global}_{i}", disabled=bloq)
                with c5: 
                    v_logo = get_logo(vis)
                    if v_logo: st.image(v_logo, width=65)
                    else: st.markdown("⚽")
                with c6: pub = st.checkbox("Público", value=dp, key=f"pb_{j_global}_{i}", disabled=bloq)
                preds_env.append({"Usuario": st.session_state.user, "Jornada": j_global, "Partido": m_id, "P_L": pl, "P_V": pv, "Publica": "SI" if pub else "NO"})
            if st.button("💾 Guardar"):
                old = df_p_all[~((df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global))]
                conn.update(worksheet="Predicciones", data=pd.concat([old, pd.DataFrame(preds_env)], ignore_index=True)); st.rerun()

    with tabs[1]: # OTROS
        st.header("🔍 Predicciones Públicas")
        if not df_p_all.empty:
            p_pub = df_p_all[(df_p_all['Jornada'] == j_global) & (df_p_all['Publica'] == "SI")]
            for u in p_pub['Usuario'].unique():
                with st.expander(f"Apuestas de {u}"): st.table(p_pub[p_pub['Usuario'] == u][['Partido', 'P_L', 'P_V']])

    with tabs[3]: # DETALLES
        st.header(f"🏆 Detalles J: {j_global}")
        df_rf = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "SI")]
        if not df_rf.empty:
            jugs = [u for u in df_u_all['Usuario'].unique() if u not in admins]
            c_m = st.columns([2] + [1]*len(jugs))
            c_m[0].write("**Partido**")
            for i, u in enumerate(jugs):
                fp = foto_dict.get(u)
                if fp and pd.notna(fp) and os.path.exists(str(fp)): c_m[i+1].image(str(fp), width=45)
                else: c_m[i+1].write(u[:3])
            m_pts, m_sty = pd.DataFrame(index=df_rf['Partido'].unique(), columns=jugs), pd.DataFrame(index=df_rf['Partido'].unique(), columns=jugs)
            for p in m_pts.index:
                inf = df_rf[df_rf['Partido'] == p].iloc[0]
                for u in jugs:
                    up = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == j_global) & (df_p_all['Partido'] == p)]
                    pts = calcular_puntos(up.iloc[0]['P_L'], up.iloc[0]['P_V'], inf['R_L'], inf['R_V'], inf['Tipo']) if not up.empty else 0.0
                    m_pts.at[p, u], m_sty.at[p, u] = pts, aplicar_color_estilo(pts, inf['Tipo'])
            st.dataframe(m_pts.style.apply(lambda x: m_sty, axis=None).format("{:.2f}"))

    with tabs[5]: # ADMIN
        if st.session_state.rol == "admin":
            a_tabs = st.tabs(["⭐ Bases", "📸 Fotos", "⚽ Resultados"])
            with a_tabs[0]:
                upd_b = []
                for u in [usr for usr in df_u_all['Usuario'].unique() if usr not in admins]:
                    pts_ex = safe_float(df_base[df_base['Usuario'] == u].iloc[0]['Puntos']) if not df_base.empty and u in df_base['Usuario'].values else 0.0
                    val = st.number_input(f"Base {u}", value=pts_ex, key=f"ba_{u}")
                    upd_b.append({"Usuario": u, "Puntos": val})
                if st.button("Guardar Bases"): conn.update(worksheet="PuntosBase", data=pd.DataFrame(upd_b)); st.rerun()
            with a_tabs[1]:
                if os.path.exists(PERFILES_DIR):
                    fotos = sorted(os.listdir(PERFILES_DIR))
                    upd_f = []
                    for u in [usr for usr in df_u_all['Usuario'].unique() if usr not in admins]:
                        idx = 0
                        db_p = foto_dict.get(u)
                        if pd.notna(db_p):
                            f_file = str(db_p).replace(PERFILES_DIR, "")
                            if f_file in fotos: idx = fotos.index(f_file) + 1
                        fs = st.selectbox(f"Foto {u}", ["Ninguna"] + fotos, index=idx, key=f"im_{u}")
                        upd_f.append({"Usuario": u, "ImagenPath": f"{PERFILES_DIR}{fs}" if fs != "Ninguna" else ""})
                    if st.button("Asociar Fotos"): conn.update(worksheet="ImagenesPerfil", data=pd.DataFrame(upd_f)); st.rerun()
            with a_tabs[2]:
                r_env, h_p = [], [time(h, m) for h in range(12, 23) for m in [0, 15, 30, 45]]
                for i, (l, v) in enumerate(JORNADAS[j_global]):
                    m_id = f"{l}-{v}"
                    ex = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Partido'] == m_id)] if not df_r_all.empty else pd.DataFrame()
                    dt, t, rl, rv, f = datetime.now(), "Normal", 0, 0, False
                    if not ex.empty:
                        t, rl, rv, f = ex.iloc[0]['Tipo'], int(ex.iloc[0]['R_L']), int(ex.iloc[0]['R_V']), ex.iloc[0]['Finalizado'] == "SI"
                        try: dt = datetime.strptime(str(ex.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                        except: pass
                    c1, c2, c3, c4, c5, c6 = st.columns([2, 1, 1, 1, 1, 1])
                    tip_a = c1.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], index=["Normal", "Doble", "Esquizo"].index(t), key=f"at_{j_global}_{i}")
                    fec_a = c2.date_input("D", value=dt.date(), key=f"af_{j_global}_{i}")
                    hor_a = c3.selectbox("H", h_p, index=h_p.index(dt.time()) if dt.time() in h_p else 36, key=f"ah_{j_global}_{i}")
                    rla, rva = c4.number_input("L", 0, value=rl, key=f"rl_{j_global}_{i}"), c5.number_input("V", 0, value=rv, key=f"rv_{j_global}_{i}")
                    fina = c6.checkbox("Fin", value=f, key=f"fi_{j_global}_{i}")
                    r_env.append({"Jornada": j_global, "Partido": m_id, "Tipo": tip_a, "R_L": rla, "R_V": rva, "Hora_Inicio": datetime.combine(fec_a, hor_a).strftime("%Y-%m-%d %H:%M:%S"), "Finalizado": "SI" if fina else "NO"})
                if st.button("Actualizar"):
                    old = df_r_all[df_r_all['Jornada'] != j_global]
                    conn.update(worksheet="Resultados", data=pd.concat([old, pd.DataFrame(r_env)], ignore_index=True)); st.rerun()
