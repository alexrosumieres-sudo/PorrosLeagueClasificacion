import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time
import os
import plotly.express as px

# --- 1. CONFIGURACIÓN DE JORNADAS ---
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

# --- 2. DICCIONARIO DE LOGOS ---
LOGOS = {
    "Athletic": "logos/athletic.jpeg", "Elche": "logos/elche.jpeg", "R. Sociedad": "logos/sociedad.jpeg",
    "Real Madrid": "logos/madrid.jpeg", "Barcelona": "logos/barca.jpeg", "Atlético": "logos/atletico.jpeg",
    "Rayo": "logos/rayo.jpeg", "Sevilla": "logos/sevilla.jpeg", "Valencia": "logos/valencia.jpeg",
    "Girona": "logos/girona.jpeg", "Osasuna": "logos/osasuna.jpeg", "Getafe": "logos/getafe.jpeg",
    "Celta": "logos/celta.jpeg", "Mallorca": "logos/mallorca.jpeg", "Villarreal": "logos/villarreal.jpeg",
    "Alavés": "logos/alaves.jpeg", "Espanyol": "logos/espanyol.jpeg", "Betis": "logos/betis.jpeg",
    "Levante": "logos/levante.jpeg", "Oviedo": "logos/oviedo.jpeg"
}

SCORING = {"Normal": (0.5, 0.75, 1.0), "Doble": (1.0, 1.5, 2.0), "Esquizo": (1.0, 1.5, 3.0)}
CODIGO_INVITACION = "LIGA2026"

# --- 3. FUNCIONES LÓGICAS ---

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

def aplicar_color_estilo(valor, tipo_partido):
    if valor == 0: return 'background-color: #ff4b4b; color: black'
    if tipo_partido == "Normal":
        if valor == 0.5: return 'background-color: #ffd700; color: black'
        if valor == 0.75: return 'background-color: #ffa500; color: black'
        if valor == 1.0: return 'background-color: #2baf2b; color: black'
    elif tipo_partido == "Doble":
        if valor in [1.0, 1.5]: return 'background-color: #a020f0; color: white'
        if valor == 2.0: return 'background-color: #2baf2b; color: black'
    elif tipo_partido == "Esquizo":
        if valor in [1.0, 1.5]: return 'background-color: #00f2ff; color: black'
        if valor == 3.0: return 'background-color: #2baf2b; color: black'
    return ''

def obtener_perfil_apostador(df_usuario):
    if df_usuario.empty: return "Novato 🐣", "Sin datos aún."
    avg_goles = (df_usuario['P_L'] + df_usuario['P_V']).mean()
    dif_promedio = abs(df_usuario['P_L'] - df_usuario['P_V']).mean()
    if avg_goles > 3.5 or dif_promedio > 2.5:
        return "KAMIKAZE / ESQUIZO 🤪", "Busca la gloria en resultados improbables. No le teme al 4-3."
    elif avg_goles > 2.2:
        avg_empates = (df_usuario['P_L'] == df_usuario['P_V']).mean()
        if avg_empates > 0.35: return "EL REY DEL EMPATE 🤝", "Cree que nadie quiere ganar. Su favorito es el 1-1."
        return "EQUILIBRADO ⚖️", "Apuesta con lógica. Sabe cuándo arriesgar."
    else:
        return "CONSERVADOR / AMARRETE 🛡️", "Asegura puntos con el 1-0 o 2-1. No arriesga ni un pelo."

# --- 4. CONFIGURACIÓN APP ---
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
        u_in = st.text_input("Usuario")
        p_in = st.text_input("Contraseña", type="password")
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
            cod = st.text_input("Código de Invitación")
            if st.button("Crear Cuenta"):
                df_u = leer_datos("Usuarios")
                if cod != CODIGO_INVITACION: st.error("🚫 Código inválido")
                else:
                    nueva = pd.DataFrame([{"Usuario": u_in, "Password": p_in, "Rol": "user"}])
                    conn.update(worksheet="Usuarios", data=pd.concat([df_u, nueva], ignore_index=True))
                    st.success("✅ Registrado")

# --- CONTENIDO PRINCIPAL ---
else:
    c_h1, c_h2 = st.columns([6, 1])
    c_h1.title(f"Hola, {st.session_state.user} 👋")
    if c_h2.button("Salir"):
        st.session_state.autenticado = False
        st.rerun()

    j_global = st.selectbox("📅 Seleccionar Jornada:", list(JORNADAS.keys()), key="global_j_sel")
    st.divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ Mis Apuestas", "👀 Ver Otras", "📊 Ranking", "🏆 Detalles", "⚙️ Admin"])

    df_r_all = leer_datos("Resultados")
    df_p_all = leer_datos("Predicciones")
    df_u_all = leer_datos("Usuarios")
    df_base = leer_datos("PuntosBase")

    with tab1:
        if st.session_state.rol == "admin":
            st.info("💡 Modo Administrador activo.")
        else:
            mis_preds = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)] if not df_p_all.empty else pd.DataFrame()
            df_r_j = df_r_all[df_r_all['Jornada'] == j_global] if not df_r_all.empty else pd.DataFrame()
            ahora, preds_enviar = datetime.now(), []
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
                    tipo = info['Tipo']
                    try:
                        limite = datetime.strptime(str(info['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                        if ahora > limite: bloqueado = True
                    except: pass
                st.markdown(f"#### {tipo} {'🔒' if bloqueado else '🔓'}")
                c_img1, c_in1, c_vs, c_in2, c_img2, c_chk = st.columns([1, 2, 0.5, 2, 1, 2])
                with c_img1: 
                    logo_path = get_logo(loc)
                    if logo_path: st.image(logo_path, width=65)
                    else: st.subheader("⚽")
                with c_in1: pl = st.number_input(f"{loc}", 0, value=def_l, key=f"l_{j_global}_{i}", disabled=bloqueado)
                with c_vs: st.markdown("<br><br>VS", unsafe_allow_html=True)
                with c_in2: pv = st.number_input(f"{vis}", 0, value=def_v, key=f"v_{j_global}_{i}", disabled=bloqueado)
                with c_img2:
                    logo_path_v = get_logo(vis)
                    if logo_path_v: st.image(logo_path_v, width=65)
                    else: st.subheader("⚽")
                with c_chk: 
                    st.write(""); pub = st.checkbox("Público", value=def_pub, key=f"pb_{j_global}_{i}", disabled=bloqueado)
                preds_enviar.append({"Usuario": st.session_state.user, "Jornada": j_global, "Partido": match_name, "P_L": pl, "P_V": pv, "Publica": "SI" if pub else "NO"})
                st.divider()
            if st.button("💾 Guardar"):
                df_p_write = df_p_all[~((df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global))] if not df_p_all.empty else pd.DataFrame()
                conn.update(worksheet="Predicciones", data=pd.concat([df_p_write, pd.DataFrame(preds_enviar)], ignore_index=True))
                st.success("¡Datos guardados!"); st.rerun()

    with tab2:
        st.header("🔍 Predicciones Públicas")
        if not df_p_all.empty:
            p_pub = df_p_all[(df_p_all['Jornada'] == j_global) & (df_p_all['Publica'] == "SI")]
            if p_pub.empty: st.info("Nada público por ahora.")
            for u in p_pub['Usuario'].unique():
                with st.expander(f"Apuestas de {u}"):
                    st.table(p_pub[p_pub['Usuario'] == u][['Partido', 'P_L', 'P_V']].rename(columns={'P_L': 'Local', 'P_V': 'Visitante'}))

    with tab3:
        st.header("📊 Clasificación y Análisis")
        if not df_r_all.empty and not df_p_all.empty:
            admins = df_u_all[df_u_all['Rol'] == 'admin']['Usuario'].tolist()
            res_dict = df_r_all.set_index(['Jornada', 'Partido']).to_dict('index')
            jornadas_fin = sorted(df_r_all[df_r_all['Finalizado'] == "SI"]['Jornada'].unique())
            
            historia = []
            usuarios_jug = [u for u in df_p_all['Usuario'].unique() if u not in admins]
            
            for j_prog in jornadas_fin:
                temp_rank = []
                for u in usuarios_jug:
                    pts_base = 0.0
                    if not df_base.empty and 'Puntos' in df_base.columns:
                        m_b = df_base[df_base['Usuario'] == u]
                        if not m_b.empty:
                            try: pts_base = float(m_b.iloc[0]['Puntos'])
                            except: pts_base = 0.0
                    
                    pts_acum = pts_base
                    u_preds = df_p_all[df_p_all['Usuario'] == u]
                    for r in u_preds.itertuples():
                        if r.Jornada in jornadas_fin[:jornadas_fin.index(j_prog)+1]:
                            k = (r.Jornada, r.Partido)
                            if k in res_dict and str(res_dict[k].get('Finalizado')) == "SI":
                                pts_acum += calcular_puntos(r.P_L, r.P_V, res_dict[k]['R_L'], res_dict[k]['R_V'], res_dict[k]['Tipo'])
                    temp_rank.append({"Usuario": u, "Puntos": pts_acum})
                
                df_temp = pd.DataFrame(temp_rank).sort_values("Puntos", ascending=False)
                df_temp['Posicion'] = range(1, len(df_temp) + 1)
                for row in df_temp.itertuples():
                    historia.append({"Jornada": j_prog, "Usuario": row.Usuario, "Posicion": row.Posicion, "Puntos": row.Puntos})

            if historia:
                df_hist = pd.DataFrame(historia)
                df_act = df_hist[df_hist['Jornada'] == j_global]
                if df_act.empty and jornadas_fin: df_act = df_hist[df_hist['Jornada'] == jornadas_fin[-1]]
                
                c_rank, c_graph = st.columns([1, 2])
                c_rank.subheader("Ranking General")
                c_rank.table(df_act[['Usuario', 'Puntos']].sort_values("Puntos", ascending=False))
                
                with c_graph:
                    st.subheader("📈 Evolución de Posición")
                    fig = px.line(df_hist, x="Jornada", y="Posicion", color="Usuario", markers=True)
                    fig.update_yaxes(autorange="reversed", tick0=1, dtick=1)
                    st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.subheader("👤 Análisis de Perfil")
            cols_perfil = st.columns(3)
            for idx, u in enumerate(usuarios_jug):
                df_u_p = df_p_all[df_p_all['Usuario'] == u]
                nombre_p, desc_p = obtener_perfil_apostador(df_u_p)
                with cols_perfil[idx % 3]:
                    st.markdown(f"**{u}**")
                    st.caption(nombre_p)
                    riesgo_val = (df_u_p['P_L'] + df_u_p['P_V']).mean() / 5.0
                    st.progress(min(riesgo_val, 1.0))
                    st.info(desc_p)

    with tab4:
        st.header(f"🏆 Detalle de Puntos: {j_global}")
        if not df_p_all.empty and not df_r_all.empty:
            admins = df_u_all[df_u_all['Rol'] == 'admin']['Usuario'].tolist()
            df_r_j_f = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "SI")]
            if df_r_j_f.empty: st.warning("Sin partidos finalizados aún.")
            else:
                jugadores = [u for u in df_p_all['Usuario'].unique() if u not in admins]
                m_pts = pd.DataFrame(index=df_r_j_f['Partido'].unique(), columns=jugadores)
                m_sty = pd.DataFrame(index=df_r_j_f['Partido'].unique(), columns=jugadores)
                for p_name in m_pts.index:
                    info_p = df_r_j_f[df_r_j_f['Partido'] == p_name].iloc[0]
                    for u in jugadores:
                        u_ap = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == j_global) & (df_p_all['Partido'] == p_name)]
                        pts_v = calcular_puntos(u_ap.iloc[0]['P_L'], u_ap.iloc[0]['P_V'], info_p['R_L'], info_p['R_V'], info_p['Tipo']) if not u_ap.empty else 0.0
                        m_pts.at[p_name, u] = pts_v
                        m_sty.at[p_name, u] = aplicar_color_estilo(pts_v, info_p['Tipo'])
                st.dataframe(m_pts.style.apply(lambda x: m_sty, axis=None).format("{:.2f}"))

    with tab5:
        if st.session_state.rol == "admin":
            st.header("🛠️ Panel Admin")
            with st.expander("⭐ Configurar Puntos Iniciales (Pre-J25)"):
                base_upd = []
                for u in [usr for usr in df_u_all['Usuario'].unique() if usr not in admins]:
                    pts_prev = 0.0
                    if not df_base.empty and 'Puntos' in df_base.columns:
                        m_b = df_base[df_base['Usuario'] == u]
                        if not m_b.empty:
                            try: pts_prev = float(m_b.iloc[0]['Puntos'])
                            except: pts_prev = 0.0
                    val_new = st.number_input(f"Base para {u}", value=pts_prev, step=0.25, key=f"b_{u}")
                    base_upd.append({"Usuario": u, "Puntos": val_new})
                if st.button("Guardar Puntos Iniciales"):
                    conn.update(worksheet="PuntosBase", data=pd.DataFrame(base_upd))
                    st.success("Actualizado"); st.rerun()

            st.write(f"Resultados Jornada: {j_global}")
            h_list, res_env = [time(h, m) for h in range(12, 23) for m in [0, 15, 30, 45]], []
            for i, (l, v) in enumerate(JORNADAS[j_global]):
                st.write(f"--- {l} vs {v} ---")
                c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 1, 1, 2])
                t_a = c1.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], key=f"ta_{j_global}_{i}")
                f_a = c2.date_input("Fecha", key=f"fa_{j_global}_{i}")
                h_a = c3.selectbox("Hora", h_list, format_func=lambda x: x.strftime("%H:%M"), key=f"ha_{j_global}_{i}", index=36)
                rl_a = c4.number_input("L", 0, key=f"rla_{j_global}_{i}")
                rv_a = c5.number_input("V", 0, key=f"rva_{j_global}_{i}")
                fi_a = c6.checkbox("Fin", key=f"fia_{j_global}_{i}")
                dt_a = datetime.combine(f_a, h_a).strftime("%Y-%m-%d %H:%M:%S")
                res_env.append({"Jornada": j_global, "Partido": f"{l}-{v}", "Tipo": t_a, "R_L": rl_a, "R_V": rv_a, "Hora_Inicio": dt_a, "Finalizado": "SI" if fi_a else "NO"})
            if st.button("🚀 Actualizar Resultados"):
                df_old = df_r_all[df_r_all['Jornada'] != j_global] if not df_r_all.empty else pd.DataFrame()
                conn.update(worksheet="Resultados", data=pd.concat([df_old, pd.DataFrame(res_env)], ignore_index=True))
                st.success("¡Resultados actualizados!"); st.rerun()
