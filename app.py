import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time
import os

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

# --- PUNTUACIONES Y REGLAS ---
SCORING = {"Normal": (0.5, 0.75, 1.0), "Doble": (1.0, 1.5, 2.0), "Esquizo": (1.0, 1.5, 3.0)}
CODIGO_INVITACION = "LIGA2026"

# --- 3. FUNCIONES DE APOYO ---
def get_logo(equipo):
    path = LOGOS.get(equipo)
    if path and os.path.exists(path):
        return path
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

# NUEVA FUNCIÓN DE COLORES SEGÚN TIPO DE PARTIDO
def aplicar_color_estilo(valor, tipo_partido):
    if valor == 0: return 'background-color: #ff4b4b; color: black' # Rojo siempre para 0
    
    if tipo_partido == "Normal":
        if valor == 0.5: return 'background-color: #ffd700; color: black' # Amarillo
        if valor == 0.75: return 'background-color: #ffa500; color: black' # Naranja
        if valor == 1.0: return 'background-color: #2baf2b; color: black' # Verde
        
    elif tipo_partido == "Doble":
        if valor in [1.0, 1.5]: return 'background-color: #a020f0; color: white' # Morado
        if valor == 2.0: return 'background-color: #2baf2b; color: black' # Verde
        
    elif tipo_partido == "Esquizo":
        if valor in [1.0, 1.5]: return 'background-color: #00f2ff; color: black' # Azul
        if valor == 3.0: return 'background-color: #2baf2b; color: black' # Verde
        
    return ''

st.set_page_config(page_title="Porra League 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos(pestaña):
    try:
        sheet_id = "1vFgccrCqmGrs9QfP8kxY_cESbRaJ_VxpsoAz-ZyL14E"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={pestaña}"
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- 4. ACCESO ---
if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>🏆 Porra League</h1>", unsafe_allow_html=True)
        modo = st.radio("Selecciona", ["Iniciar Sesión", "Registrarse"], horizontal=True)
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        
        if modo == "Iniciar Sesión":
            if st.button("Entrar"):
                df_u = leer_datos("Usuarios")
                if not df_u.empty:
                    user_db = df_u[(df_u['Usuario'].astype(str) == str(user_input)) & (df_u['Password'].astype(str) == str(pass_input))]
                    if not user_db.empty:
                        st.session_state.autenticado, st.session_state.user, st.session_state.rol = True, user_input, user_db.iloc[0]['Rol']
                        st.rerun()
                    else: st.error("❌ Datos incorrectos")
        else:
            cod_inv = st.text_input("Código de Invitación")
            if st.button("Crear Cuenta"):
                df_u = leer_datos("Usuarios")
                if cod_inv != CODIGO_INVITACION: st.error("🚫 Código inválido")
                elif not user_input or not pass_input: st.error("Campos vacíos")
                else:
                    nueva = pd.DataFrame([{"Usuario": user_input, "Password": pass_input, "Rol": "user"}])
                    conn.update(worksheet="Usuarios", data=pd.concat([df_u, nueva], ignore_index=True))
                    st.success("✅ Registrado con éxito")

# --- 5. CONTENIDO ---
else:
    c_head1, c_head2 = st.columns([6, 1])
    c_head1.title(f"Bienvenido, {st.session_state.user} 👋")
    if c_head2.button("Salir"):
        st.session_state.autenticado = False
        st.rerun()

    j_global = st.selectbox("📅 Seleccionar Jornada:", list(JORNADAS.keys()), key="global_j_sel")
    st.divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ Mis Apuestas", "👀 Ver Otras", "📊 Ranking", "🏆 Detalles", "⚙️ Admin"])

    df_r_all = leer_datos("Resultados")
    df_p_all = leer_datos("Predicciones")
    df_u_all = leer_datos("Usuarios")

    with tab1:
        if st.session_state.rol == "admin":
            st.info("💡 Eres Administrador. Gestiona la liga en la pestaña 'Admin'.")
        else:
            mis_preds = pd.DataFrame()
            if not df_p_all.empty:
                mis_preds = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)]
            df_r_j = df_r_all[df_r_all['Jornada'] == j_global] if not df_r_all.empty else pd.DataFrame()
            ahora = datetime.now()
            preds_a_enviar = []
            for i, (loc, vis) in enumerate(JORNADAS[j_global]):
                match_name = f"{loc}-{vis}"
                bloqueado, tipo = False, "Normal"
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
                    logo_l = get_logo(loc)
                    if logo_l: st.image(logo_l, width=65)
                    else: st.subheader("⚽")
                with c_in1: pl = st.number_input(f"{loc}", 0, value=def_l, key=f"l_{j_global}_{i}", disabled=bloqueado)
                with c_vs: st.markdown("<br><br>VS", unsafe_allow_html=True)
                with c_in2: pv = st.number_input(f"{vis}", 0, value=def_v, key=f"v_{j_global}_{i}", disabled=bloqueado)
                with c_img2:
                    logo_v = get_logo(vis)
                    if logo_v: st.image(logo_v, width=65)
                    else: st.subheader("⚽")
                with c_chk: 
                    st.write("")
                    pub = st.checkbox("Público", value=def_pub, key=f"pb_{j_global}_{i}", disabled=bloqueado)
                preds_a_enviar.append({"Usuario": st.session_state.user, "Jornada": j_global, "Partido": match_name, "P_L": pl, "P_V": pv, "Publica": "SI" if pub else "NO"})
                st.divider()
            if st.button("💾 Guardar Cambios"):
                df_p_write = leer_datos("Predicciones")
                if not df_p_write.empty:
                    df_p_write = df_p_write[~((df_p_write['Usuario'] == st.session_state.user) & (df_p_write['Jornada'] == j_global))]
                conn.update(worksheet="Predicciones", data=pd.concat([df_p_write, pd.DataFrame(preds_a_enviar)], ignore_index=True))
                st.success("¡Datos guardados!")
                st.rerun()

    with tab2:
        st.header(f"🔍 Predicciones públicas - {j_global}")
        if not df_p_all.empty:
            p_publicas = df_p_all[(df_p_all['Jornada'] == j_global) & (df_p_all['Publica'] == "SI")]
            if p_publicas.empty: st.info("Nada público todavía.")
            for u in p_publicas['Usuario'].unique():
                with st.expander(f"Apuestas de {u}"):
                    st.table(p_publicas[p_publicas['Usuario'] == u][['Partido', 'P_L', 'P_V']].rename(columns={'P_L': 'Local', 'P_V': 'Visitante'}))

    with tab3:
        st.header(f"📊 Clasificaciones - {j_global}")
        if not df_r_all.empty and not df_p_all.empty:
            admins = df_u_all[df_u_all['Rol'] == 'admin']['Usuario'].tolist()
            res_dict = df_r_all.set_index(['Jornada', 'Partido']).to_dict('index')
            ranking = []
            for u in df_p_all['Usuario'].unique():
                if u in admins: continue
                u_p = df_p_all[df_p_all['Usuario'] == u]
                pj, pt = 0, 0
                for r in u_p.itertuples():
                    key = (r.Jornada, r.Partido)
                    if key in res_dict and str(res_dict[key].get('Finalizado')) == "SI":
                        pts = calcular_puntos(r.P_L, r.P_V, res_dict[key]['R_L'], res_dict[key]['R_V'], res_dict[key]['Tipo'])
                        pt += pts
                        if r.Jornada == j_global: pj += pts
                ranking.append({"Usuario": u, "Puntos Jornada": pj, "Puntos Totales": pt})
            if ranking:
                df_final_rank = pd.DataFrame(ranking)
                cr1, cr2 = st.columns(2)
                with cr1:
                    st.subheader("Esta Jornada")
                    st.table(df_final_rank[['Usuario', 'Puntos Jornada']].sort_values("Puntos Jornada", ascending=False))
                with cr2:
                    st.subheader("General")
                    st.table(df_final_rank[['Usuario', 'Puntos Totales']].sort_values("Puntos Totales", ascending=False))

    with tab4:
        st.header(f"🏆 Detalle de Puntos: {j_global}")
        if not df_p_all.empty and not df_r_all.empty:
            admins = df_u_all[df_u_all['Rol'] == 'admin']['Usuario'].tolist()
            df_r_j_fin = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "SI")]
            if df_r_j_fin.empty:
                st.warning("Sin partidos finalizados.")
            else:
                usrs = [u for u in df_p_all['Usuario'].unique() if u not in admins]
                # Matriz para los puntos y matriz para los estilos
                matriz_puntos = pd.DataFrame(index=df_r_j_fin['Partido'].unique(), columns=usrs)
                matriz_estilos = pd.DataFrame(index=df_r_j_fin['Partido'].unique(), columns=usrs)
                for part in matriz_puntos.index:
                    info_partido = df_r_j_fin[df_r_j_fin['Partido'] == part].iloc[0]
                    tipo = info_partido['Tipo']
                    res_l, res_v = info_partido['R_L'], info_partido['R_V']
                    for u in usrs:
                        u_p = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == j_global) & (df_p_all['Partido'] == part)]
                        pts = calcular_puntos(u_p.iloc[0]['P_L'], u_p.iloc[0]['P_V'], res_l, res_v, tipo) if not u_p.empty else 0.0
                        matriz_puntos.at[part, u] = pts
                        matriz_estilos.at[part, u] = aplicar_color_estilo(pts, tipo)
                # Mostramos la tabla aplicando la matriz de estilos
                st.dataframe(matriz_puntos.style.apply(lambda x: matriz_estilos, axis=None).format("{:.2f}"))

    with tab5:
        if st.session_state.rol == "admin":
            st.header("🛠️ Panel de Administración")
            st.write(f"Configurando: **{j_global}**")
            h_perm = [time(h, m) for h in range(12, 23) for m in [0, 15, 30, 45]]
            conf_admin = []
            for i, (loc, vis) in enumerate(JORNADAS[j_global]):
                st.write(f"--- {loc} vs {vis} ---")
                c_t, c_f, c_h, c_rl, c_rv, c_fi = st.columns([2, 2, 2, 1, 1, 2])
                tipo_a = c_t.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], key=f"at_{j_global}_{i}")
                fec_a = c_f.date_input("Fecha", key=f"af_{j_global}_{i}")
                hor_a = c_h.selectbox("Hora", h_perm, format_func=lambda x: x.strftime("%H:%M"), key=f"ah_{j_global}_{i}", index=36)
                rl_a = c_rl.number_input("L", 0, key=f"arl_{j_global}_{i}")
                rv_a = c_rv.number_input("V", 0, key=f"arv_{j_global}_{i}")
                fin_a = c_fi.checkbox("Finalizado", key=f"afi_{j_global}_{i}")
                dt_save = datetime.combine(fec_a, hor_a).strftime("%Y-%m-%d %H:%M:%S")
                conf_admin.append({"Jornada": j_global, "Partido": f"{loc}-{vis}", "Tipo": tipo_a, "R_L": rl_a, "R_V": rv_a, "Hora_Inicio": dt_save, "Finalizado": "SI" if fin_a else "NO"})
            if st.button("🚀 Actualizar"):
                df_old_res = leer_datos("Resultados")
                if not df_old_res.empty: df_old_res = df_old_res[df_old_res['Jornada'] != j_global]
                conn.update(worksheet="Resultados", data=pd.concat([df_old_res, pd.DataFrame(conf_admin)], ignore_index=True))
                st.success("¡Datos guardados!")
        else:
            st.error("Acceso denegado.")
