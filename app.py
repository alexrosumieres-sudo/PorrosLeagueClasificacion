import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time
import os
import plotly.express as px
import random

# --- 1. CONFIGURACIONES GENERALES ---
PERFILES_DIR = "perfiles/"
LOGOS_DIR = "logos/"

NIVEL_EQUIPOS = {
    "Real Madrid": 1, "Barcelona": 1, "Villarreal": 1, "Atlético": 1,
    "Betis": 2, "Espanyol": 2, "Celta": 2, "R. Sociedad": 2, "Athletic": 2,
    "Osasuna": 3, "Getafe": 3, "Girona": 3, "Sevilla": 3, "Alavés": 3, "Valencia": 3, "Elche": 3, "Rayo": 3,
    "Mallorca": 4, "Levante": 4, "Oviedo": 4
}

# Datos oficiales tras la Jornada 24
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

FRASES_PUESTOS = {
    "oro": [
        ("¿Por qué? Porque soy rico, guapo y un gran jugador. Me tienen envidia.", "Cristiano Ronaldo"),
        ("I am the Special One.", "José Mourinho"),
        ("Vuestra envidia me hace fuerte, vuestro odio me hace imparable.", "Cristiano Ronaldo"),
        ("No soy el mejor del mundo, soy el mejor de la historia.", "Cristiano Ronaldo"),
        ("A mí me gusta sentirme presionado, si no, no hay gracia.", "Zlatan Ibrahimovic")
    ],
    "plata": [
        ("Ganar, ganar, ganar y volver a ganar.", "Luis Aragonés"),
        ("Fútbol es fútbol.", "Vujadin Boškov"),
        ("Partido a partido.", "Cholo Simeone"),
        ("Ni antes éramos tan buenos, ni ahora tan malos.", "Cliché deportivo"),
        ("Las estadísticas están para romperse.", "Leyenda del fútbol")
    ],
    "bronce": [
        ("¿Por qué? ¿Por qué? ¿Por qué?", "José Mourinho"),
        ("No me pises, que llevo chanclas.", "Luis Aragonés"),
        ("¡A qué estamos jugando! ¡A las canicas no!", "Luis Aragonés"),
        ("Me cortaron las piernas.", "Diego Maradona"),
        ("¡Digo lo que pienso y no me callo nada!", "Jesús Gil")
    ],
    "barro": [
        ("Se queda... (pero en el pozo de la tabla).", "Gerard Piqué"),
        ("Estamos en la UVI, pero todavía estamos vivos.", "Javier Clemente"),
        ("¿Alguien tiene el teléfono del VAR?", "Apostador desesperado"),
        ("A veces se gana, otras veces se aprende. Tú hoy eres catedrático.", "Anónimo"),
        ("He fallado más de 9.000 tiros en mi carrera... y tú hoy todos.", "Michael Jordan")
    ]
}

LOGROS_DATA = {
    "guru": {"icon": "🔮", "name": "El Gurú", "desc": "Pleno en partido Esquizo."},
    "hattrick": {"icon": "🎯", "name": "Hat-Trick", "desc": "3+ resultados exactos en la jornada."},
    "cima": {"icon": "🏔️", "name": "En la Cima", "desc": "Líder de la clasificación general."},
    "amarrategui": {"icon": "🧱", "name": "Amarrategui", "desc": "5+ aciertos con 1-0, 0-1 o 0-0."},
    "pleno": {"icon": "💯", "name": "Pleno", "desc": "Puntuado en los 10 partidos de la jornada."}
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

def obtener_perfil_apostador(df_u):
    if df_u is None or df_u.empty: return "Novato 🐣", "Sin datos.", 0.0
    avg_g = (df_u['P_L'] + df_u['P_V']).mean()
    riesgo = min(avg_g / 5.0, 1.0)
    if avg_g > 3.4: return "BUSCADOR DE PLENOS 🤪", "Ataque total.", riesgo
    if avg_g < 2.1: return "CONSERVADOR / AMARRETE 🛡️", "Fiel al 1-0.", riesgo
    return "ESTRATEGA ⚖️", "Apuestas equilibradas.", riesgo

def calcular_logros_u(usuario, df_p_all, df_r_all, jornada_sel, ranking):
    logros = []
    if not ranking.empty and ranking.iloc[0]['Usuario'] == usuario: logros.append("cima")
    u_p = df_p_all[(df_p_all['Usuario'] == usuario) & (df_p_all['Jornada'] == jornada_sel)]
    res_j = df_r_all[(df_r_all['Jornada'] == jornada_sel) & (df_r_all['Finalizado'] == "SI")]
    if u_p.empty or res_j.empty: return logros
    pts_j, exactos, amarra = [], 0, 0
    for row in u_p.itertuples():
        m = res_j[res_j['Partido'] == row.Partido]
        if not m.empty:
            inf = m.iloc[0]
            pts = calcular_puntos(row.P_L, row.P_V, inf['R_L'], inf['R_V'], inf['Tipo'])
            pts_j.append(pts)
            if pts == SCORING.get(inf['Tipo'])[2]:
                exactos += 1
                if inf['Tipo'] == "Esquizo": logros.append("guru")
            if pts > 0 and sorted([row.P_L, row.P_V]) in [[0,0], [0,1]]: amarra += 1
    if len(pts_j) == 10:
        if all(p > 0 for p in pts_j): logros.append("pleno")
        if exactos >= 3: logros.append("hattrick")
        if amarra >= 5: logros.append("amarrategui")
    return list(set(logros))

def analizar_adn_pro(usuario, df_p, df_r):
    df_m = pd.merge(df_p[df_p['Usuario'] == usuario], df_r[df_r['Finalizado'] == "SI"], on=['Jornada', 'Partido'])
    if df_m.empty: return None
    df_m['Pts'] = df_m.apply(lambda x: calcular_puntos(x.P_L, x.P_V, x.R_L, x.R_V, x.Tipo), axis=1)
    pts_eq = {}
    for _, r in df_m.iterrows():
        l, v = r['Partido'].split('-')
        pts_eq[l] = pts_eq.get(l, 0) + r['Pts']
        pts_eq[v] = pts_eq.get(v, 0) + r['Pts']
    exactos = len(df_m[df_m.apply(lambda x: x.P_L == x.R_L and x.P_V == x.R_V, axis=1)])
    signos = len(df_m[df_m['Pts'] > 0]) - exactos
    return {
        "amuleto": max(pts_eq, key=pts_eq.get) if pts_eq else "N/A",
        "bestia": min(pts_eq, key=pts_eq.get) if pts_eq else "N/A",
        "exactos": exactos, "signos": signos, "fallos": len(df_m)-(exactos+signos),
        "avg_g": (df_m['P_L']+df_m['P_V']).mean(), "real_g": (df_m['R_L']+df_m['R_V']).mean()
    }

# --- 3. APP ---
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
        st.title("🏆 Porra League 2026")
        u_in = st.text_input("Usuario")
        p_in = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            df_u = leer_datos("Usuarios")
            if not df_u.empty:
                user_db = df_u[(df_u['Usuario'].astype(str) == str(u_in)) & (df_u['Password'].astype(str) == str(p_in))]
                if not user_db.empty:
                    st.session_state.autenticado, st.session_state.user, st.session_state.rol = True, u_in, user_db.iloc[0]['Rol']
                    st.rerun()
                else: st.error("❌ Datos incorrectos")
        if st.button("Registrarse"):
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
        mi_f = foto_dict.get(st.session_state.user)
        if mi_f and pd.notna(mi_f) and os.path.exists(str(mi_f)): st.image(str(mi_f), width=75)
        else: st.subheader("👤")
    with c_h2: st.title(f"Hola, {st.session_state.user} 👋")
    with c_h3: 
        if st.button("Salir"): st.session_state.autenticado = False; st.rerun()

    j_global = st.selectbox("📅 Jornada Seleccionada:", list(JORNADAS.keys()), key="global_j")
    st.divider()
    tabs = st.tabs(["✍️ Apuestas", "👀 Otros", "📊 Clasificación", "📈 Estadísticas PRO", "🏆 Detalles", "🔮 Simulador", "⚙️ Admin"])

    with tabs[0]: # APUESTAS
        if st.session_state.rol != "admin":
            mis_p = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)]
            df_rj = df_r_all[df_r_all['Jornada'] == j_global]
            env = []
            for i, (loc, vis) in enumerate(JORNADAS[j_global]):
                m_id, b, t = f"{loc}-{vis}", False, "Normal"
                dl, dv, dp = 0, 0, False
                if not mis_p.empty:
                    pr = mis_p[mis_p['Partido'] == m_id]
                    if not pr.empty: dl, dv, dp = int(pr.iloc[0]['P_L']), int(pr.iloc[0]['P_V']), str(pr.iloc[0]['Publica']) == "SI"
                if not df_rj.empty and m_id in df_rj['Partido'].values:
                    inf = df_rj[df_rj['Partido'] == m_id].iloc[0]
                    t, b = inf['Tipo'], datetime.now() > datetime.strptime(str(inf['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                
                st.markdown(f"#### {t} {'🔒' if b else '🔓'}")
                c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 0.5, 2, 1, 2])
                with c1: 
                    lg = get_logo(loc)
                    if lg: st.image(lg, width=65)
                    else: st.markdown("⚽")
                with c2: pl = st.number_input(f"{loc}", 0, value=dl, key=f"l_{j_global}_{i}", disabled=b)
                with c3: st.markdown("<br>VS", unsafe_allow_html=True)
                with c4: pv = st.number_input(f"{vis}", 0, value=dv, key=f"v_{j_global}_{i}", disabled=b)
                with c5:
                    lv = get_logo(vis)
                    if lv: st.image(lv, width=65)
                    else: st.markdown("⚽")
                with c6: pub = st.checkbox("Público", value=dp, key=f"pb_{j_global}_{i}", disabled=b)
                env.append({"Usuario": st.session_state.user, "Jornada": j_global, "Partido": m_id, "P_L": pl, "P_V": pv, "Publica": "SI" if pub else "NO"})
            if st.button("💾 Guardar Porra"):
                old = df_p_all[~((df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global))]
                conn.update(worksheet="Predicciones", data=pd.concat([old, pd.DataFrame(env)], ignore_index=True))
                st.success("¡Guardado!")

    with tabs[1]: # OTROS
        p_pub = df_p_all[(df_p_all['Jornada'] == j_global) & (df_p_all['Publica'] == "SI")]
        if p_pub.empty: st.info("No hay apuestas públicas todavía.")
        for u in p_pub['Usuario'].unique():
            if u != st.session_state.user:
                with st.expander(f"Apuestas de {u}"): st.table(p_pub[p_pub['Usuario'] == u][['Partido', 'P_L', 'P_V']])

    with tabs[2]: # RANKING DUAL CON FRASES ROTATORIAS
        tipo_r = st.radio("Tipo de Ranking:", ["General", "De esta Jornada"], horizontal=True)
        u_jug = [u for u in df_u_all['Usuario'].unique() if u not in admins]
        pts_list = []
        for u in u_jug:
            p = safe_float(df_base[df_base['Usuario']==u].iloc[0]['Puntos']) if tipo_r=="General" else 0.0
            u_p = df_p_all[(df_p_all['Usuario']==u) & (df_p_all['Jornada']==j_global)] if tipo_r=="De esta Jornada" else df_p_all[df_p_all['Usuario']==u]
            for r in u_p.itertuples():
                m = df_r_all[(df_r_all['Jornada']==r.Jornada)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
                if not m.empty: p += calcular_puntos(r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'])
            pts_list.append({"Usuario": u, "Puntos": p})
        df_rank = pd.DataFrame(pts_list).sort_values("Puntos", ascending=False)
        df_rank['Posicion'] = range(1, len(df_rank)+1)

        for _, row in df_rank.iterrows():
            if row['Posicion'] <= 2: frase_t = random.choice(FRASES_PUESTOS['oro'])
            elif row['Posicion'] <= 4: frase_t = random.choice(FRASES_PUESTOS['plata'])
            elif row['Posicion'] <= 6: frase_t = random.choice(FRASES_PUESTOS['bronce'])
            else: frase_t = random.choice(FRASES_PUESTOS['barro'])
            
            l_u = calcular_logros_u(row['Usuario'], df_p_all, df_r_all, j_global, df_rank)
            icons = "".join([LOGROS_DATA[lid]['icon'] for lid in l_u])
            n, d, r = obtener_perfil_apostador(df_p_all[df_p_all['Usuario']==row['Usuario']])

            c1, c2, c3, c4 = st.columns([0.5, 1.2, 4, 1.5])
            with c1: st.markdown(f"### #{row['Posicion']}")
            with c2:
                f_p = foto_dict.get(row['Usuario'])
                if f_p and pd.notna(f_p) and os.path.exists(str(f_p)): st.image(str(f_p), width=85)
                else: st.subheader("👤")
            with c3:
                st.markdown(f"**{row['Usuario']}** {icons}")
                st.info(f"_{frase_t[0]}_ \n\n **— {frase_t[1]}**")
                st.progress(r); st.caption(f"{n} | {d}")
            with c4: st.markdown(f"#### {row['Puntos']:.2f} pts")
            st.divider()

    with tabs[3]: # STATS PRO
        st.header("📊 ADN del Apostador")
        u_sel = st.selectbox("Analizar a:", u_jug)
        adn = analizar_adn_pro(u_sel, df_p_all, df_r_all)
        if adn:
            c1, c2, c3 = st.columns(3)
            c1.metric("⭐ Amuleto", adn['amuleto'])
            c2.metric("💀 Bestia Negra", adn['bestia'])
            c3.metric("🎯 % Precisión", f"{(adn['signos']+adn['exactos'])/(adn['exactos']+adn['signos']+adn['fallos'])*100:.1f}%")
            st.divider()
            f1, f2 = st.columns(2)
            with f1: st.plotly_chart(px.pie(values=[adn['exactos'], adn['signos'], adn['fallos']], names=['Plenos', 'Signos', 'Fallos'], color_discrete_sequence=['#2baf2b', '#ffd700', '#ff4b4b']), use_container_width=True)
            with f2:
                st.subheader("⚽ Sesgo de Goles")
                st.write(f"Media Goles Predicha: **{adn['avg_g']:.2f}**")
                st.write(f"Media Goles Real: **{adn['real_g']:.2f}**")
                if adn['avg_g'] - adn['real_g'] > 0.5: st.warning("Eres un Optimista del Gol")
                elif adn['avg_g'] - adn['real_g'] < -0.5: st.info("Eres un Amarrategui")
                else: st.success("Ojo Clínico")
        else: st.info("Faltan partidos finalizados para el análisis.")

    with tabs[4]: # DETALLES
        df_rf = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "SI")]
        if not df_rf.empty:
            jugs = [u for u in df_u_all['Usuario'].unique() if u not in admins]
            c_m = st.columns([2] + [1]*len(jugs))
            for i, u in enumerate(jugs):
                fp = foto_dict.get(u)
                if fp and pd.notna(fp) and os.path.exists(str(fp)): c_m[i+1].image(str(fp), width=45)
                else: c_m[i+1].write(u[:3])
            m_p = pd.DataFrame(index=df_rf['Partido'].unique(), columns=jugs)
            for p in m_p.index:
                inf = df_rf[df_rf['Partido'] == p].iloc[0]
                for u in jugs:
                    up = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == j_global) & (df_p_all['Partido'] == p)]
                    pts = calcular_puntos(up.iloc[0]['P_L'], up.iloc[0]['P_V'], inf['R_L'], inf['R_V'], inf['Tipo']) if not up.empty else 0.0
                    m_p.at[p, u] = pts
            st.dataframe(m_p)
        else: st.warning("No hay partidos finalizados en esta jornada.")

    with tabs[5]: # SIMULADOR
        st.header("🔮 Simulador LaLiga")
        usr_sim = st.selectbox("Simular según:", u_jug)
        if st.button("🚀 Ejecutar Simulación"):
            sim = {k: v.copy() for k, v in STATS_LALIGA_BASE.items()}
            for p in df_p_all[df_p_all['Usuario']==usr_sim].itertuples():
                try:
                    tl, tv = p.Partido.split('-')
                    if tl in sim and tv in sim:
                        sim[tl]["PJ"]+=1; sim[tv]["PJ"]+=1
                        sim[tl]["GF"]+=p.P_L; sim[tl]["GC"]+=p.P_V
                        sim[tv]["GF"]+=p.P_V; sim[tv]["GC"]+=p.P_L
                        if p.P_L > p.P_V: sim[tl]["Pts"] += 3; sim[tl]["V"]+=1; sim[tv]["D"]+=1
                        elif p.P_V > p.P_L: sim[tv]["Pts"] += 3; sim[tv]["V"]+=1; sim[tl]["D"]+=1
                        else: sim[tl]["Pts"] += 1; sim[tv]["Pts"] += 1; sim[tl]["E"]+=1; sim[tv]["E"]+=1
                except: continue
            df_s = pd.DataFrame.from_dict(sim, orient='index').reset_index().sort_values("Pts", ascending=False)
            df_s['DG'] = df_s['GF'] - df_s['GC']
            df_s['Pos'] = range(1, 21)
            st.dataframe(df_s[['Pos', 'index', 'PJ', 'V', 'E', 'D', 'GF', 'GC', 'DG', 'Pts']], hide_index=True, use_container_width=True)

    with tabs[6]: # ADMIN
        if st.session_state.rol == "admin":
            st.header("🛠️ Panel Control")
            a_tabs = st.tabs(["⭐ Bases", "📸 Fotos", "⚽ Resultados"])
            with a_tabs[0]:
                upd_b = []
                for u in [usr for usr in df_u_all['Usuario'].unique() if usr not in admins]:
                    pts_ex = safe_float(df_base[df_base['Usuario'] == u].iloc[0]['Puntos']) if not df_base.empty and u in df_base['Usuario'].values else 0.0
                    val = st.number_input(f"Base {u}", value=pts_ex, key=f"ba_{u}")
                    upd_b.append({"Usuario": u, "Puntos": val})
                if st.button("Guardar Bases"):
                    conn.update(worksheet="PuntosBase", data=pd.DataFrame(upd_b))
                    st.success("Ok")
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
                    if st.button("Asociar"):
                        conn.update(worksheet="ImagenesPerfil", data=pd.DataFrame(upd_f))
                        st.success("Ok")
            with a_tabs[2]:
                r_env, h_p = [], [time(h, m) for h in range(12, 23) for m in [0, 15, 30, 45]]
                for i, (l, v) in enumerate(JORNADAS[j_global]):
                    m_i = f"{l}-{v}"
                    st.subheader(f"⚽ {m_i}")
                    ex = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Partido'] == m_i)] if not df_r_all.empty else pd.DataFrame()
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
                    fina = c6.checkbox("F", value=f, key=f"fi_{j_global}_{i}")
                    r_env.append({"Jornada": j_global, "Partido": m_i, "Tipo": tip_a, "R_L": rla, "R_V": rva, "Hora_Inicio": datetime.combine(fec_a, hor_a).strftime("%Y-%m-%d %H:%M:%S"), "Finalizado": "SI" if fina else "NO"})
                if st.button("Actualizar Jornada"):
                    old = df_r_all[df_r_all['Jornada'] != j_global]
                    conn.update(worksheet="Resultados", data=pd.concat([old, pd.DataFrame(r_env)], ignore_index=True))
                    st.success("¡Resultados actualizados!")
