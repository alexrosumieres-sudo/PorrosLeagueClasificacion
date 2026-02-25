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
    # 1. CARGA DE DATOS CENTRALIZADA
    df_perf = leer_datos("ImagenesPerfil")
    df_r_all = leer_datos("Resultados")
    df_p_all = leer_datos("Predicciones")
    df_u_all = leer_datos("Usuarios")
    df_base = leer_datos("PuntosBase")
    df_logs_all = leer_datos("LogsAdmin") # Cargamos los logs para la Auditoría
    
    foto_dict = df_perf.set_index('Usuario')['ImagenPath'].to_dict() if not df_perf.empty else {}
    u_jugadores = [u for u in df_u_all['Usuario'].unique() if u not in df_u_all[df_u_all['Rol']=='admin']['Usuario'].tolist()]

    # --- CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; color: #31333F; }
        .hero-bg { background: #f8f9fa; border-radius: 20px; padding: 25px; margin-bottom: 25px; border: 1px solid #dee2e6; }
        .kpi-box { background: white; border-radius: 12px; padding: 12px; text-align: center; border: 1px solid #eee; }
        .kpi-label { font-size: 0.75em; color: #6c757d; font-weight: bold; text-transform: uppercase; }
        .kpi-value { font-size: 1.6em; font-weight: 800; color: #2baf2b; display: block; }
        .panini-card { background: #f8f9fb; border-radius: 15px; padding: 20px; border: 1px solid #e0e0e0; margin-bottom: 20px; }
        .quote-text { color: #4f4f4f; font-style: italic; border-left: 3px solid #2baf2b; padding-left: 10px; margin: 10px 0; }
        .pos-badge { background-color: #2baf2b; color: white; padding: 5px 15px; border-radius: 50%; font-weight: bold; }
        .match-box { background: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #eee; border-left: 5px solid #2baf2b; margin-bottom: 10px; }
        .crown { font-size: 2em; position: absolute; top: -35px; left: 35px; transform: rotate(-15deg); }
        .section-tag { font-size: 0.7em; background: #31333F; color: white; padding: 2px 8px; border-radius: 5px; margin-bottom: 5px; display: inline-block; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚽ Menú Liga")
        lista_jornadas_keys = list(JORNADAS.keys())
        idx_defecto = 0
        for i, nombre_j in enumerate(lista_jornadas_keys):
            pendientes = df_r_all[(df_r_all['Jornada'] == nombre_j) & (df_r_all['Finalizado'] == "NO")]
            if not pendientes.empty:
                idx_defecto = i
                break
        j_global = st.selectbox("📅 Seleccionar Jornada:", lista_jornadas_keys, index=idx_defecto, key="side_j")
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    # --- CÁLCULO DE POSICIONES ACTUALES ---
    stats_h = []
    for u in u_jugadores:
        pb = df_base[df_base['Usuario'] == u]
        pts = safe_float(pb['Puntos'].values[0]) if not pb.empty else 0.0
        u_p_hist = df_p_all[df_p_all['Usuario'] == u]
        for r in u_p_hist.itertuples():
            m = df_r_all[(df_r_all['Jornada']==r.Jornada)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
            if not m.empty: pts += calcular_puntos(r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'])
        stats_h.append({"Usuario": u, "Puntos": pts})
    
    df_h = pd.DataFrame(stats_h).sort_values("Puntos", ascending=False).reset_index(drop=True)
    df_h['Posicion'] = range(1, len(df_h) + 1)
    lider = df_h.iloc[0] if not df_h.empty else {"Usuario": "-", "Puntos": 0.0}

    es_admin = st.session_state.rol == "admin"
    if es_admin:
        mi_pos = "ADMIN"
        ph_val = 0.0
    else:
        q_p = df_h[df_h['Usuario'] == st.session_state.user]['Posicion']
        mi_pos = f"#{int(q_p.values[0])}" if not q_p.empty else "-"
        ph_val = 0.0
        u_p_hoy = df_p_all[(df_p_all['Usuario']==st.session_state.user)&(df_p_all['Jornada']==j_global)]
        for r in u_p_hoy.itertuples():
            m = df_r_all[(df_r_all['Jornada']==j_global)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
            if not m.empty: ph_val += calcular_puntos(r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'])

    # --- LÓGICA DE EVOLUCIÓN (HISTÓRICO) ---
    j_terminadas = [jn for jn in lista_jornadas_keys if not df_r_all[(df_r_all['Jornada'] == jn) & (df_r_all['Finalizado'] == "SI")].empty]
    evol_list = []
    for jt in j_terminadas:
        hist_rank = []
        for u in u_jugadores:
            pb = df_base[df_base['Usuario'] == u]
            p_c = safe_float(pb['Puntos'].values[0]) if not pb.empty else 0.0
            p_hist = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] <= jt)]
            for r in p_hist.itertuples():
                m = df_r_all[(df_r_all['Jornada']==r.Jornada)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
                if not m.empty: p_c += calcular_puntos(r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'])
            hist_rank.append({"Usuario": u, "Puntos": p_c})
        df_t = pd.DataFrame(hist_rank).sort_values("Puntos", ascending=False).reset_index(drop=True)
        df_t['Puesto'] = range(1, len(df_t) + 1)
        for _, row in df_t.iterrows():
            evol_list.append({"Jornada": jt, "Usuario": row['Usuario'], "Puesto": row['Puesto']})
    df_evolucion_final = pd.DataFrame(evol_list)

    # --- RENDER HERO ---
    st.title(f"Hola, {st.session_state.user} 👋")
    with st.container():
        st.markdown('<div class="hero-bg">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1.5, 0.2, 3.5])
        with c1:
            st.markdown('<span class="section-tag">LÍDER ACTUAL</span>', unsafe_allow_html=True)
            st.markdown(f'<div style="position: relative; text-align: center;"><span class="crown">👑</span>', unsafe_allow_html=True)
            f_l = foto_dict.get(lider['Usuario'], "")
            if f_l and os.path.exists(str(f_l)): st.image(f_l, width=80)
            else: st.markdown("<h2>👤</h2>", unsafe_allow_html=True)
            st.markdown(f"**{lider['Usuario']}**<br>{lider['Puntos']:.2f} Pts</div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f'<span class="section-tag">{"INFO ADMIN" if es_admin else "MIS DATOS"}</span>', unsafe_allow_html=True)
            ca, cb, cc = st.columns(3)
            with ca: st.markdown(f'<div class="kpi-box"><span class="kpi-label">Puesto</span><span class="kpi-value">{mi_pos}</span></div>', unsafe_allow_html=True)
            with cb:
                px_p = df_r_all[(df_r_all['Jornada']==j_global)&(df_r_all['Finalizado']=="NO")].sort_values("Hora_Inicio").head(1)
                if not px_p.empty:
                    diff = datetime.strptime(str(px_p.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S") - datetime.now()
                    hrs = max(0, int(diff.total_seconds() // 3600))
                    st.markdown(f'<div class="kpi-box"><span class="kpi-label">Cierre en</span><span class="kpi-value" style="color:{"#ff4b4b" if hrs<24 else "#2baf2b"}">{hrs}h</span></div>', unsafe_allow_html=True)
                else: st.markdown('<div class="kpi-box"><span class="kpi-label">Estado</span><span class="kpi-value">Cerrada</span></div>', unsafe_allow_html=True)
            with cc:
                st.markdown(f'<div class="kpi-box"><span class="kpi-label">Pts Hoy</span><span class="kpi-value" style="color:#007bff;">{ph_val:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- DEFINICIÓN DE PESTAÑAS ---
    tabs = st.tabs(["✍️ Apuestas", "👀 Otros", "📊 Clasificación", "📈 Evolución", "📊 Stats PRO", "🏆 Detalles", "🔮 Simulador", "🎲 Oráculo", "📜 Auditoría", "⚙️ Admin"])

    with tabs[0]: # APUESTAS
        if es_admin:
            st.warning("🛡️ El administrador no puede poner apuestas.")
        else:
            u_preds = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)]
            env = []
            for i, (loc, vis) in enumerate(JORNADAS[j_global]):
                m_id = f"{loc}-{vis}"
                dl, dv, dp = 0, 0, "NO"
                if not u_preds.empty:
                    rd = u_preds[u_preds['Partido'] == m_id]
                    if not rd.empty: dl, dv, dp = int(rd.iloc[0]['P_L']), int(rd.iloc[0]['P_V']), rd.iloc[0]['Publica']
                
                ri = df_r_all[(df_r_all['Jornada']==j_global) & (df_r_all['Partido']==m_id)]
                lock = False
                if not ri.empty:
                    lock = datetime.now() > datetime.strptime(str(ri.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                
                st.markdown(f'<div class="match-box">', unsafe_allow_html=True)
                ca, cb, cc, cd, ce, cf = st.columns([1, 2, 0.5, 2, 1, 2])
                with ca: 
                    lgl = get_logo(loc)
                    if lgl: st.image(lgl, width=45)
                    else: st.write("⚽")
                with cb: pl = st.number_input(f"{loc}", 0, 9, dl, key=f"pl_{i}", disabled=lock)
                with cd: pv = st.number_input(f"{vis}", 0, 9, dv, key=f"pv_{i}", disabled=lock)
                with ce: 
                    lgv = get_logo(vis)
                    if lgv: st.image(lgv, width=45)
                    else: st.write("⚽")
                with cf: pub = st.checkbox("Pública", dp=="SI", key=f"pb_{i}", disabled=lock)
                st.markdown('</div>', unsafe_allow_html=True)
                env.append({"Usuario": st.session_state.user, "Jornada": j_global, "Partido": m_id, "P_L": pl, "P_V": pv, "Publica": "SI" if pub else "NO"})
            if st.button("💾 Guardar Mis Predicciones", use_container_width=True):
                old = df_p_all[~((df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global))]
                conn.update(worksheet="Predicciones", data=pd.concat([old, pd.DataFrame(env)], ignore_index=True))
                st.cache_data.clear(); st.success("✅ Guardado."); st.rerun()

    with tabs[1]: # OTROS (REVELAR)
        p_fin = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "SI")]
        if not p_fin.empty:
            st.subheader("✅ Apuestas Reveladas (Finalizados)")
            for _, m in p_fin.iterrows():
                with st.expander(f"📊 {m['Partido']} (Real: {int(m['R_L'])}-{int(m['R_V'])})"):
                    df_res = df_p_all[(df_p_all['Jornada']==j_global)&(df_p_all['Partido']==m['Partido'])].copy()
                    if not df_res.empty:
                        df_res['Pts'] = df_res.apply(lambda x: calcular_puntos(x.P_L, x.P_V, m.R_L, m.R_V, m.Tipo), axis=1)
                        st.table(df_res[['Usuario', 'P_L', 'P_V', 'Pts']].sort_values("Pts", ascending=False))
        st.subheader("🔒 Próximos Partidos (Solo Públicas)")
        p_pub = df_p_all[(df_p_all['Jornada'] == j_global) & (df_p_all['Publica'] == "SI") & (df_p_all['Usuario'] != st.session_state.user)]
        if not p_fin.empty: p_pub = p_pub[~p_pub['Partido'].isin(p_fin['Partido'])]
        if p_pub.empty: st.info("Nada que mostrar.")
        else:
            for u in p_pub['Usuario'].unique():
                with st.expander(f"👤 {u}"): st.table(p_pub[p_pub['Usuario']==u][['Partido', 'P_L', 'P_V']])

    with tabs[2]: # CLASIFICACIÓN
        for _, r in df_h.iterrows():
            st.markdown(f'<div class="panini-card">', unsafe_allow_html=True)
            ca, cb, cc, cd = st.columns([0.6, 1.2, 3.5, 1.5])
            with ca: st.markdown(f'<br><span class="pos-badge">#{r["Posicion"]}</span>', unsafe_allow_html=True)
            with cb:
                im = foto_dict.get(r['Usuario'], "")
                if im and os.path.exists(str(im)): st.image(im, width=80)
                else: st.markdown("### 👤")
            with cc:
                fr = random.choice(FRASES_POR_PUESTO.get(r["Posicion"] if r["Posicion"]<=7 else 7))
                st.markdown(f"### {r['Usuario']}"); st.markdown(f'<div class="quote-text">"{fr[0]}"<br><small>— {fr[1]}</small></div>', unsafe_allow_html=True)
            with cd: st.markdown(f'<br><span style="font-size: 2em; font-weight: bold; color: #2baf2b;">{r["Puntos"]:.2f}</span><br>Pts', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tabs[3]: # EVOLUCIÓN
        st.header("📈 Evolución del Ranking")
        if not df_evolucion_final.empty:
            fig_ev = px.line(df_evolucion_final, x="Jornada", y="Puesto", color="Usuario", markers=True, category_orders={"Jornada": lista_jornadas_keys})
            fig_ev.update_yaxes(autorange="reversed", tickmode="linear", tick0=1, dtick=1)
            st.plotly_chart(fig_ev, use_container_width=True)
        else: st.info("Aún no hay jornadas finalizadas para mostrar evolución.")

    with tabs[4]: # STATS PRO
        us = st.selectbox("Analizar Jugador:", u_jugadores)
        adn = analizar_adn_pro(us, df_p_all, df_r_all)
        if adn:
            st.metric("🎯 % Acierto", f"{(adn['exactos']+adn['signos'])/(adn['exactos']+adn['signos']+adn['fallos']+0.001)*100:.1f}%")
            st.plotly_chart(px.pie(values=[adn['exactos'], adn['signos'], adn['fallos']], names=['Plenos', 'Signos', 'Fallos'], color_discrete_sequence=['#2baf2b', '#ffd700', '#ff4b4b']), use_container_width=True)

    with tabs[5]: # DETALLES
        df_det = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "SI")]
        if not df_det.empty:
            mat = pd.DataFrame(index=df_det['Partido'].unique(), columns=u_jugadores)
            for p in mat.index:
                inf = df_det[df_det['Partido'] == p].iloc[0]
                for u in u_jugadores:
                    up = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == j_global) & (df_p_all['Partido'] == p)]
                    mat.at[p, u] = calcular_puntos(up.iloc[0]['P_L'], up.iloc[0]['P_V'], inf['R_L'], inf['R_V'], inf['Tipo']) if not up.empty else 0.0
            st.dataframe(mat.astype(float), use_container_width=True)
        else: st.info("Sin partidos finalizados.")

    with tabs[6]: # SIMULADOR
        usim = st.selectbox("Basar simulación en:", u_jugadores)
        if st.button("Simular Liga"):
            sim = {k: v.copy() for k, v in STATS_LALIGA_BASE.items()}
            for p in df_p_all[df_p_all['Usuario']==usim].itertuples():
                try:
                    tl, tv = p.Partido.split('-')
                    if tl in sim and tv in sim:
                        sim[tl]["PJ"]+=1; sim[tv]["PJ"]+=1
                        if p.P_L > p.P_V: sim[tl]["Pts"]+=3; sim[tl]["V"]+=1; sim[tv]["D"]+=1
                        elif p.P_V > p.P_L: sim[tv]["Pts"]+=3; sim[tv]["V"]+=1; sim[tl]["D"]+=1
                        else: sim[tl]["Pts"]+=1; sim[tv]["Pts"]+=1; sim[tl]["E"]+=1; sim[tv]["E"]+=1
                except: continue
            st.table(pd.DataFrame.from_dict(sim, orient='index').sort_values("Pts", ascending=False))

    with tabs[7]: # ORÁCULO
        if usa_oraculo:
            pr = simular_oraculo(u_jugadores, df_p_all, df_r_all, j_global)
            if pr:
                for u, v in sorted(pr.items(), key=lambda x: x[1], reverse=True):
                    if v > 0: st.write(f"**{u}**: {v:.1f}%"); st.progress(v/100)
        else: st.info("El Oráculo se activa con 1-3 partidos restantes.")

    with tabs[8]: # AUDITORÍA
        st.header("📜 Historial de Cambios (Admin)")
        if not df_logs_all.empty:
            st.table(df_logs_all.sort_values("Fecha", ascending=False).head(30))
        else: st.info("Sin actividad registrada.")

    with tabs[9]: # ADMIN
        if es_admin:
            t1, t2, t3 = st.tabs(["⭐ Bases", "📸 Fotos", "⚽ Resultados"])
            with t1:
                up_b = []
                for u in u_jugadores:
                    val = st.number_input(f"Base {u}", value=safe_float(df_base[df_base['Usuario']==u]['Puntos'].values[0]) if not df_base[df_base['Usuario']==u].empty else 0.0, key=f"b_{u}")
                    up_b.append({"Usuario": u, "Puntos": val})
                if st.button("Guardar Puntos Base"):
                    conn.update(worksheet="PuntosBase", data=pd.DataFrame(up_b))
                    st.cache_data.clear(); st.success("Bases actualizadas."); st.rerun()
            with t2:
                fs = ["Ninguna"] + sorted([f for f in os.listdir(PERFILES_DIR) if f.endswith(('.jpeg', '.jpg', '.png', '.webp'))])
                up_f = []
                for u in u_jugadores:
                    act = os.path.basename(foto_dict.get(u, "")) or "Ninguna"
                    sel = st.selectbox(f"Foto {u}", fs, index=fs.index(act) if act in fs else 0, key=f"f_{u}")
                    up_f.append({"Usuario": u, "ImagenPath": f"{PERFILES_DIR}{sel}" if sel != "Ninguna" else ""})
                if st.button("Guardar Fotos"):
                    conn.update(worksheet="ImagenesPerfil", data=pd.DataFrame(up_f))
                    st.cache_data.clear(); st.success("Fotos guardadas."); st.rerun()
            with t3:
                st.subheader(f"Gestión {j_global}")
                res_env, h_ops = [], [time(h, m).strftime("%H:%M") for h in range(12, 23) for m in [0, 15, 30, 45]]
                for i, (l_eq, v_eq) in enumerate(JORNADAS[j_global]):
                    m_id = f"{l_eq}-{v_eq}"
                    prev = df_r_all[(df_r_all['Jornada']==j_global) & (df_r_all['Partido']==m_id)]
                    rl, rv, fin, t, f_v, h_v = 0, 0, False, "Normal", datetime(2026,2,23).date(), "21:00"
                    if not prev.empty:
                        rl, rv, fin = int(prev.iloc[0]['R_L']), int(prev.iloc[0]['R_V']), prev.iloc[0]['Finalizado']=="SI"
                        t, dt = prev.iloc[0]['Tipo'], datetime.strptime(str(prev.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                        f_v, h_v = dt.date(), dt.strftime("%H:%M")
                    st.write(f"**⚽ {m_id}**")
                    ca, cb, cc, cd, ce, cf = st.columns([1, 1.2, 1, 0.7, 0.7, 0.6])
                    nt = ca.selectbox("T", ["Normal", "Doble", "Esquizo"], index=["Normal", "Doble", "Esquizo"].index(t), key=f"at_{i}")
                    nf, nh = cb.date_input("D", f_v, key=f"ad_{i}"), cc.selectbox("H", h_ops, index=h_ops.index(h_v), key=f"ah_{i}")
                    nrl, nrv, nfi = cd.number_input("L", 0, 9, rl, key=f"arl_{i}"), ce.number_input("V", 0, 9, rv, key=f"arv_{i}"), cf.checkbox("F", fin, key=f"afi_{i}")
                    res_env.append({"Jornada": j_global, "Partido": m_id, "Tipo": nt, "R_L": nrl, "R_V": nrv, "Hora_Inicio": f"{nf} {nh}:00", "Finalizado": "SI" if nfi else "NO"})
                if st.button("🏟️ Guardar Resultados"):
                    otros = df_r_all[df_r_all['Jornada'] != j_global]
                    conn.update(worksheet="Resultados", data=pd.concat([otros, pd.DataFrame(res_env)], ignore_index=True))
                    # --- REGISTRO AUDITORÍA ---
                    n_log = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "Usuario": st.session_state.user, "Accion": f"Actualizó {j_global}"}])
                    conn.update(worksheet="LogsAdmin", data=pd.concat([df_logs_all, n_log], ignore_index=True))
                    st.cache_data.clear(); st.success("OK y log registrado."); st.rerun()
        else:
            st.warning("⛔ No eres admin.")

