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

# Datos base de LaLiga extraídos de la clasificación oficial J24
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
CODIGO_INVITACION = "LIGA2026"

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
        return p_diff if (p_l - p_v) == (r_l - r_v) else p_ganador
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
    avg_goles = (df_u['P_L'] + df_u['P_V']).mean()
    locuras = 0
    for row in df_u.itertuples():
        try:
            eq_l, eq_v = row.Partido.split('-')
            if (NIVEL_EQUIPOS.get(eq_l, 3) >= NIVEL_EQUIPOS.get(eq_v, 3) + 2 and row.P_L > row.P_V) or \
               (NIVEL_EQUIPOS.get(eq_v, 3) >= NIVEL_EQUIPOS.get(eq_l, 3) + 2 and row.P_V > row.P_L):
                locuras += 1
        except: continue
    pct_loc = locuras / len(df_u)
    riesgo = (avg_goles / 5.0) + (pct_loc * 0.5)
    if pct_loc > 0.15: return "VISIONARIO ESQUIZO 🔮", f"Apuesta al débil ({locuras} veces).", riesgo
    if avg_goles > 3.4: return "BUSCADOR DE PLENOS 🤪", "Busca el ataque total.", riesgo
    if avg_goles < 2.1: return "CONSERVADOR 🛡️", "Fiel al 1-0.", riesgo
    return "ESTRATEGA ⚖️", "Apuesta con lógica.", riesgo

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
        if st.button("Aceptar"):
            df_u = leer_datos("Usuarios")
            if modo == "Iniciar Sesión":
                user_db = df_u[(df_u['Usuario'].astype(str) == str(u_in)) & (df_u['Password'].astype(str) == str(p_in))]
                if not user_db.empty:
                    st.session_state.autenticado, st.session_state.user, st.session_state.rol = True, u_in, user_db.iloc[0]['Rol']
                    st.rerun()
                else: st.error("❌ Datos incorrectos")
            else:
                nueva = pd.DataFrame([{"Usuario": u_in, "Password": p_in, "Rol": "user"}])
                conn.update(worksheet="Usuarios", data=pd.concat([df_u, nueva], ignore_index=True))
                st.success("✅ Registrado")
else:
    # --- CARGA DE DATOS ---
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

    with tabs[0]: # Apuestas
        if st.session_state.rol != "admin":
            mis_p = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)] if not df_p_all.empty else pd.DataFrame()
            df_rj = df_r_all[df_r_all['Jornada'] == j_global] if not df_r_all.empty else pd.DataFrame()
            preds_env = []
            for i, (loc, vis) in enumerate(JORNADAS[j_global]):
                m_id, bloq, tipo = f"{loc}-{vis}", False, "Normal"
                dl, dv, dp = 0, 0, False
                if not mis_p.empty:
                    prev = mis_p[mis_p['Partido'] == m_id]
                    if not prev.empty: dl, dv, dp = int(prev.iloc[0]['P_L']), int(prev.iloc[0]['P_V']), str(prev.iloc[0]['Publica']) == "SI"
                if not df_rj.empty and m_id in df_rj['Partido'].values:
                    inf = df_rj[df_rj['Partido'] == m_id].iloc[0]
                    tipo = inf['Tipo']
                    if datetime.now() > datetime.strptime(str(inf['Hora_Inicio']), "%Y-%m-%d %H:%M:%S"): bloq = True
                
                st.markdown(f"#### {tipo} {'🔒' if bloq else '🔓'}")
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
                st.divider()
            if st.button("💾 Guardar"):
                old = df_p_all[~((df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global))]
                conn.update(worksheet="Predicciones", data=pd.concat([old, pd.DataFrame(preds_env)], ignore_index=True))
                st.success("Guardado"); st.rerun()

    with tabs[1]: # Otros
        st.header("🔍 Predicciones Públicas")
        if not df_p_all.empty:
            p_pub = df_p_all[(df_p_all['Jornada'] == j_global) & (df_p_all['Publica'] == "SI")]
            if p_pub.empty: st.warning("Sin datos públicos.")
            for u in p_pub['Usuario'].unique():
                with st.expander(f"Apuestas de {u}"): st.table(p_pub[p_pub['Usuario'] == u][['Partido', 'P_L', 'P_V']])

    with tabs[2]: # Clasificación
        st.header("📊 Ranking")
        if not df_u_all.empty:
            j_fin = sorted(df_r_all[df_r_all['Finalizado'] == "SI"]['Jornada'].unique()) if not df_r_all.empty else []
            u_jug = [u for u in df_u_all['Usuario'].unique() if u not in admins]
            hist = []
            for u in u_jug:
                pb = safe_float(df_base[df_base['Usuario'] == u].iloc[0]['Puntos']) if not df_base.empty and u in df_base['Usuario'].values else 0.0
                hist.append({"Jornada": "Base", "Usuario": u, "Puntos": pb})
            res_d = df_r_all.set_index(['Jornada', 'Partido']).to_dict('index') if not df_r_all.empty else {}
            for j in j_fin:
                for u in u_jug:
                    pb = safe_float(df_base[df_base['Usuario'] == u].iloc[0]['Puntos']) if not df_base.empty and u in df_base['Usuario'].values else 0.0
                    pts = pb
                    u_p = df_p_all[df_p_all['Usuario'] == u] if not df_p_all.empty else pd.DataFrame()
                    for r in u_p.itertuples():
                        if r.Jornada in j_fin[:j_fin.index(j)+1]:
                            k = (r.Jornada, r.Partido)
                            if k in res_d and res_d[k]['Finalizado'] == "SI": pts += calcular_puntos(r.P_L, r.P_V, res_d[k]['R_L'], res_d[k]['R_V'], res_d[k]['Tipo'])
                    hist.append({"Jornada": j, "Usuario": u, "Puntos": pts})
            df_h = pd.DataFrame(hist)
            df_h['Posicion'] = df_h.groupby('Jornada')['Puntos'].rank(method='min', ascending=False)
            if len(df_h['Jornada'].unique()) > 1:
                fig = px.line(df_h, x="Jornada", y="Posicion", color="Usuario", markers=True)
                fig.update_yaxes(autorange="reversed", tick0=1, dtick=1); st.plotly_chart(fig, use_container_width=True)
            st.divider()
            u_j = j_fin[-1] if j_fin else "Base"
            df_act = df_h[df_h['Jornada'] == u_j].sort_values("Posicion")
            for _, row in df_act.iterrows():
                c1, c2, c3, c4 = st.columns([0.5, 1.2, 4, 1.5])
                with c1: st.markdown(f"### #{int(row['Posicion'])}")
                with c2:
                    fp = foto_dict.get(row['Usuario'])
                    if fp and pd.notna(fp) and os.path.exists(str(fp)): st.image(str(fp), width=85)
                    else: st.subheader("👤")
                with c3:
                    u_preds = df_p_all[df_p_all['Usuario'] == row['Usuario']] if not df_p_all.empty else pd.DataFrame()
                    np, dp, ri = obtener_perfil_apostador(u_preds)
                    st.markdown(f"**{row['Usuario']}** - *{np}*")
                    st.progress(min(ri, 1.0)); st.caption(dp)
                with c4: st.markdown(f"#### {row['Puntos']:.2f} pts")
                st.divider()

    with tabs[3]: # Detalles
        st.header(f"🏆 Detalles J: {j_global}")
        df_rf = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "SI")] if not df_r_all.empty else pd.DataFrame()
        if not df_rf.empty:
            jugs = [u for u in df_p_all['Usuario'].unique() if u not in admins]
            c_m = st.columns([2] + [1]*len(jugs))
            c_m[0].write("**Partido**")
            for i, u in enumerate(jugs):
                fp = foto_dict.get(u)
                if fp and pd.notna(fp) and os.path.exists(str(fp)): c_m[i+1].image(str(fp), width=45)
                else: c_m[i+1].write(u[:3])
            m_pts = pd.DataFrame(index=df_rf['Partido'].unique(), columns=jugs)
            m_sty = pd.DataFrame(index=df_rf['Partido'].unique(), columns=jugs)
            for p in m_pts.index:
                inf = df_rf[df_rf['Partido'] == p].iloc[0]
                for u in jugs:
                    up = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == j_global) & (df_p_all['Partido'] == p)] if not df_p_all.empty else pd.DataFrame()
                    pts = calcular_puntos(up.iloc[0]['P_L'], up.iloc[0]['P_V'], inf['R_L'], inf['R_V'], inf['Tipo']) if not up.empty else 0.0
                    m_pts.at[p, u], m_sty.at[p, u] = pts, aplicar_color_estilo(pts, inf['Tipo'])
            st.dataframe(m_pts.style.apply(lambda x: m_sty, axis=None).format("{:.2f}"))
        else: st.warning("Sin datos finalizados.")

    with tabs[4]: # Simulador Pro (Sin Escudos)
        st.header("🔮 Simulador de LaLiga")
        u_sim = [u for u in df_u_all['Usuario'].unique() if u not in admins] if not df_u_all.empty else []
        if u_sim:
            usr_s = st.selectbox("Simular según:", u_sim)
            if st.button("🚀 Simular"):
                sim_d = {k: v.copy() for k, v in STATS_LALIGA_BASE.items()}
                for p in (df_p_all[df_p_all['Usuario'] == usr_s].itertuples() if not df_p_all.empty else []):
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
                # Tabla sin columna 'Escudo' y empezando en 'Pos'
                st.dataframe(df_sim[['Pos', 'Equipo', 'PJ', 'V', 'E', 'D', 'GF', 'GC', 'DG', 'Pts']],
                             hide_index=True, use_container_width=True)

    with tabs[5]: # Admin
        if st.session_state.rol == "admin":
            st.header("🛠️ Panel Control")
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
                    st.write(f"--- {l} vs {v} ---")
                    m_id = f"{l}-{v}"
                    ex = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Partido'] == m_id)] if not df_r_all.empty else pd.DataFrame()
                    dt, t, rl, rv, f = datetime.now(), "Normal", 0, 0, False
                    if not ex.empty:
                        t, rl, rv, f = ex.iloc[0]['Tipo'], int(ex.iloc[0]['R_L']), int(ex.iloc[0]['R_V']), ex.iloc[0]['Finalizado'] == "SI"
                        try: dt = datetime.strptime(str(ex.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                        except: pass
                    c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 1, 1, 2])
                    tip_a = c1.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], index=["Normal", "Doble", "Esquizo"].index(t), key=f"at_{j_global}_{i}")
                    fec_a = c2.date_input("Fecha", value=dt.date(), key=f"af_{j_global}_{i}")
                    hor_a = c3.selectbox("Hora", h_p, index=h_p.index(dt.time()) if dt.time() in h_p else 36, key=f"ah_{j_global}_{i}")
                    rla, rva = c4.number_input("L", 0, value=rl, key=f"rl_{j_global}_{i}"), c5.number_input("V", 0, value=rv, key=f"rv_{j_global}_{i}")
                    fina = c6.checkbox("Fin", value=f, key=f"fi_{j_global}_{i}")
                    dt_s = datetime.combine(fec_a, hor_a).strftime("%Y-%m-%d %H:%M:%S")
                    r_env.append({"Jornada": j_global, "Partido": m_id, "Tipo": tip_a, "R_L": rla, "R_V": rva, "Hora_Inicio": dt_s, "Finalizado": "SI" if fina else "NO"})
                if st.button("Actualizar"):
                    old = df_r_all[df_r_all['Jornada'] != j_global] if not df_r_all.empty else pd.DataFrame()
                    conn.update(worksheet="Resultados", data=pd.concat([old, pd.DataFrame(r_env)], ignore_index=True)); st.rerun()
