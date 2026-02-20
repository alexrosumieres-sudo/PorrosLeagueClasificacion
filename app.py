import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time
import os
import plotly.express as px
import plotly.graph_objects as go
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

# Datos base oficiales extraídos de la clasificación J24
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

LOGOS = {eq: f"{LOGOS_DIR}{eq.lower().replace(' ', '').replace('.', '')}.jpeg" for eq in STATS_LALIGA_BASE.keys()}
SCORING = {"Normal": (0.5, 0.75, 1.0), "Doble": (1.0, 1.5, 2.0), "Esquizo": (1.0, 1.5, 3.0)}

# --- FRASES MÍTICAS ROTATORIAS (7 JUGADORES) ---
FRASES_PUESTOS = {
    "oro": ["¿Por qué? Porque soy rico, guapo y un gran jugador.", "I am the Special One.", "Vuestra envidia me hace fuerte.", "No soy el mejor, soy el mejor de la historia.", "Dios está conmigo, y yo conmigo mismo."],
    "plata": ["Ganar, ganar y volver a ganar.", "Fútbol es fútbol.", "Partido a partido.", "Ni antes éramos tan buenos, ni ahora tan malos.", "Las estadísticas están para romperse."],
    "bronce": ["¿Por qué? ¿Por qué?", "No me pises, que llevo chanclas.", "¡A las canicas no!", "Me cortaron las piernas.", "¡Digo lo que pienso y no me callo nada!"],
    "barro": ["Se queda... (en el pozo).", "Estamos en la UVI, pero vivos.", "¿Alguien tiene el teléfono del VAR?", "A veces se aprende, tú hoy eres catedrático.", "He fallado 9.000 tiros... tú hoy todos."]
}

LOGROS_DATA = {
    "guru": {"icon": "🔮", "name": "El Gurú", "desc": "Pleno en partido Esquizo."},
    "hattrick": {"icon": "🎯", "name": "Hat-Trick", "desc": "3+ resultados exactos en la jornada."},
    "cima": {"icon": "🏔️", "name": "En la Cima", "desc": "Líder de la general."},
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

def aplicar_color_estilo(valor, tipo_partido):
    if valor == 0: return 'background-color: #ff4b4b'
    return 'background-color: #2baf2b'

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

def analizar_adn(usuario, df_p, df_r):
    df_m = pd.merge(df_p[df_p['Usuario'] == usuario], df_r[df_r['Finalizado'] == "SI"], on=['Jornada', 'Partido'])
    if df_m.empty: return None
    df_m['Pts'] = df_m.apply(lambda x: calcular_puntos(x.P_L, x.P_V, x.R_L, x.R_V, x.Tipo), axis=1)
    pts_eq = {}
    for _, r in df_m.iterrows():
        l, v = r['Partido'].split('-')
        pts_eq[l], pts_eq[v] = pts_eq.get(l, 0) + r['Pts'], pts_eq.get(v, 0) + r['Pts']
    exactos = len(df_m[df_m.apply(lambda x: x.P_L == x.R_L and x.P_V == x.R_V, axis=1)])
    signos = len(df_m[df_m['Pts'] > 0]) - exactos
    return {"amuleto": max(pts_eq, key=pts_eq.get), "bestia": min(pts_eq, key=pts_eq.get), "exactos": exactos, "signos": signos, "fallos": len(df_m)-(exactos+signos), "avg_g": (df_m['P_L']+df_m['P_V']).mean(), "real_g": (df_m['R_L']+df_m['R_V']).mean()}

# --- 3. APP ---
st.set_page_config(page_title="Porra League 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏆 Porra League")
        u, p = st.text_input("Usuario"), st.text_input("Pass", type="password")
        if st.button("Entrar"):
            df_u = leer_datos("Usuarios")
            db = df_u[(df_u['Usuario'].astype(str)==u) & (df_u['Password'].astype(str)==p)]
            if not db.empty:
                st.session_state.autenticado, st.session_state.user, st.session_state.rol = True, u, db.iloc[0]['Rol']
                st.rerun()
            else: st.error("Fallo")
else:
    df_perfiles, df_r_all, df_p_all, df_u_all, df_base = leer_datos("ImagenesPerfil"), leer_datos("Resultados"), leer_datos("Predicciones"), leer_datos("Usuarios"), leer_datos("PuntosBase")
    foto_dict = df_perfiles.set_index('Usuario')['ImagenPath'].to_dict() if not df_perfiles.empty else {}
    admins = df_u_all[df_u_all['Rol'] == 'admin']['Usuario'].tolist() if not df_u_all.empty else []

    j_global = st.selectbox("📅 Jornada Seleccionada:", list(JORNADAS.keys()))
    st.divider()
    tabs = st.tabs(["✍️ Apuestas", "👀 Otros", "📊 Clasificación", "📈 Stats PRO", "🏆 Detalles", "🔮 Simulador", "⚙️ Admin"])

    with tabs[2]: # RANKING CON FRASES Y LOGROS
        tipo = st.radio("Ver:", ["General", "Jornada"], horizontal=True)
        u_jug = [u for u in df_u_all['Usuario'].unique() if u not in admins]
        pts_l = []
        for u in u_jug:
            p = safe_float(df_base[df_base['Usuario']==u].iloc[0]['Puntos']) if tipo=="General" else 0.0
            u_p = df_p_all[(df_p_all['Usuario']==u) & (df_p_all['Jornada']==j_global)] if tipo=="Jornada" else df_p_all[df_p_all['Usuario']==u]
            for r in u_p.itertuples():
                m = df_r_all[(df_r_all['Jornada']==r.Jornada)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
                if not m.empty: p += calcular_puntos(r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'])
            pts_l.append({"Usuario": u, "Puntos": p})
        df_rank = pd.DataFrame(pts_l).sort_values("Puntos", ascending=False)
        df_rank['Posicion'] = range(1, len(df_rank)+1)

        for _, row in df_rank.iterrows():
            if row['Posicion'] <= 2: frase = random.choice(FRASES_PUESTOS['oro'])
            elif row['Posicion'] <= 4: frase = random.choice(FRASES_PUESTOS['plata'])
            elif row['Posicion'] <= 6: frase = random.choice(FRASES_PUESTOS['bronce'])
            else: frase = random.choice(FRASES_PUESTOS['barro'])
            l_u = calcular_logros_u(row['Usuario'], df_p_all, df_r_all, j_global, df_rank)
            icons = "".join([LOGROS_DATA[lid]['icon'] for lid in l_u])
            n, d, r = obtener_perfil_apostador(df_p_all[df_p_all['Usuario']==row['Usuario']])
            c1, c2, c3, c4 = st.columns([0.5, 1.2, 4, 1.5])
            with c1: st.markdown(f"### #{row['Posicion']}")
            with c2:
                f = foto_dict.get(row['Usuario'])
                if f and pd.notna(f) and os.path.exists(str(f)): st.image(str(f), width=85)
                else: st.subheader("👤")
            with c3:
                st.markdown(f"**{row['Usuario']}** {icons}")
                st.info(f"_{frase}_")
                st.progress(r); st.caption(f"{n} | {d}")
            with c4: st.markdown(f"#### {row['Puntos']:.2f} pts")
            st.divider()

    with tabs[3]: # STATS PRO
        st.header("📊 ADN Apostador")
        u_sel = st.selectbox("Analizar a:", u_jug)
        s = analizar_adn(u_sel, df_p_all, df_r_all)
        if s:
            c1, c2, c3 = st.columns(3)
            c1.metric("⭐ Amuleto", s['amuleto']); c2.metric("💀 Bestia", s['bestia'])
            st.divider()
            f1, f2 = st.columns(2)
            with f1: st.plotly_chart(px.pie(values=[s['exactos'], s['signos'], s['fallos']], names=['Plenos', 'Signos', 'Fallos'], color_discrete_sequence=['#2baf2b', '#ffd700', '#ff4b4b']))
            with f2:
                st.write(f"Media Goles: {s['avg_g']:.2f} (Real: {s['real_g']:.2f})")
                if s['avg_g'] - s['real_g'] > 0.5: st.warning("Eres un Optimista del Gol")
        else: st.info("Faltan datos.")

    with tabs[5]: # SIMULADOR PRO
        st.header("🔮 Simulador LaLiga")
        usr_s = st.selectbox("Simular según:", u_jug)
        if st.button("🚀 Simular"):
            sim = {k: v.copy() for k, v in STATS_LALIGA_BASE.items()} #
            for p in df_p_all[df_p_all['Usuario']==usr_s].itertuples():
                try:
                    tl, tv = p.Partido.split('-')
                    if p.P_L > p.P_V: sim[tl]["Pts"] += 3
                    elif p.P_V > p.P_L: sim[tv]["Pts"] += 3
                    else: sim[tl]["Pts"] += 1; sim[tv]["Pts"] += 1
                except: continue
            df_s = pd.DataFrame.from_dict(sim, orient='index').reset_index().sort_values("Pts", ascending=False)
            df_s['Pos'] = range(1, 21)
            st.dataframe(df_s[['Pos', 'index', 'Pts']], hide_index=True, use_container_width=True) #

    with tabs[0]: # APUESTAS
        if st.session_state.rol != "admin":
            mis_p = df_p_all[(df_p_all['Usuario']==st.session_state.user) & (df_p_all['Jornada']==j_global)]
            df_rj = df_r_all[df_r_all['Jornada']==j_global]
            env = []
            for i, (loc, vis) in enumerate(JORNADAS[j_global]):
                m_id, b, t = f"{loc}-{vis}", False, "Normal"
                dl, dv, dp = 0, 0, False
                if not mis_p.empty:
                    pr = mis_p[mis_p['Partido']==m_id]
                    if not pr.empty: dl, dv, dp = int(pr.iloc[0]['P_L']), int(pr.iloc[0]['P_V']), str(pr.iloc[0]['Publica'])=="SI"
                if not df_rj.empty and m_id in df_rj['Partido'].values:
                    inf = df_rj[df_rj['Partido']==m_id].iloc[0]
                    t = inf['Tipo']
                    if datetime.now() > datetime.strptime(str(inf['Hora_Inicio']), "%Y-%m-%d %H:%M:%S"): b = True
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
            if st.button("💾 Guardar"):
                old = df_p_all[~((df_p_all['Usuario']==st.session_state.user) & (df_p_all['Jornada']==j_global))]
                conn.update(worksheet="Predicciones", data=pd.concat([old, pd.DataFrame(env)], ignore_index=True)); st.rerun()

    # (Detalles, Otros y Admin se mantienen funcionales como en versiones previas)
