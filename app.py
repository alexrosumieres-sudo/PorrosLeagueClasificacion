import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time
import os
import plotly.express as px
import random
import itertools
import numpy as np
import time

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
@st.cache_data(ttl=10) # TTL bajo para que los cambios del admin se vean rápido
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
    res_sim = [(0,0), (1,0), (0,1), (1,1), (2,1), (1,2), (2,2), (2,0), (0,2)]
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
        if c1.button("Entrar", use_container_width=True):
            df_u = leer_datos("Usuarios")
            user = df_u[(df_u['Usuario'].astype(str) == u_in) & (df_u['Password'].astype(str) == p_in)]
            if not user.empty:
                st.session_state.autenticado, st.session_state.user, st.session_state.rol = True, u_in, user.iloc[0]['Rol']; st.rerun()
            else: st.error("❌ Credenciales incorrectas")
        if c2.button("Registrarse", use_container_width=True):
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
        .match-box-locked { background: #e9ecef !important; opacity: 0.8; border-left: 5px solid #6c757d !important; filter: grayscale(0.5); }
        .lock-icon { font-size: 1.2em; cursor: help; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚽ Menú Liga")
        
        # --- MEJORA: SALTO AUTOMÁTICO DE JORNADA ---
        lista_jornadas = list(JORNADAS.keys())
        indice_defecto = 0
        for i, nombre_j in enumerate(lista_jornadas):
            pendientes = df_r_all[(df_r_all['Jornada'] == nombre_j) & (df_r_all['Finalizado'] == "NO")]
            if not pendientes.empty:
                indice_defecto = i
                break
        
        j_global = st.selectbox("📅 Seleccionar Jornada:", lista_jornadas, index=indice_defecto, key="side_j")
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False; st.rerun()

    # --- CÁLCULO DE DASHBOARD HERO ---
    stats_hero = []
    for u in u_jugadores:
        pb_row = df_base[df_base['Usuario'] == u]
        p_base = safe_float(pb_row['Puntos'].values[0]) if not pb_row.empty else 0.0
        u_p_hist = df_p_all[df_p_all['Usuario'] == u]
        p_acum = p_base
        for r in u_p_hist.itertuples():
            m = df_r_all[(df_r_all['Jornada'] == r.Jornada) & (df_r_all['Partido'] == r.Partido) & (df_r_all['Finalizado'] == "SI")]
            if not m.empty:
                p_acum += calcular_puntos(r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'])
        stats_hero.append({"Usuario": u, "Puntos": p_acum})
    
    df_hero = pd.DataFrame(stats_hero).sort_values("Puntos", ascending=False).reset_index(drop=True)
    df_hero['Posicion'] = range(1, len(df_hero) + 1)
    lider = df_hero.iloc[0] if not df_hero.empty else {"Usuario": "Nadie", "Puntos": 0.0}

    es_admin = st.session_state.rol == "admin"
    if es_admin:
        mi_pos = "ADMIN"
        mi_puntos_hoy = 0.00
    else:
        mi_pos_query = df_hero[df_hero['Usuario'] == st.session_state.user]['Posicion']
        mi_pos = f"#{int(mi_pos_query.values[0])}" if not mi_pos_query.empty else "-"
        u_p_hoy = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)]
        mi_puntos_hoy = 0.0
        for r in u_p_hoy.itertuples():
            m = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Partido'] == r.Partido) & (df_r_all['Finalizado'] == "SI")]
            if not m.empty:
                mi_puntos_hoy += calcular_puntos(r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'])

    prox_p = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "NO")].sort_values("Hora_Inicio").head(1)

    st.title(f"Hola, {st.session_state.user} 👋")

    # --- RENDER DASHBOARD HERO ---
    with st.container():
        st.markdown('<div class="hero-bg">', unsafe_allow_html=True)
        col_lider, col_sep, col_datos = st.columns([1.5, 0.2, 3.5])
        with col_lider:
            st.markdown('<span class="section-tag">LÍDER ACTUAL</span>', unsafe_allow_html=True)
            st.markdown('<div style="position: relative; text-align: center;"><span class="crown">👑</span>', unsafe_allow_html=True)
            f_l = foto_dict.get(lider['Usuario'])
            if f_l and os.path.exists(str(f_l)): st.image(f_l, width=90)
            else: st.markdown("<h2 style='margin:0;'>👤</h2>", unsafe_allow_html=True)
            st.markdown(f"**{lider['Usuario']}**<br><span style='color:#daa520; font-weight:bold;'>{lider['Puntos']:.2f} Pts</span></div>", unsafe_allow_html=True)
        with col_datos:
            st.markdown(f'<span class="section-tag">{"PANEL CONTROL" if es_admin else "TUS ESTADÍSTICAS"}</span>', unsafe_allow_html=True)
            c2, c3, c4 = st.columns(3)
            with c2: st.markdown(f'<div class="kpi-box"><span class="kpi-label">Tu Puesto</span><span class="kpi-value">{mi_pos}</span></div>', unsafe_allow_html=True)
            with c3:
                if not prox_p.empty:
                    # Calculamos la diferencia total
                    diff = datetime.strptime(str(prox_p.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S") - datetime.now()
                    ts = int(diff.total_seconds())
                    
                    if ts > 0:
                        # Desglose de tiempo
                        dias = ts // 86400
                        horas = (ts % 86400) // 3600
                        minutos = (ts % 3600) // 60
                        segundos = ts % 60
                        
                        # Lógica de colores dinámica
                        # Rojo: < 2h | Naranja: < 24h | Verde: > 24h
                        color = "#ff4b4b" if ts < 7200 else ("#ffa500" if ts < 86400 else "#2baf2b")
                        
                        # Formato de texto
                        t_str = f"{horas:02d}h {minutos:02d}m {segundos:02d}s"
                        if dias > 0: t_str = f"{dias}d {horas:02d}h" # Si faltan días, priorizamos días/horas
                        
                        st.markdown(f'''
                            <div class="kpi-box">
                                <span class="kpi-label">Cierre en</span>
                                <span class="kpi-value" style="color:{color}; font-size: 1.3em;">{t_str}</span>
                            </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="kpi-box"><span class="kpi-label">Mercado</span><span class="kpi-value" style="color:#6c757d;">Cerrado</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="kpi-box"><span class="kpi-label">Jornada</span><span class="kpi-value">Cerrada</span></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="kpi-box"><span class="kpi-label">Puntos Hoy</span><span class="kpi-value" style="color:#007bff;">{mi_puntos_hoy:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    usa_oraculo = 1 <= len(df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "NO")]) <= 3
    tabs = st.tabs(["✍️ Apuestas", "👀 Otros", "📊 Clasificación", "📈 Stats PRO", "🏆 Detalles", "🔮 Simulador", "🎲 Oráculo", "⚙️ Admin"])

    with tabs[0]: # --- PESTAÑA APUESTAS ---
        if es_admin:
            st.warning("🛡️ Acceso restringido: Los administradores no participan en las porras.")
            st.info("Tu función es supervisar la liga y actualizar los resultados desde la pestaña **⚙️ Admin**.")
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnh6Znd6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/fNuXfHoZY3nqE/giphy.gif", width=400)
        else:
            u_preds = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)]
            env = []
            for i, (loc, vis) in enumerate(JORNADAS[j_global]):
                m_id = f"{loc}-{vis}"
                
                # 1. Lógica de bloqueo
                dl, dv, dp = 0, 0, "NO"
                if not u_preds.empty:
                    match_data = u_preds[u_preds['Partido'] == m_id]
                    if not match_data.empty:
                        dl, dv, dp = int(match_data.iloc[0]['P_L']), int(match_data.iloc[0]['P_V']), match_data.iloc[0]['Publica']
                
                res_info = df_r_all[(df_r_all['Jornada']==j_global) & (df_r_all['Partido']==m_id)]
                lock = False
                msg_lock = "" # Tooltip
                if not res_info.empty:
                    lock = datetime.now() > datetime.strptime(str(res_info.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                    if lock:
                        msg_lock = f"Bloqueado: Comenzó el {res_info.iloc[0]['Hora_Inicio']}"
    
                # 2. Aplicar clase CSS dinámica
                card_class = "match-box-locked" if lock else "match-box"
                st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                
                c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 0.5, 2, 1, 2])
                
                with c1: 
                    log = get_logo(loc)
                    if log: st.image(log, width=45)
                
                # 3. Añadir Tooltip (help) e icono 🔒
                with c2: 
                    label_l = f"{loc} 🔒" if lock else loc
                    pl = st.number_input(label_l, 0, 9, dl, key=f"pl_{i}_{j_global}", disabled=lock, help=msg_lock)
                
                with c4: 
                    label_v = f"{vis} 🔒" if lock else vis
                    pv = st.number_input(label_v, 0, 9, dv, key=f"pv_{i}_{j_global}", disabled=lock, help=msg_lock)
                
                with c5: 
                    logv = get_logo(vis)
                    if logv: st.image(logv, width=45)
                
                with c6: 
                    pub = st.checkbox("Pública", dp=="SI", key=f"pb_{i}_{j_global}", disabled=lock)
                
                st.markdown('</div>', unsafe_allow_html=True)
                env.append({"Usuario": st.session_state.user, "Jornada": j_global, "Partido": m_id, "P_L": pl, "P_V": pv, "Publica": "SI" if pub else "NO"})
            
            if st.button("💾 Guardar Mis Predicciones", use_container_width=True):
                otras = df_p_all[~((df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global))]
                conn.update(worksheet="Predicciones", data=pd.concat([otras, pd.DataFrame(env)], ignore_index=True))
                st.cache_data.clear()
                st.success("✅ Predicciones guardadas con éxito.")
                st.rerun()

    with tabs[1]: # --- PESTAÑA OTROS (REVELAR AL FINALIZAR) ---
        st.header("👀 Qué han puesto los demás")
        
        # Obtenemos los partidos de esta jornada que ya están finalizados
        partidos_fin = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "SI")]
        
        # 1. SECCIÓN DE PARTIDOS FINALIZADOS (REVELACIÓN TOTAL)
        if not partidos_fin.empty:
            st.markdown("### ✅ Resultados y Apuestas Reveladas")
            st.caption("Al finalizar el partido, las apuestas de todos los jugadores se hacen visibles.")
            
            for _, match in partidos_fin.iterrows():
                m_id = match['Partido']
                res_real = f"{int(match['R_L'])}-{int(match['R_V'])}"
                tipo_p = match['Tipo']
                
                with st.expander(f"📊 {m_id}  —  Resultado Real: {res_real} ({tipo_p})"):
                    # Buscamos todas las predicciones para este partido específico
                    preds_match = df_p_all[(df_p_all['Jornada'] == j_global) & (df_p_all['Partido'] == m_id)]
                    
                    if not preds_match.empty:
                        resumen_partido = []
                        for _, p in preds_match.iterrows():
                            # Calculamos puntos de cada uno para mostrar en la tabla
                            pts = calcular_puntos(p['P_L'], p['P_V'], match['R_L'], match['R_V'], tipo_p)
                            resumen_partido.append({
                                "Jugador": p['Usuario'],
                                "Apostó": f"{int(p['P_L'])}-{int(p['P_V'])}",
                                "Puntos": pts
                            })
                        
                        # Creamos un DataFrame y lo ordenamos por puntos (quien más ganó, arriba)
                        df_resumen = pd.DataFrame(resumen_partido).sort_values("Puntos", ascending=False)
                        st.table(df_resumen)
                    else:
                        st.write("Nadie hizo predicciones para este partido.")
            st.divider()

        # 2. SECCIÓN DE PARTIDOS NO FINALIZADOS (SOLO PÚBLICAS)
        st.markdown("### 🔒 Próximos Partidos / En Juego")
        st.caption("Solo puedes ver las apuestas de quienes las han marcado como 'Públicas'.")
        
        # Filtramos predicciones públicas de otros usuarios
        p_pub = df_p_all[(df_p_all['Jornada'] == j_global) & (df_p_all['Publica'] == "SI") & (df_p_all['Usuario'] != st.session_state.user)]
        
        # Quitamos de aquí las que ya se muestran arriba por estar finalizadas
        if not partidos_fin.empty:
            p_pub = p_pub[~p_pub['Partido'].isin(partidos_fin['Partido'])]

        if p_pub.empty:
            st.info("No hay apuestas públicas visibles para los partidos restantes.")
        else:
            usuarios_pub = p_pub['Usuario'].unique()
            for u in usuarios_pub:
                with st.expander(f"👤 Apuestas de {u}"):
                    # Mostramos solo los partidos que aún no han sido revelados arriba
                    df_u_pub = p_pub[p_pub['Usuario'] == u][['Partido', 'P_L', 'P_V']]
                    st.table(df_u_pub)

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
            c1, c2, c3 = st.columns(3); c1.metric("⭐ Amuleto", adn['amuleto']); c2.metric("💀 Bestia", adn['bestia']); c3.metric("🎯 %", f"{(adn['signos']+adn['exactos'])/(adn['exactos']+adn['signos']+adn['fallos']+0.001)*100:.1f}%")
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
            st.dataframe(m_p.astype(float), use_container_width=True)
        else: st.info("Sin partidos finalizados.")

    with tabs[5]: # SIMULADOR
        usr_sim = st.selectbox("Simular LaLiga según apuestas de:", u_jugadores)
        if st.button("Generar Clasificación Simulada"):
            sim = {k: v.copy() for k, v in STATS_LALIGA_BASE.items()}
            for p in df_p_all[df_p_all['Usuario']==usr_sim].itertuples():
                try:
                    tl, tv = p.Partido.split('-')
                    if tl in sim and tv in sim:
                        sim[tl]["PJ"]+=1; sim[tv]["PJ"]+=1
                        if p.P_L > p.P_V: sim[tl]["Pts"]+=3; sim[tl]["V"]+=1; sim[tv]["D"]+=1
                        elif p.P_V > p.P_L: sim[tv]["Pts"]+=3; sim[tv]["V"]+=1; sim[tl]["D"]+=1
                        else: sim[tl]["Pts"]+=1; sim[tv]["Pts"]+=1; sim[tl]["E"]+=1; sim[tv]["E"]+=1
                except: continue
            st.dataframe(pd.DataFrame.from_dict(sim, orient='index').sort_values("Pts", ascending=False), use_container_width=True)

    with tabs[6]: # ORÁCULO
        if usa_oraculo:
            prob = simular_oraculo(u_jugadores, df_p_all, df_r_all, j_global)
            if prob:
                if any(v >= 90 for v in prob.values()):
                    st.balloons()
                    st.success("¡Tenemos un virtual ganador de la jornada! 🏆")
                st.subheader("🔮 Probabilidades de Victoria en la Jornada")
                
                # Gráfico de Evolución
                df_hist = leer_datos("HistoricoOraculo")
                df_hist = df_hist[df_hist['Jornada'] == j_global]
                
                if not df_hist.empty:
                    fig_evo = px.line(
                        df_hist, x="Fecha", y="Probabilidad", color="Usuario",
                        title="Evolución en Tiempo Real",
                        markers=True, line_shape="spline",
                        color_discrete_sequence=px.colors.qualitative.Prism
                    )
                    fig_evo.update_layout(yaxis_range=[0, 100], hovermode="x unified")
                    st.plotly_chart(fig_evo, use_container_width=True)
                
                # Barras actuales con Delta
                st.markdown("---")
                for u, v in sorted(prob.items(), key=lambda x: x[1], reverse=True):
                    if v > 0:
                        # Buscamos la prob anterior para el "pique"
                        u_hist = df_hist[df_hist['Usuario'] == u]
                        delta = None
                        if len(u_hist) > 1:
                            delta = v - u_hist.iloc[-2]['Probabilidad']
                        
                        col_n, col_b = st.columns([1, 4])
                        col_n.markdown(f"**{u}**")
                        col_b.progress(v/100)
                        st.write(f"Probabilidad actual: **{v:.1f}%**" + (f" ({delta:+.1f}%)" if delta else ""))
        else: 
            st.info("El Oráculo se activa cuando quedan 1-3 partidos.")

    with tabs[7]: # --- PESTAÑA ADMIN COMPLETA ---
        if st.session_state.rol == "admin":
            st.header("⚙️ Panel de Control de Administrador")
            
            # Sub-pestañas para organizar el trabajo
            t_bases, t_fotos, t_resultados = st.tabs(["⭐ Puntos Base", "📸 Fotos de Perfil", "⚽ Resultados y Horarios"])

            with t_bases:
                st.subheader("Configurar Puntos Iniciales")
                st.info("Usa esto para dar ventaja a nuevos jugadores o corregir errores manuales.")
                upd_b = []
                for u in u_jugadores:
                    # Buscamos puntos actuales en el dataframe de base
                    pb_row = df_base[df_base['Usuario'] == u]
                    pts_actuales = safe_float(pb_row['Puntos'].values[0]) if not pb_row.empty else 0.0
                    
                    col_u, col_p = st.columns([2, 1])
                    col_u.markdown(f"**{u}**")
                    nuevo_val = col_p.number_input(f"Pts base {u}", value=pts_actuales, step=0.5, key=f"adm_b_{u}", label_visibility="collapsed")
                    upd_b.append({"Usuario": u, "Puntos": nuevo_val})
                
                if st.button("💾 Guardar Todos los Puntos Base", use_container_width=True):
                    conn.update(worksheet="PuntosBase", data=pd.DataFrame(upd_b))
                    st.cache_data.clear()
                    st.success("✅ Puntos base actualizados. El ranking general ha cambiado.")
                    st.rerun()

            with t_fotos:
                st.subheader("Asignar Imágenes a Usuarios")
                if os.path.exists(PERFILES_DIR):
                    archivos = ["Ninguna"] + sorted([f for f in os.listdir(PERFILES_DIR) if f.endswith(('.jpeg', '.jpg', '.png', '.webp'))])
                    upd_f = []
                    for u in u_jugadores:
                        # Limpieza de datos para evitar el error de basename
                        path_en_db = foto_dict.get(u, "")
                        if pd.isna(path_en_db) or not isinstance(path_en_db, str):
                            path_en_db = ""
                        
                        nombre_foto_actual = os.path.basename(path_en_db) if path_en_db != "" else "Ninguna"
                        
                        col_u2, col_f = st.columns([2, 1])
                        col_u2.write(f"Usuario: **{u}**")
                        # Si la foto que está en el Excel no existe en la carpeta, ponemos "Ninguna" por defecto
                        idx_foto = archivos.index(nombre_foto_actual) if nombre_foto_actual in archivos else 0
                        
                        foto_sel = col_f.selectbox(f"Foto {u}", archivos, index=idx_foto, key=f"adm_f_{u}", label_visibility="collapsed")
                        
                        path_final = f"{PERFILES_DIR}{foto_sel}" if foto_sel != "Ninguna" else ""
                        upd_f.append({"Usuario": u, "ImagenPath": path_final})
                    
                    if st.button("🖼️ Actualizar Todas las Fotos", use_container_width=True):
                        conn.update(worksheet="ImagenesPerfil", data=pd.DataFrame(upd_f))
                        st.cache_data.clear()
                        st.success("✅ Fotos actualizadas correctamente.")
                        st.rerun()
                else:
                    st.error(f"⚠️ La carpeta '{PERFILES_DIR}' no existe.")

            with t_resultados:
                st.subheader(f"Gestión de la {j_global}")
                st.write("Configura el tipo de partido, la fecha/hora de bloqueo y los resultados.")
                
                r_env = []
                h_ops = [time(h, m).strftime("%H:%M") for h in range(12, 23) for m in [0, 15, 30, 45]]
                
                for i, (loc, vis) in enumerate(JORNADAS[j_global]):
                    m_id = f"{loc}-{vis}"
                    prev = df_r_all[(df_r_all['Jornada']==j_global) & (df_r_all['Partido']==m_id)]
                    
                    # Valores por defecto (si el partido es nuevo)
                    rl, rv, fin, t = 0, 0, False, "Normal"
                    fecha_v = datetime(2026, 2, 23).date()
                    hora_v = "21:00"

                    if not prev.empty: 
                        rl, rv, fin = int(prev.iloc[0]['R_L']), int(prev.iloc[0]['R_V']), prev.iloc[0]['Finalizado']=="SI"
                        t = prev.iloc[0]['Tipo']
                        try:
                            dt_obj = datetime.strptime(str(prev.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                            fecha_v = dt_obj.date()
                            hora_v = dt_obj.strftime("%H:%M")
                        except: pass

                    st.markdown(f"---")
                    st.markdown(f"**⚽ {m_id}**")
                    c1, c2, c3, c4, c5, c6 = st.columns([1.2, 1.2, 1, 0.7, 0.7, 0.6])
                    
                    nt = c1.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], index=["Normal", "Doble", "Esquizo"].index(t), key=f"at_{i}")
                    nf = c2.date_input("Día", value=fecha_v, key=f"adate_{i}")
                    nh = c3.selectbox("Hora", h_ops, index=h_ops.index(hora_v) if hora_v in h_ops else 0, key=f"aho_{i}")
                    nrl = c4.number_input("L", 0, 9, rl, key=f"arl_{i}")
                    nrv = c5.number_input("V", 0, 9, rv, key=f"arv_{i}")
                    nfi = c6.checkbox("Fin", fin, key=f"afi_{i}")
                    
                    r_env.append({
                        "Jornada": j_global, "Partido": m_id, "Tipo": nt, 
                        "R_L": nrl, "R_V": nrv, "Hora_Inicio": f"{nf} {nh}:00", 
                        "Finalizado": "SI" if nfi else "NO"
                    })
                
                st.divider()
                if st.button("🏟️ GUARDAR RESULTADOS JORNADA", use_container_width=True):
                    # Mantener los resultados de las otras jornadas
                    otros = df_r_all[df_r_all['Jornada'] != j_global]
                    conn.update(worksheet="Resultados", data=pd.concat([otros, pd.DataFrame(r_env)], ignore_index=True))
                    st.cache_data.clear()
                    st.success(f"✅ Datos de la {j_global} guardados.")
                    if usa_oraculo:
                        # Calculamos las probabilidades actuales
                        probs_ahora = simular_oraculo(u_jugadores, df_p_all, pd.concat([otros, pd.DataFrame(r_env)]), j_global)
                        if probs_ahora:
                            # Preparamos los datos para el histórico
                            ahora_str = datetime.now().strftime("%H:%M:%S")
                            df_hist_nuevo = pd.DataFrame([
                                {"Jornada": j_global, "Fecha": ahora_str, "Usuario": u, "Probabilidad": round(p, 1)}
                                for u, p in probs_ahora.items() if p > 0
                            ])
                            # Leemos el histórico actual y concatenamos
                            df_h_existente = leer_datos("HistoricoOraculo")
                            df_h_final = pd.concat([df_h_existente, df_hist_nuevo], ignore_index=True)
                            conn.update(worksheet="HistoricoOraculo", data=df_h_final)
                    st.rerun()
        else:
            # Mensaje por si alguien intenta cotillear sin ser admin
            st.warning("⛔ Acceso restringido.")
            st.error(f"Tu usuario (**{st.session_state.user}**) no tiene permisos de administrador.")
            st.info("Si deberías ser admin, pide que cambien tu rol en la base de datos a 'admin'.")







