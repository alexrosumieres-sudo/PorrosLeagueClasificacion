import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time
import os
import plotly.express as px
import random
import itertools
import numpy as np

# --- 1. CONFIGURACIONES GENERALES ---
PERFILES_DIR = "perfiles/"
LOGOS_DIR = "logos/"

NIVEL_EQUIPOS = {
    "Real Madrid": 1, "Barcelona": 1, "Villarreal": 1, "Atlético": 1,
    "Betis": 2, "Espanyol": 2, "Celta": 2, "R. Sociedad": 2, "Athletic": 2,
    "Osasuna": 3, "Getafe": 3, "Girona": 3, "Sevilla": 3, "Alavés": 3, "Valencia": 3, "Elche": 3, "Rayo": 3,
    "Mallorca": 4, "Levante": 4, "Oviedo": 4
}

# Datos oficiales tras la Jornada 24 (Base para el simulador)
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

# --- FRASES MÍTICAS ---
FRASES_POR_PUESTO = {
    1: [("Ganar, ganar y volver a ganar.", "Luis Aragonés"), ("Siuuuuu.", "CR7")],
    2: [("Perder una final es lo peor.", "Messi"), ("Lo intentamos.", "Sergio Ramos")],
    3: [("Partido a partido.", "Simeone"), ("Ni tan mal.", "Anónimo")],
    4: [("El fútbol es así.", "Boskov"), ("Hay que seguir.", "Ancelotti")],
    5: [("¿Por qué?", "Mourinho"), ("Fútbol es fútbol.", "Boskov")],
    6: [("Prefiero no hablar.", "Mourinho"), ("Hay que levantarse.", "CR7")],
    7: [("Estamos en la UVI.", "Clemente"), ("Salimos como nunca...", "Di Stéfano")]
}

LOGROS_DATA = {
    "guru": {"icon": "🔮", "name": "El Gurú", "desc": "Pleno en Esquizo."},
    "cima": {"icon": "🏔️", "name": "En la Cima", "desc": "Líder general."},
    "pleno": {"icon": "💯", "name": "Pleno", "desc": "Puntuado en los 10."}
}

# --- 2. FUNCIONES DE APOYO ---
@st.cache_data(ttl=60)
def leer_datos(pestaña):
    try:
        sheet_id = "1vFgccrCqmGrs9QfP8kxY_cESbRaJ_VxpsoAz-ZyL14E"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={pestaña}"
        return pd.read_csv(url)
    except: return pd.DataFrame()

def safe_float(valor):
    try:
        if pd.isna(valor) or str(valor).strip() == "": return 0.0
        return float(str(valor).replace(',', '.'))
    except: return 0.0

def get_logo(equipo):
    path = LOGOS.get(equipo)
    if path and os.path.exists(path): return path
    return None

def calcular_puntos(p_l, p_v, r_l, r_v, tipo="Normal"):
    try:
        p_l, p_v, r_l, r_v = float(p_l), float(p_v), float(r_l), float(r_v)
        p_ganador, p_diff, p_exacto = SCORING.get(tipo, SCORING["Normal"])
        if p_l == r_l and p_v == r_v: return p_exacto
        signo_p = (p_l > p_v) - (p_l < p_v)
        signo_r = (r_l > r_v) - (r_l < r_v)
        if signo_p == signo_r:
            return p_diff if (p_l - p_v) == (r_l - r_v) else p_ganador
        return 0.0
    except: return 0.0

def obtener_perfil_apostador(df_u):
    if df_u is None or df_u.empty: return "Novato 🐣", "Sin datos.", 0.0
    avg_g = (df_u['P_L'] + df_u['P_V']).mean()
    riesgo = min(avg_g / 5.0, 1.0)
    if avg_g > 3.4: return "BUSCADOR DE PLENOS 🤪", "Ataque total.", riesgo
    if avg_g < 2.1: return "CONSERVADOR 🛡️", "Fiel al 1-0.", riesgo
    return "ESTRATEGA ⚖️", "Equilibrado.", riesgo

def calcular_logros_u(usuario, df_p_all, df_r_all, jornada_sel, ranking):
    logros = []
    if not ranking.empty and ranking.iloc[0]['Usuario'] == usuario: logros.append("cima")
    u_p = df_p_all[(df_p_all['Usuario'] == usuario) & (df_p_all['Jornada'] == jornada_sel)]
    res_j = df_r_all[(df_r_all['Jornada'] == jornada_sel) & (df_r_all['Finalizado'] == "SI")]
    if u_p.empty or res_j.empty: return logros
    pts_j = []
    for row in u_p.itertuples():
        m = res_j[res_j['Partido'] == row.Partido]
        if not m.empty:
            pts_j.append(calcular_puntos(row.P_L, row.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo']))
    if len(pts_j) == 10 and all(p > 0 for p in pts_j): logros.append("pleno")
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
    ex = len(df_m[df_m.apply(lambda x: x.P_L == x.R_L and x.P_V == x.R_V, axis=1)])
    sig = len(df_m[df_m['Pts'] > 0]) - ex
    return {
        "amuleto": max(pts_eq, key=pts_eq.get) if pts_eq else "N/A",
        "bestia": min(pts_eq, key=pts_eq.get) if pts_eq else "N/A",
        "exactos": ex, "signos": sig, "fallos": len(df_m)-(ex+sig),
        "avg_g": (df_m['P_L']+df_m['P_V']).mean(), "real_g": (df_m['R_L']+df_m['R_V']).mean()
    }

def simular_oraculo(usuarios, df_p_all, df_r_all, jornada_sel):
    res_sim = [(0,0), (1,0), (0,1), (1,1), (2,1), (1,2), (2,2), (3,1), (0,2)]
    pend = df_r_all[(df_r_all['Jornada'] == jornada_sel) & (df_r_all['Finalizado'] == "NO")]
    if pend.empty or len(pend) > 3: return None
    p_id, t_id = pend['Partido'].tolist(), pend['Tipo'].tolist()
    victorias = {u: 0 for u in usuarios}
    combos = list(itertools.product(res_sim, repeat=len(p_id)))
    for c in combos:
        esc = {u: 0.0 for u in usuarios}
        for u in usuarios:
            u_p = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == jornada_sel)]
            for r in u_p.itertuples():
                m_r = df_r_all[(df_r_all['Jornada']==jornada_sel)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
                if not m_r.empty: esc[u] += calcular_puntos(r.P_L, r.P_V, m_r.iloc[0]['R_L'], m_r.iloc[0]['R_V'], m_r.iloc[0]['Tipo'])
                for i, p_n in enumerate(p_id):
                    if r.Partido == p_n: esc[u] += calcular_puntos(r.P_L, r.P_V, c[i][0], c[i][1], t_id[i])
        mx = max(esc.values()); gan = [u for u, p in esc.items() if p == mx]
        for g in gan: victorias[g] += 1 / len(gan)
    return {u: (v/len(combos))*100 for u, v in victorias.items()}

# --- 3. APP ---
st.set_page_config(page_title="Porra League 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏆 Porra League 2026")
        u_in, p_in = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
        c1, c2 = st.columns(2)
        if c1.button("Entrar"):
            df_u = leer_datos("Usuarios")
            user = df_u[(df_u['Usuario'].astype(str) == u_in) & (df_u['Password'].astype(str) == p_in)]
            if not user.empty:
                st.session_state.autenticado, st.session_state.user, st.session_state.rol = True, u_in, user.iloc[0]['Rol']; st.rerun()
            else: st.error("❌ Credenciales incorrectas")
        if c2.button("Registrarse"):
            df_u = leer_datos("Usuarios")
            if u_in in df_u['Usuario'].values: st.error("❌ Usuario ya existe")
            else:
                nueva = pd.DataFrame([{"Usuario": u_in, "Password": p_in, "Rol": "user"}])
                conn.update(worksheet="Usuarios", data=pd.concat([df_u, nueva], ignore_index=True)); st.success("✅ Hecho")
else:
    # 1. CARGA DE DATOS
    df_perf = leer_datos("ImagenesPerfil")
    df_r_all, df_p_all, df_u_all, df_base = leer_datos("Resultados"), leer_datos("Predicciones"), leer_datos("Usuarios"), leer_datos("PuntosBase")
    foto_dict = df_perf.set_index('Usuario')['ImagenPath'].to_dict() if not df_perf.empty else {}
    u_jugadores = [u for u in df_u_all['Usuario'].unique() if u not in df_u_all[df_u_all['Rol']=='admin']['Usuario'].tolist()]

    # --- CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; color: #31333F; }
        .hero-bg { background: #f8f9fa; border-radius: 20px; padding: 25px; margin-bottom: 25px; border: 1px solid #dee2e6; }
        .kpi-box { background: white; border-radius: 12px; padding: 12px; text-align: center; border: 1px solid #eee; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        .kpi-label { font-size: 0.75em; color: #6c757d; font-weight: bold; text-transform: uppercase; }
        .kpi-value { font-size: 1.6em; font-weight: 800; color: #2baf2b; display: block; }
        .panini-card { background: #f8f9fb; border-radius: 15px; padding: 20px; border: 1px solid #e0e0e0; margin-bottom: 20px; }
        .quote-text { color: #4f4f4f; font-style: italic; border-left: 3px solid #2baf2b; padding-left: 10px; margin: 10px 0; }
        .pos-badge { background-color: #2baf2b; color: white; padding: 5px 15px; border-radius: 50%; font-weight: bold; }
        .match-box { background: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #eee; border-left: 5px solid #2baf2b; margin-bottom: 10px; }
        .crown { font-size: 2em; position: absolute; top: -35px; left: 35px; transform: rotate(-15deg); z-index: 10; }
        .section-tag { font-size: 0.7em; background: #31333F; color: white; padding: 2px 8px; border-radius: 5px; margin-bottom: 5px; display: inline-block; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚽ Menú Liga")
        j_global = st.selectbox("📅 Jornada:", list(JORNADAS.keys()), key="side_j")
        st.divider()
        # BOTÓN DE SALIR RESTAURADO
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    # --- CÁLCULO DE DASHBOARD HERO (LÍDER VS USUARIO) ---
    stats_hero = []
    for u in u_jugadores:
        pb_row = df_base[df_base['Usuario']==u]
        p_base = safe_float(pb_row['Puntos'].values[0]) if not pb_row.empty else 0.0
        u_p_hist = df_p_all[df_p_all['Usuario'] == u]
        p_acum = p_base
        for r in u_p_hist.itertuples():
            m = df_r_all[(df_r_all['Jornada']==r.Jornada)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
            if not m.empty: p_acum += calcular_puntos(r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'])
        stats_hero.append({"Usuario": u, "Puntos": p_acum})
    
    df_hero = pd.DataFrame(stats_hero).sort_values("Puntos", ascending=False).reset_index(drop=True)
    df_hero['Posicion'] = range(1, len(df_hero)+1)
    lider = df_hero.iloc[0]
    mi_pos = df_hero[df_hero['Usuario'] == st.session_state.user]['Posicion'].values[0]
    prox_p = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "NO")].sort_values("Hora_Inicio").head(1)

    st.title(f"Hola, {st.session_state.user} 👋")

    # --- RENDER DASHBOARD HERO ---
    with st.container():
        st.markdown('<div class="hero-bg">', unsafe_allow_html=True)
        col_lider, col_sep, col_datos = st.columns([1.5, 0.2, 3.5])
        
        with col_lider: # SECCIÓN DEL LÍDER
            st.markdown('<span class="section-tag">LÍDER ACTUAL</span>', unsafe_allow_html=True)
            st.markdown('<div style="position: relative; text-align: center;">', unsafe_allow_html=True)
            st.markdown('<span class="crown">👑</span>', unsafe_allow_html=True)
            f_l = foto_dict.get(lider['Usuario'])
            if f_l and os.path.exists(str(f_l)): st.image(f_l, width=90)
            else: st.markdown("<h2 style='margin:0;'>👤</h2>", unsafe_allow_html=True)
            st.markdown(f"**{lider['Usuario']}**<br><span style='color:#daa520; font-weight:bold;'>{lider['Puntos']:.2f} Pts</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_datos: # SECCIÓN TUS DATOS
            st.markdown('<span class="section-tag">TUS ESTADÍSTICAS</span>', unsafe_allow_html=True)
            c2, c3, c4 = st.columns(3)
            with c2: st.markdown(f'<div class="kpi-box"><span class="kpi-label">Tu Puesto</span><span class="kpi-value">#{mi_pos}</span></div>', unsafe_allow_html=True)
            with c3:
                if not prox_p.empty:
                    diff = datetime.strptime(str(prox_p.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S") - datetime.now()
                    h = max(0, int(diff.total_seconds() // 3600))
                    st.markdown(f'<div class="kpi-box"><span class="kpi-label">Cierre en</span><span class="kpi-value" style="color:{"#ff4b4b" if h<24 else "#2baf2b"}">{h}h</span></div>', unsafe_allow_html=True)
                else: st.markdown('<div class="kpi-box"><span class="kpi-label">Jornada</span><span class="kpi-value">Cerrada</span></div>', unsafe_allow_html=True)
            with c4:
                pts_h = 0.0
                u_p_h = df_p_all[(df_p_all['Usuario']==st.session_state.user) & (df_p_all['Jornada']==j_global)]
                for r in u_p_h.itertuples():
                    m = df_r_all[(df_r_all['Jornada']==j_global)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
                    if not m.empty: pts_h += calcular_puntos(r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'])
                st.markdown(f'<div class="kpi-box"><span class="kpi-label">Puntos Hoy</span><span class="kpi-value" style="color:#007bff;">{pts_h:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    usa_oraculo = 1 <= len(df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "NO")]) <= 3
    tabs = st.tabs(["✍️ Apuestas", "👀 Otros", "📊 Clasificación", "📈 Stats PRO", "🏆 Detalles", "🔮 Simulador", "🎲 Oráculo", "⚙️ Admin"])

    with tabs[0]: # APUESTAS
        u_p_s = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)]
        env = []
        for i, (loc, vis) in enumerate(JORNADAS[j_global]):
            m_id, dl, dv, dp, lock, t = f"{loc}-{vis}", 0, 0, "NO", False, "Normal"
            if not u_p_s.empty:
                r_p = u_p_s[u_p_s['Partido'] == m_id]
                if not r_p.empty: dl, dv, dp = int(r_p.iloc[0]['P_L']), int(r_p.iloc[0]['P_V']), r_p.iloc[0]['Publica']
            res_r = df_r_all[(df_r_all['Jornada']==j_global) & (df_r_all['Partido']==m_id)]
            if not res_r.empty:
                t = res_r.iloc[0]['Tipo']
                lock = datetime.now() > datetime.strptime(str(res_r.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
            st.markdown(f'<div class="match-box">', unsafe_allow_html=True)
            c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 0.5, 2, 1, 2])
            with c1:
                lg = get_logo(loc)
                if lg: st.image(lg, width=45)
                else: st.write("⚽")
            with c2: pl = st.number_input(f"{loc}", 0, 9, dl, key=f"pl_{i}", disabled=lock)
            with c4: pv = st.number_input(f"{vis}", 0, 9, dv, key=f"pv_{i}", disabled=lock)
            with c5:
                lv = get_logo(vis)
                if lv: st.image(lv, width=45)
                else: st.write("⚽")
            with c6: pub = st.checkbox("Pública", dp=="SI", key=f"pb_{i}", disabled=lock)
            st.markdown('</div>', unsafe_allow_html=True)
            env.append({"Usuario": st.session_state.user, "Jornada": j_global, "Partido": m_id, "P_L": pl, "P_V": pv, "Publica": "SI" if pub else "NO"})
        if st.button("💾 Guardar Todo"):
            old = df_p_all[~((df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global))]
            conn.update(worksheet="Predicciones", data=pd.concat([old, pd.DataFrame(env)], ignore_index=True)); st.cache_data.clear(); st.success("OK")

    with tabs[1]: # OTROS
        p_p_j = df_p_all[(df_p_all['Jornada'] == j_global) & (df_p_all['Publica'] == "SI")]
        if p_p_j.empty: st.info("Sin apuestas públicas.")
        else:
            for u in p_p_j['Usuario'].unique():
                if u != st.session_state.user:
                    with st.expander(f"Apuestas de {u}"): st.table(p_p_j[p_p_j['Usuario'] == u][['Partido', 'P_L', 'P_V']])

    with tabs[2]: # CLASIFICACIÓN
        tipo_r = st.radio("Ranking:", ["General", "Jornada"], horizontal=True)
        pts_l = []
        for u in u_jugadores:
            if tipo_r == "General":
                pb_r = df_base[df_base['Usuario'] == u]
                p_b = safe_float(pb_r['Puntos'].values[0]) if not pb_r.empty else 0.0
                u_p_h = df_p_all[df_p_all['Usuario'] == u]
            else: p_b, u_p_h = 0.0, df_p_all[(df_p_all['Usuario']==u) & (df_p_all['Jornada']==j_global)]
            p_a = p_b
            for r in u_p_h.itertuples():
                m = df_r_all[(df_r_all['Jornada']==r.Jornada)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
                if not m.empty: p_a += calcular_puntos(r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'])
            pts_l.append({"Usuario": u, "Puntos": p_a})
        df_rk = pd.DataFrame(pts_l).sort_values("Puntos", ascending=False)
        df_rk['Posicion'] = range(1, len(df_rk)+1)
        for _, row in df_rk.iterrows():
            pos = row['Posicion']
            f_t = random.choice(FRASES_POR_PUESTO.get(pos if pos <= 7 else 7))
            st.markdown(f'<div class="panini-card">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([0.6, 1.2, 3.5, 1.5])
            with c1: st.markdown(f'<br><span class="pos-badge">#{pos}</span>', unsafe_allow_html=True)
            with c2:
                img = foto_dict.get(row['Usuario'])
                if img and os.path.exists(str(img)): st.image(img, width=80)
                else: st.markdown("### 👤")
            with c3: st.markdown(f"### {row['Usuario']}"); st.markdown(f'<div class="quote-text">"{f_t[0]}"<br><small>— {f_t[1]}</small></div>', unsafe_allow_html=True)
            with c4: st.markdown(f'<br><span style="font-size: 2em; font-weight: bold; color: #2baf2b;">{row["Puntos"]:.2f}</span><br>Pts', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tabs[3]: # STATS PRO
        u_sel = st.selectbox("Analizar:", u_jugadores)
        adn = analizar_adn_pro(u_sel, df_p_all, df_r_all)
        if adn:
            c1, c2, c3 = st.columns(3); c1.metric("⭐ Amuleto", adn['amuleto']); c2.metric("💀 Bestia", adn['bestia']); c3.metric("🎯 %", f"{(adn['signos']+adn['exactos'])/(adn['exactos']+adn['signos']+adn['fallos'])*100:.1f}%")
            st.plotly_chart(px.pie(values=[adn['exactos'], adn['signos'], adn['fallos']], names=['Plenos', 'Signos', 'Fallos'], color_discrete_sequence=['#2baf2b', '#ffd700', '#ff4b4b']), use_container_width=True)

    with tabs[4]: # DETALLES
        df_rf = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "SI")]
        if not df_rf.empty:
            m_p = pd.DataFrame(index=df_rf['Partido'].unique(), columns=u_jugadores)
            for p in m_p.index:
                inf = df_rf[df_rf['Partido'] == p].iloc[0]
                for u in u_jugadores:
                    up = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == j_global) & (df_p_all['Partido'] == p)]
                    m_p.at[p, u] = calcular_puntos(up.iloc[0]['P_L'], up.iloc[0]['P_V'], inf['R_L'], inf['R_V'], inf['Tipo']) if not up.empty else 0.0
            st.dataframe(m_p.astype(float))
        else: st.info("Sin partidos finalizados.")

    with tabs[5]: # SIMULADOR
        usr_s = st.selectbox("Basar en:", u_jugadores)
        if st.button("Simular Liga"):
            sim = {k: v.copy() for k, v in STATS_LALIGA_BASE.items()}
            for p in df_p_all[df_p_all['Usuario']==usr_s].itertuples():
                try:
                    tl, tv = p.Partido.split('-')
                    if tl in sim and tv in sim:
                        sim[tl]["PJ"]+=1; sim[tv]["PJ"]+=1
                        if p.P_L > p.P_V: sim[tl]["Pts"]+=3; sim[tl]["V"]+=1; sim[tv]["D"]+=1
                        elif p.P_V > p.P_L: sim[tv]["Pts"]+=3; sim[tv]["V"]+=1; sim[tl]["D"]+=1
                        else: sim[tl]["Pts"]+=1; sim[tv]["Pts"]+=1; sim[tl]["E"]+=1; sim[tv]["E"]+=1
                except: continue
            st.dataframe(pd.DataFrame.from_dict(sim, orient='index').sort_values("Pts", ascending=False))

    with tabs[6]: # ORÁCULO
        if usa_oraculo:
            probs = simular_oraculo(u_jugadores, df_p_all, df_r_all, j_global)
            if probs:
                for u, v in sorted(probs.items(), key=lambda x: x[1], reverse=True):
                    if v > 0: st.write(f"**{u}**: {v:.1f}%"); st.progress(v/100)
        else: st.info("Se activa con 1-3 partidos restantes.")

    with tabs[7]: # ADMIN
        if st.session_state.rol == "admin":
            r_env = []
            for i, (l, v) in enumerate(JORNADAS[j_global]):
                m_id = f"{l}-{v}"
                prev = df_r_all[(df_r_all['Jornada']==j_global) & (df_r_all['Partido']==m_id)]
                rl, rv, fin, t, hor = 0, 0, False, "Normal", "2026-02-23 21:00:00"
                if not prev.empty: 
                    rl, rv, fin = int(prev.iloc[0]['R_L']), int(prev.iloc[0]['R_V']), prev.iloc[0]['Finalizado']=="SI"
                    t, hor = prev.iloc[0]['Tipo'], prev.iloc[0]['Hora_Inicio']
                c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
                with c1: st.write(m_id)
                nt = c2.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], index=["Normal", "Doble", "Esquizo"].index(t), key=f"at_{i}")
                nrl, nrv, nfi = c3.number_input("L", 0, 9, rl, key=f"arl_{i}"), c4.number_input("V", 0, 9, rv, key=f"arv_{i}"), c5.checkbox("Fin", fin, key=f"afi_{i}")
                r_env.append({"Jornada": j_global, "Partido": m_id, "Tipo": nt, "R_L": nrl, "R_V": nrv, "Hora_Inicio": hor, "Finalizado": "SI" if nfi else "NO"})
            if st.button("Actualizar"):
                otros = df_r_all[df_r_all['Jornada'] != j_global]
                conn.update(worksheet="Resultados", data=pd.concat([otros, pd.DataFrame(r_env)], ignore_index=True)); st.cache_data.clear(); st.rerun()
