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

PUNTOS_LALIGA_BASE = {
    "Real Madrid": 60, "Barcelona": 58, "Villarreal": 48, "Atlético": 45,
    "Betis": 41, "Espanyol": 35, "Celta": 34, "R. Sociedad": 31, "Athletic": 31,
    "Osasuna": 30, "Getafe": 29, "Girona": 29, "Sevilla": 26, "Alavés": 26,
    "Valencia": 26, "Elche": 25, "Rayo": 25, "Mallorca": 24, "Levante": 18, "Oviedo": 16
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
CODIGO_INVITACION = "LIGA2026"

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
    if signo_p == signo_r:
        return p_diff if (p_l - p_v) == (r_l - r_v) else p_ganador
    return 0.0

def aplicar_color_estilo(valor, tipo_partido):
    if valor == 0: return 'background-color: #ff4b4b; color: black'
    if tipo_partido == "Normal":
        if valor == 0.5: return 'background-color: #ffd700; color: black'
        if valor == 0.75: return 'background-color: #ffa500; color: black'
        return 'background-color: #2baf2b; color: black'
    if tipo_partido == "Doble":
        if valor in [1.0, 1.5]: return 'background-color: #a020f0; color: white'
        return 'background-color: #2baf2b; color: black'
    if tipo_partido == "Esquizo":
        if valor in [1.0, 1.5]: return 'background-color: #00f2ff; color: black'
        return 'background-color: #2baf2b; color: black'
    return ''

def obtener_perfil_apostador(df_usuario):
    if df_usuario.empty: return "Novato 🐣", "Sin datos aún.", 0.0
    avg_goles = (df_usuario['P_L'] + df_usuario['P_V']).mean()
    locuras = 0
    for row in df_usuario.itertuples():
        try:
            eq_l, eq_v = row.Partido.split('-')
            if (NIVEL_EQUIPOS.get(eq_l, 3) >= NIVEL_EQUIPOS.get(eq_v, 3) + 2 and row.P_L > row.P_V) or \
               (NIVEL_EQUIPOS.get(eq_v, 3) >= NIVEL_EQUIPOS.get(eq_l, 3) + 2 and row.P_V > row.P_L):
                locuras += 1
        except: continue
    pct_locuras = locuras / len(df_usuario) if len(df_usuario) > 0 else 0
    riesgo = (avg_goles / 5.0) + (pct_locuras * 0.5)
    if pct_locuras > 0.15: return "EL VISIONARIO / ESQUIZO TOTAL 🔮", f"Confía en los milagros ({locuras} locuras).", riesgo
    if avg_goles > 3.4: return "BUSCADOR DE PLENOS 🤪", "Busca el ataque total.", riesgo
    if avg_goles < 2.1: return "CONSERVADOR / AMARRETE 🛡️", "Fiel al 1-0.", riesgo
    return "ESTRATEGA ⚖️", "Apuesta con lógica.", riesgo

# --- 3. INICIO DE APP ---
st.set_page_config(page_title="Porra League 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos(pestaña):
    try:
        sheet_id = "1vFgccrCqmGrs9QfP8kxY_cESbRaJ_VxpsoAz-ZyL14E"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={pestaña}"
        return pd.read_csv(url)
    except: return pd.DataFrame()

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# --- ACCESO ---
if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>🏆 Porra League</h1>", unsafe_allow_html=True)
        modo = st.radio("Selecciona", ["Iniciar Sesión", "Registrarse"], horizontal=True)
        u_in, p_in = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
        if modo == "Iniciar Sesión":
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
# --- CONTENIDO ---
else:
    df_perfiles = leer_datos("ImagenesPerfil")
    foto_dict = df_perfiles.set_index('Usuario')['ImagenPath'].to_dict() if not df_perfiles.empty else {}
    
    c_h1, c_h2, c_h3 = st.columns([1, 5, 1])
    with c_h1:
        mi_foto = foto_dict.get(st.session_state.user)
        if mi_foto and pd.notna(mi_foto) and os.path.exists(str(mi_foto)): st.image(str(mi_foto), width=70)
        else: st.subheader("👤")
    with c_h2: st.title(f"Hola, {st.session_state.user} 👋")
    with c_h3: 
        if st.button("Salir"): st.session_state.autenticado = False; st.rerun()

    j_global = st.selectbox("📅 Seleccionar Jornada:", list(JORNADAS.keys()), key="global_j")
    st.divider()

    tabs = st.tabs(["✍️ Apuestas", "👀 Otros", "📊 Clasificación", "🏆 Detalles", "🔮 Simulador", "⚙️ Admin"])

    df_r_all = leer_datos("Resultados")
    df_p_all = leer_datos("Predicciones")
    df_u_all = leer_datos("Usuarios")
    df_base = leer_datos("PuntosBase")

    with tabs[0]: # Apuestas
        if st.session_state.rol == "admin": st.info("💡 Modo Admin activo.")
        else:
            mis_preds = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)] if not df_p_all.empty else pd.DataFrame()
            df_r_j = df_r_all[df_r_all['Jornada'] == j_global] if not df_r_all.empty else pd.DataFrame()
            ahora, preds_env = datetime.now(), []
            for i, (loc, vis) in enumerate(JORNADAS[j_global]):
                match_name, bloqueado, tipo = f"{loc}-{vis}", False, "Normal"
                def_l, def_v, def_pub = 0, 0, False
                if not mis_preds.empty:
                    m_prev = mis_preds[mis_preds['Partido'] == match_name]
                    if not m_prev.empty:
                        def_l, def_v = int(m_prev.iloc[0]['P_L']), int(m_prev.iloc[0]['P_V'])
                        def_pub = True if str(m_prev.iloc[0]['Publica']) == "SI" else False
                if not df_r_j.empty and match_name in df_r_j['Partido'].values:
                    info = df_r_j[df_r_j['Partido'] == match_name].iloc[0]
                    tipo, limite = info['Tipo'], datetime.strptime(str(info['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                    if ahora > limite: bloqueado = True
                st.markdown(f"#### {tipo} {'🔒' if bloqueado else '🔓'}")
                c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 0.5, 2, 1, 2])
                with c1: 
                    logo = get_logo(loc)
                    if logo: st.image(logo, width=65)
                    else: st.markdown("⚽")
                with c2: pl = st.number_input(f"{loc}", 0, value=def_l, key=f"l_{j_global}_{i}", disabled=bloqueado)
                with c3: st.markdown("<br><br>VS", unsafe_allow_html=True)
                with c4: pv = st.number_input(f"{vis}", 0, value=def_v, key=f"v_{j_global}_{i}", disabled=bloqueado)
                with c5:
                    logo_v = get_logo(vis)
                    if logo_v: st.image(logo_v, width=65)
                    else: st.markdown("⚽")
                with c6: pub = st.checkbox("Público", value=def_pub, key=f"pb_{j_global}_{i}", disabled=bloqueado)
                preds_env.append({"Usuario": st.session_state.user, "Jornada": j_global, "Partido": match_name, "P_L": pl, "P_V": pv, "Publica": "SI" if pub else "NO"})
            if st.button("💾 Guardar"):
                old_p = df_p_all[~((df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global))] if not df_p_all.empty else pd.DataFrame()
                conn.update(worksheet="Predicciones", data=pd.concat([old_p, pd.DataFrame(preds_env)], ignore_index=True))
                st.success("Guardado"); st.rerun()

    with tabs[1]: # Otros
        st.header("🔍 Predicciones Públicas")
        if not df_p_all.empty:
            p_pub = df_p_all[(df_p_all['Jornada'] == j_global) & (df_p_all['Publica'] == "SI")]
            for u in p_pub['Usuario'].unique():
                with st.expander(f"Apuestas de {u}"):
                    st.table(p_pub[p_pub['Usuario'] == u][['Partido', 'P_L', 'P_V']])

    with tabs[2]: # Clasificación
        st.header("📊 Clasificación y Evolución")
        admins = df_u_all[df_u_all['Rol'] == 'admin']['Usuario'].tolist()
        if not df_u_all.empty:
            res_dict = df_r_all.set_index(['Jornada', 'Partido']).to_dict('index') if not df_r_all.empty else {}
            jornadas_fin = sorted(df_r_all[df_r_all['Finalizado'] == "SI"]['Jornada'].unique()) if not df_r_all.empty else []
            usuarios_jug = [u for u in df_u_all['Usuario'].unique() if u not in admins]
            
            historia = []
            # ESTADO INICIAL (JORNADA BASE)
            temp_base = []
            for u in usuarios_jug:
                p_base = 0.0
                if not df_base.empty and u in df_base['Usuario'].values:
                    p_base = safe_float(df_base[df_base['Usuario'] == u].iloc[0]['Puntos'])
                temp_base.append({"Usuario": u, "Puntos": p_base})
            df_b_rank = pd.DataFrame(temp_base).sort_values("Puntos", ascending=False)
            df_b_rank['Posicion'] = range(1, len(df_b_rank) + 1)
            for row in df_b_rank.itertuples():
                historia.append({"Jornada": "Base", "Usuario": row.Usuario, "Posicion": row.Posicion, "Puntos": row.Puntos})

            # EVOLUCIÓN POR JORNADA
            for j_prog in jornadas_fin:
                temp = []
                for u in usuarios_jug:
                    p_base = 0.0
                    if not df_base.empty and u in df_base['Usuario'].values:
                        p_base = safe_float(df_base[df_base['Usuario'] == u].iloc[0]['Puntos'])
                    pts_acum = p_base
                    u_preds = df_p_all[df_p_all['Usuario'] == u] if not df_p_all.empty else pd.DataFrame()
                    if not u_preds.empty:
                        for r in u_preds.itertuples():
                            if r.Jornada in jornadas_fin[:jornadas_fin.index(j_prog)+1]:
                                k = (r.Jornada, r.Partido)
                                if k in res_dict and str(res_dict[k].get('Finalizado')) == "SI":
                                    pts_acum += calcular_puntos(r.P_L, r.P_V, res_dict[k]['R_L'], res_dict[k]['R_V'], res_dict[k]['Tipo'])
                    temp.append({"Usuario": u, "Puntos": pts_acum})
                df_temp = pd.DataFrame(temp).sort_values("Puntos", ascending=False)
                df_temp['Posicion'] = range(1, len(df_temp) + 1)
                for row in df_temp.itertuples(): historia.append({"Jornada": j_prog, "Usuario": row.Usuario, "Posicion": row.Posicion, "Puntos": row.Puntos})
            
            df_hist = pd.DataFrame(historia)
            
            # Gráfico de Evolución
            if len(df_hist['Jornada'].unique()) > 1:
                fig = px.line(df_hist, x="Jornada", y="Posicion", color="Usuario", markers=True)
                fig.update_yaxes(autorange="reversed", tick0=1, dtick=1); st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.subheader("🏆 Leaderboard")
            
            # Mostramos la última jornada disponible (si no hay finalizadas, mostramos la Base)
            ultima_j = jornadas_fin[-1] if jornadas_fin else "Base"
            df_act = df_hist[df_hist['Jornada'] == ultima_j].sort_values("Posicion")
            
            for _, row in df_act.iterrows():
                c_r1, c_r2, c_r3, c_r4 = st.columns([0.5, 1.2, 4, 1.5])
                with c_r1: st.markdown(f"### #{row['Posicion']}")
                with c_r2:
                    f_p = foto_dict.get(row['Usuario'])
                    if f_p and pd.notna(f_p) and os.path.exists(str(f_p)): st.image(str(f_p), width=85)
                    else: st.subheader("👤")
                with c_r3:
                    u_ap = df_p_all[df_p_all['Usuario'] == row['Usuario']] if not df_p_all.empty else pd.DataFrame()
                    n_p, d_p, ri = obtener_perfil_apostador(u_ap)
                    st.markdown(f"**{row['Usuario']}** - *{n_p}*")
                    st.progress(min(ri, 1.0))
                    st.caption(d_p)
                with c_r4: st.markdown(f"#### {row['Puntos']:.2f} pts")
                st.divider()

    with tabs[3]: # Detalles
        st.header(f"🏆 Detalle Puntos: {j_global}")
        df_r_j_f = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "SI")] if not df_r_all.empty else pd.DataFrame()
        if not df_r_j_f.empty:
            jugs = [u for u in df_u_all['Usuario'].unique() if u not in admins]
            c_mini = st.columns([2] + [1]*len(jugs))
            c_mini[0].write("**Partido**")
            for i, u in enumerate(jugs):
                fp = foto_dict.get(u)
                if fp and pd.notna(fp) and os.path.exists(str(fp)): c_mini[i+1].image(str(fp), width=45)
                else: c_mini[i+1].write(u[:3])
            
            m_pts = pd.DataFrame(index=df_r_j_f['Partido'].unique(), columns=jugs)
            m_sty = pd.DataFrame(index=df_r_j_f['Partido'].unique(), columns=jugs)
            for p in m_pts.index:
                inf = df_r_j_f[df_r_j_f['Partido'] == p].iloc[0]
                for u in jugs:
                    u_p = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == j_global) & (df_p_all['Partido'] == p)] if not df_p_all.empty else pd.DataFrame()
                    pts = calcular_puntos(u_p.iloc[0]['P_L'], u_p.iloc[0]['P_V'], inf['R_L'], inf['R_V'], inf['Tipo']) if not u_p.empty else 0.0
                    m_pts.at[p, u], m_sty.at[p, u] = pts, aplicar_color_estilo(pts, inf['Tipo'])
            st.dataframe(m_pts.style.apply(lambda x: m_sty, axis=None).format("{:.2f}"))
        else: st.info("La jornada aún no ha comenzado o no hay partidos finalizados.")

    with tabs[4]: # Simulador
        st.header("🔮 Simulador de LaLiga")
        opciones_sim = [u for u in df_u_all['Usuario'].unique() if u not in admins]
        if opciones_sim:
            usr_sim = st.selectbox("Simular resultados según:", opciones_sim)
            if st.button("🚀 Ejecutar Simulación"):
                clas = PUNTOS_LALIGA_BASE.copy()
                u_preds = df_p_all[df_p_all['Usuario'] == usr_sim] if not df_p_all.empty else pd.DataFrame()
                for p in u_preds.itertuples():
                    try:
                        tl, tv = p.Partido.split('-')
                        if p.P_L > p.P_V: clas[tl] += 3
                        elif p.P_V > p.P_L: clas[tv] += 3
                        else: clas[tl] += 1; clas[tv] += 1
                    except: continue
                df_s = pd.DataFrame(list(clas.items()), columns=['Equipo', 'Pts']).sort_values('Pts', ascending=False)
                df_s['Pos'] = range(1, 21); st.table(df_s[['Pos', 'Equipo', 'Pts']])

    with tabs[5]: # Admin
        if st.session_state.rol == "admin":
            st.header("🛠️ Panel Control")
            adm_tabs = st.tabs(["⭐ Puntos Base", "📸 Avatares", "⚽ Resultados"])
            with adm_tabs[0]:
                base_upd = []
                for u in [usr for usr in df_u_all['Usuario'].unique() if usr not in admins]:
                    p_ex = safe_float(df_base[df_base['Usuario'] == u].iloc[0]['Puntos']) if not df_base.empty and u in df_base['Usuario'].values else 0.0
                    v_n = st.number_input(f"Base {u}", value=p_ex, key=f"b_{u}")
                    base_upd.append({"Usuario": u, "Puntos": v_n})
                if st.button("Guardar Bases"): conn.update(worksheet="PuntosBase", data=pd.DataFrame(base_upd)); st.rerun()
            with adm_tabs[1]:
                if os.path.exists(PERFILES_DIR):
                    fotos = sorted(os.listdir(PERFILES_DIR))
                    p_data = []
                    for u in [usr for usr in df_u_all['Usuario'].unique() if usr not in admins]:
                        idx_f = 0
                        path_db = foto_dict.get(u)
                        if pd.notna(path_db):
                            nombre_archivo = str(path_db).replace(PERFILES_DIR, "")
                            if nombre_archivo in fotos: idx_f = fotos.index(nombre_archivo) + 1
                        f_sel = st.selectbox(f"Imagen para {u}", ["Ninguna"] + fotos, index=idx_f, key=f"img_{u}")
                        p_data.append({"Usuario": u, "ImagenPath": f"{PERFILES_DIR}{f_sel}" if f_sel != "Ninguna" else ""})
                    if st.button("Asociar Avatares"): conn.update(worksheet="ImagenesPerfil", data=pd.DataFrame(p_data)); st.rerun()
            with adm_tabs[2]:
                r_env = []
                for i, (l, v) in enumerate(JORNADAS[j_global]):
                    st.write(f"--- {l} vs {v} ---")
                    c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 1, 1, 2])
                    tip = c1.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], key=f"at_{j_global}_{i}")
                    fec = c2.date_input("Fecha", key=f"af_{j_global}_{i}")
                    hor = c3.selectbox("Hora", [time(h, m) for h in range(12, 23) for m in [0, 15, 30, 45]], key=f"ah_{j_global}_{i}", index=36)
                    rl, rv = c4.number_input("L", 0, key=f"rl_{j_global}_{i}"), c5.number_input("V", 0, key=f"rv_{j_global}_{i}")
                    fin = c6.checkbox("Fin", key=f"fi_{j_global}_{i}")
                    dt = datetime.combine(fec, hor).strftime("%Y-%m-%d %H:%M:%S")
                    r_env.append({"Jornada": j_global, "Partido": f"{l}-{v}", "Tipo": tip, "R_L": rl, "R_V": rv, "Hora_Inicio": dt, "Finalizado": "SI" if fin else "NO"})
                if st.button("Publicar Resultados"):
                    old = df_r_all[df_r_all['Jornada'] != j_global] if not df_r_all.empty else pd.DataFrame()
                    conn.update(worksheet="Resultados", data=pd.concat([old, pd.DataFrame(r_env)], ignore_index=True)); st.rerun()
