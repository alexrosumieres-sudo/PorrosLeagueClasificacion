import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time
import os
import plotly.express as px
import random
import itertools

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
}

LOGOS = {eq: f"{LOGOS_DIR}{eq.lower().replace(' ', '').replace('.', '')}.jpeg" for eq in STATS_LALIGA_BASE.keys()}
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
    if path and os.path.exists(path): return path
    return None

def calcular_puntos(p_l, p_v, r_l, r_v, tipo="Normal"):
    p_ganador, p_diff, p_exacto = SCORING.get(tipo, SCORING["Normal"])
    if p_l == r_l and p_v == r_v: return p_exacto
    signo_p = (p_l > p_v) - (p_l < p_v)
    signo_r = (r_l > r_v) - (r_l < r_v)
    if signo_p == signo_r:
        if (p_l - p_v) == (r_l - r_v): return p_diff
        return p_ganador
    return 0.0

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

def simular_oraculo(usuarios, df_p_all, df_r_all, jornada_sel):
    res_sim = [(0,0), (1,0), (0,1), (1,1), (2,1), (1,2), (2,0), (0,2), (2,2), (3,0), (0,3), (3,1), (1,3), (3,2), (2,3)]
    pendientes = df_r_all[(df_r_all['Jornada'] == jornada_sel) & (df_r_all['Finalizado'] == "NO")]
    if pendientes.empty or len(pendientes) > 3: return None
    
    p_id = pendientes['Partido'].tolist()
    t_id = pendientes['Tipo'].tolist()
    
    # Puntos jornada actuales
    pts_hoy = {u: 0.0 for u in usuarios}
    for u in usuarios:
        u_p = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == jornada_sel)]
        for r in u_p.itertuples():
            m_r = df_r_all[(df_r_all['Jornada']==jornada_sel) & (df_r_all['Partido']==r.Partido) & (df_r_all['Finalizado']=="SI")]
            if not m_r.empty:
                pts_hoy[u] += calcular_puntos(r.P_L, r.P_V, m_r.iloc[0]['R_L'], m_r.iloc[0]['R_V'], m_r.iloc[0]['Tipo'])

    victorias = {u: 0 for u in usuarios}
    combos = list(itertools.product(res_sim, repeat=len(p_id)))
    
    for c in combos:
        escenario = pts_hoy.copy()
        for i, res in enumerate(c):
            for u in usuarios:
                u_pred = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == jornada_sel) & (df_p_all['Partido'] == p_id[i])]
                if not u_pred.empty:
                    escenario[u] += calcular_puntos(u_pred.iloc[0]['P_L'], u_pred.iloc[0]['P_V'], res[0], res[1], t_id[i])
        max_p = max(escenario.values())
        ganadores = [u for u, p in escenario.items() if p == max_p]
        for g in ganadores: victorias[g] += 1 / len(ganadores)
    return {u: (v/len(combos))*100 for u, v in victorias.items()}

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
else:
    # CARGA DATOS
    df_perfiles = leer_datos("ImagenesPerfil")
    df_r_all = leer_datos("Resultados")
    df_p_all = leer_datos("Predicciones")
    df_u_all = leer_datos("Usuarios")
    df_base = leer_datos("PuntosBase")
    
    foto_dict = df_perfiles.set_index('Usuario')['ImagenPath'].to_dict() if not df_perfiles.empty else {}
    admins = df_u_all[df_u_all['Rol'] == 'admin']['Usuario'].tolist() if not df_u_all.empty else []
    u_jugadores = [u for u in df_u_all['Usuario'].unique() if u not in admins]

    j_global = st.selectbox("📅 Jornada:", list(JORNADAS.keys()))
    
    # Lógica Oráculo
    p_pend = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "NO")]
    usa_oraculo = 1 <= len(p_pend) <= 3
    
    tab_list = ["✍️ Apuestas", "👀 Otros", "📊 Clasificación", "📈 Stats PRO", "🔮 Simulador"]
    if usa_oraculo: tab_list.append("🎲 Escenarios")
    tab_list.append("⚙️ Admin")
    tabs = st.tabs(tab_list)

    # --- PESTAÑA: CLASIFICACIÓN ---
    with tabs[2]:
        tipo_r = st.radio("Ranking:", ["General", "Jornada"], horizontal=True)
        pts_list = []
        for u in u_jugadores:
            pb = safe_float(df_base[df_base['Usuario']==u].iloc[0]['Puntos']) if tipo_r == "General" else 0.0
            u_p = df_p_all[(df_p_all['Usuario']==u) & (df_p_all['Jornada']==j_global)] if tipo_r == "Jornada" else df_p_all[df_p_all['Usuario']==u]
            pts_acum = pb
            for r in u_p.itertuples():
                m_k = df_r_all[(df_r_all['Jornada']==r.Jornada)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
                if not m_k.empty: pts_acum += calcular_puntos(r.P_L, r.P_V, m_k.iloc[0]['R_L'], m_k.iloc[0]['R_V'], m_k.iloc[0]['Tipo'])
            pts_list.append({"Usuario": u, "Puntos": pts_acum})
        
        df_rank = pd.DataFrame(pts_list).sort_values("Puntos", ascending=False)
        df_rank['Posicion'] = range(1, len(df_rank)+1)
        
        for _, row in df_rank.iterrows():
            if row['Posicion'] <= 2: f_t = random.choice(FRASES_PUESTOS['oro'])
            elif row['Posicion'] <= 4: f_t = random.choice(FRASES_PUESTOS['plata'])
            elif row['Posicion'] <= 6: f_t = random.choice(FRASES_PUESTOS['bronce'])
            else: f_t = random.choice(FRASES_PUESTOS['barro'])
            
            l_u = calcular_logros_u(row['Usuario'], df_p_all, df_r_all, j_global, df_rank)
            icons = "".join([LOGROS_DATA[lid]['icon'] for lid in l_u])
            
            c1, c2, c3, c4 = st.columns([0.5, 1.2, 4, 1.5])
            with c1: st.markdown(f"### #{row['Posicion']}")
            with c2:
                fp = foto_dict.get(row['Usuario'])
                if fp and os.path.exists(str(fp)): st.image(fp, width=80)
                else: st.subheader("👤")
            with c3:
                st.markdown(f"**{row['Usuario']}** {icons}")
                st.info(f"_{f_t[0]}_ \n\n **— {f_t[1]}**")
            with c4: st.markdown(f"#### {row['Puntos']:.2f} pts")
            st.divider()

    # --- PESTAÑA: ESCENARIOS ---
    if usa_oraculo:
        with tabs[tab_list.index("🎲 Escenarios")]:
            st.header("🔮 El Oráculo de Probabilidades")
            st.write(f"Quedan {len(p_pend)} partidos. Calculando opciones de ganar la jornada...")
            probs = simular_oraculo(u_jugadores, df_p_all, df_r_all, j_global)
            if probs:
                for u, val in sorted(probs.items(), key=lambda x: x[1], reverse=True):
                    if val > 0:
                        st.write(f"**{u}**: {val:.1f}%")
                        st.progress(val/100)

    # --- PESTAÑA: ADMIN ---
    with tabs[tab_list.index("⚙️ Admin")]:
        if st.session_state.rol == "admin":
            st.header("⚙️ Panel de Gestión")
            adm_tabs = st.tabs(["⭐ Bases", "📸 Fotos", "⚽ Resultados"])
            
            with adm_tabs[0]:
                upd_b = []
                for u in u_jugadores:
                    pts_ex = 0.0
                    if not df_base.empty and u in df_base['Usuario'].values:
                        pts_ex = safe_float(df_base[df_base['Usuario'] == u].iloc[0]['Puntos'])
                    v = st.number_input(f"Base {u}", value=pts_ex, key=f"b_{u}")
                    upd_b.append({"Usuario": u, "Puntos": v})
                if st.button("Guardar Bases"):
                    conn.update(worksheet="PuntosBase", data=pd.DataFrame(upd_b))
                    st.success("Bases OK")
            
            with adm_tabs[2]:
                res_env = []
                h_ops = [time(h, m) for h in range(12, 23) for m in [0, 15, 30, 45]]
                for i, (loc, vis) in enumerate(JORNADAS[j_global]):
                    m_id = f"{loc}-{vis}"
                    st.subheader(f"⚽ {m_id}")
                    prev = df_r_all[(df_r_all['Jornada']==j_global) & (df_r_all['Partido']==m_id)]
                    dt, t_p, rl, rv, f = datetime.now(), "Normal", 0, 0, False
                    if not prev.empty:
                        t_p, rl, rv, f = prev.iloc[0]['Tipo'], int(prev.iloc[0]['R_L']), int(prev.iloc[0]['R_V']), prev.iloc[0]['Finalizado'] == "SI"
                        try: dt = datetime.strptime(str(prev.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                        except: pass
                    
                    c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 1, 1, 1])
                    nt = c1.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], index=["Normal", "Doble", "Esquizo"].index(t_p), key=f"t_{i}")
                    nf = c2.date_input("Fecha", value=dt.date(), key=f"d_{i}")
                    nh = c3.selectbox("Hora", h_ops, index=h_ops.index(dt.time()) if dt.time() in h_ops else 0, key=f"h_{i}")
                    nrl = c4.number_input("L", 0, value=rl, key=f"rl_{i}")
                    nrv = c5.number_input("V", 0, value=rv, key=f"rv_{i}")
                    nfina = c6.checkbox("Fin", value=f, key=f"f_{i}")
                    
                    res_env.append({"Jornada": j_global, "Partido": m_id, "Tipo": nt, "R_L": nrl, "R_V": nrv, "Hora_Inicio": datetime.combine(nf, nh).strftime("%Y-%m-%d %H:%M:%S"), "Finalizado": "SI" if nfina else "NO"})
                
                if st.button("Actualizar Jornada"):
                    otros = df_r_all[df_r_all['Jornada'] != j_global]
                    conn.update(worksheet="Resultados", data=pd.concat([otros, pd.DataFrame(res_env)], ignore_index=True))
                    st.success("Guardado")

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
                    else: st.write("⚽")
                with c2: pl = st.number_input(f"{loc}", 0, value=dl, key=f"pl_{i}", disabled=b)
                with c4: pv = st.number_input(f"{vis}", 0, value=dv, key=f"pv_{i}", disabled=b)
                with c5:
                    lv = get_logo(vis)
                    if lv: st.image(lv, width=65)
                    else: st.write("⚽")
                with c6: pub = st.checkbox("Público", value=dp, key=f"pb_{i}", disabled=b)
                env.append({"Usuario": st.session_state.user, "Jornada": j_global, "Partido": m_id, "P_L": pl, "P_V": pv, "Publica": "SI" if pub else "NO"})
            if st.button("💾 Guardar"):
                old = df_p_all[~((df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global))]
                conn.update(worksheet="Predicciones", data=pd.concat([old, pd.DataFrame(env)], ignore_index=True))
                st.rerun()

    # OTRAS PESTAÑAS (Simulador y Stats) se mantienen igual que las funcionales previas
