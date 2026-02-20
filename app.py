import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time

# --- 1. CONFIGURACIÓN DE JORNADAS Y EQUIPOS ---
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
    "Athletic": "https://upload.wikimedia.org/wikipedia/en/thumb/9/98/Club_Athletic_Bilbao_logo.svg/1200px-Club_Athletic_Bilbao_logo.svg.png",
    "Elche": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a7/Elche_CF_logo.svg/1200px-Elche_CF_logo.svg.png",
    "R. Sociedad": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f1/Real_Sociedad_logo.svg/1200px-Real_Sociedad_logo.svg.png",
    "Real Madrid": "https://upload.wikimedia.org/wikipedia/en/thumb/5/56/Real_Madrid_CF.svg/1200px-Real_Madrid_CF.svg.png",
    "Barcelona": "https://upload.wikimedia.org/wikipedia/en/thumb/4/47/FC_Barcelona_(crest).svg/1200px-FC_Barcelona_(crest).svg.png",
    "Atlético": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f4/Atletico_Madrid_2017_logo.svg/1200px-Atletico_Madrid_2017_logo.svg.png",
    "Rayo": "https://upload.wikimedia.org/wikipedia/en/thumb/3/3b/Rayo_Vallecano_logo.svg/1200px-Rayo_Vallecano_logo.svg.png",
    "Sevilla": "https://upload.wikimedia.org/wikipedia/en/thumb/3/3b/Sevilla_FC_logo.svg/1200px-Sevilla_FC_logo.svg.png",
    "Valencia": "https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Valenciacf.svg/1200px-Valenciacf.svg.png",
    "Girona": "https://upload.wikimedia.org/wikipedia/en/thumb/9/90/Girona_FC_logo.svg/1200px-Girona_FC_logo.svg.png"
}

SCORING = {"Normal": (0.5, 0.75, 1.0), "Doble": (1.0, 1.5, 2.0), "Esquizo": (1.0, 1.5, 3.0)}
CODIGO_INVITACION = "LIGA2026"

# --- 2. FUNCIONES DE APOYO ---
def get_logo(equipo):
    return LOGOS.get(equipo, "⚽")

def calcular_puntos(p_l, p_v, r_l, r_v, tipo="Normal"):
    p_ganador, p_diff, p_exacto = SCORING.get(tipo, SCORING["Normal"])
    if p_l == r_l and p_v == r_v: return p_exacto
    signo_p = (p_l > p_v) - (p_l < p_v)
    signo_r = (r_l > r_v) - (r_l < r_v)
    if signo_p == signo_r:
        if (p_l - p_v) == (r_l - r_v): return p_diff
        return p_ganador
    return 0.0

def color_celulas(val):
    if val == 0: color = '#ff4b4b' 
    elif val >= 1.5: color = '#00f2ff'
    elif val >= 1.0: color = '#2baf2b' 
    else: color = '#ffd700' 
    return f'background-color: {color}; color: black'

# --- 3. INICIO APP Y CONEXIÓN ---
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

# --- 5. CONTENIDO PRINCIPAL ---
else:
    c_head1, c_head2 = st.columns([6, 1])
    c_head1.title(f"Bienvenido, {st.session_state.user} 👋")
    if c_head2.button("Salir"):
        st.session_state.autenticado = False
        st.rerun()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ Mis Apuestas", "👀 Ver Otras", "📊 Ranking", "🏆 Detalles", "⚙️ Admin"])

    with tab1:
        if st.session_state.rol == "admin":
            st.info("💡 Eres Administrador. Gestiona la liga en la pestaña 'Admin'.")
        else:
            j_sel = st.selectbox("Elegir Jornada", list(JORNADAS.keys()), key="ap_j")
            df_r = leer_datos("Resultados")
            df_p_existentes = leer_datos("Predicciones")
            
            # Cargar mis datos previos para precarga
            mis_preds_hoy = pd.DataFrame()
            if not df_p_existentes.empty:
                mis_preds_hoy = df_p_existentes[(df_p_existentes['Usuario'] == st.session_state.user) & (df_p_existentes['Jornada'] == j_sel)]

            df_r_j = df_r[df_r['Jornada'] == j_sel] if not df_r.empty else pd.DataFrame()
            ahora = datetime.now()
            
            preds_a_enviar = []
            for i, (loc, vis) in enumerate(JORNADAS[j_sel]):
                match_name = f"{loc}-{vis}"
                bloqueado, tipo = False, "Normal"
                
                # Valores por defecto para precarga
                def_l, def_v, def_pub = 0, 0, False
                if not mis_preds_hoy.empty:
                    m_prev = mis_preds_hoy[mis_preds_hoy['Partido'] == match_name]
                    if not m_prev.empty:
                        def_l, def_v = int(m_prev.iloc[0]['P_L']), int(m_prev.iloc[0]['P_V'])
                        def_pub = True if m_prev.iloc[0]['Publica'] == "SI" else False

                # Bloqueo horario
                if not df_r_j.empty and match_name in df_r_j['Partido'].values:
                    info = df_r_j[df_r_j['Partido'] == match_name].iloc[0]
                    tipo = info['Tipo']
                    try:
                        limite = datetime.strptime(str(info['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                        if ahora > limite: bloqueado = True
                    except: pass

                # Interfaz de Partido con LOGOS
                st.markdown(f"#### {tipo} {'🔒' if bloqueado else '🔓'}")
                c_img1, c_in1, c_vs, c_in2, c_img2, c_chk = st.columns([1, 2, 0.5, 2, 1, 2])
                
                with c_img1: 
                    logo = get_logo(loc)
                    if logo.startswith("http"): st.image(logo, width=50)
                    else: st.write(logo)
                with c_in1: pl = st.number_input(f"{loc}", 0, value=def_l, key=f"l_{j_sel}_{i}", disabled=bloqueado)
                with c_vs: st.markdown("<br>VS", unsafe_allow_html=True)
                with c_in2: pv = st.number_input(f"{vis}", 0, value=def_v, key=f"v_{j_sel}_{i}", disabled=bloqueado)
                with c_img2:
                    logo = get_logo(vis)
                    if logo.startswith("http"): st.image(logo, width=50)
                    else: st.write(logo)
                with c_chk: pub = st.checkbox("Público", value=def_pub, key=f"pb_{j_sel}_{i}", disabled=bloqueado)
                
                preds_a_enviar.append({"Usuario": st.session_state.user, "Jornada": j_sel, "Partido": match_name, "P_L": pl, "P_V": pv, "Publica": "SI" if pub else "NO"})
                st.divider()

            if st.button("💾 Guardar Cambios"):
                df_all_p = leer_datos("Predicciones")
                df_all_p = df_all_p[~((df_all_p['Usuario'] == st.session_state.user) & (df_all_p['Jornada'] == j_sel))] if not df_all_p.empty else pd.DataFrame()
                conn.update(worksheet="Predicciones", data=pd.concat([df_all_p, pd.DataFrame(preds_a_enviar)], ignore_index=True))
                st.success("¡Datos guardados!")
                st.rerun()

    with tab2:
        st.header("🔍 Predicciones públicas")
        j_v = st.selectbox("Ver jornada:", list(JORNADAS.keys()), key="v_j_s")
        df_p_all = leer_datos("Predicciones")
        if not df_p_all.empty:
            p_publicas = df_p_all[(df_p_all['Jornada'] == j_v) & (df_p_all['Publica'] == "SI")]
            if p_publicas.empty: st.info("No hay datos públicos.")
            for u in p_publicas['Usuario'].unique():
                with st.expander(f"Apuestas de {u}"):
                    st.table(p_publicas[p_publicas['Usuario'] == u][['Partido', 'P_L', 'P_V']].rename(columns={'P_L': 'Local', 'P_V': 'Visitante'}))

    with tab3:
        st.header("📊 Clasificaciones")
        df_p = leer_datos("Predicciones"); df_r = leer_datos("Resultados"); df_u = leer_datos("Usuarios")
        if not df_r.empty and not df_p.empty:
            admins = df_u[df_u['Rol'] == 'admin']['Usuario'].tolist()
            res_dict = df_r.set_index(['Jornada', 'Partido']).to_dict('index')
            ranking = []
            for u in df_p['Usuario'].unique():
                if u in admins: continue
                u_p = df_p[df_p['Usuario'] == u]
                pj, pt = 0, 0
                for r in u_p.itertuples():
                    key = (r.Jornada, r.Partido)
                    if key in res_dict and str(res_dict[key].get('Finalizado')) == "SI":
                        pts = calcular_puntos(r.P_L, r.P_V, res_dict[key]['R_L'], res_dict[key]['R_V'], res_dict[key]['Tipo'])
                        pt += pts
                        if r.Jornada == j_sel: pj += pts
                ranking.append({"Usuario": u, f"Puntos {j_sel}": pj, "Puntos Totales": pt})
            
            df_final = pd.DataFrame(ranking)
            cr1, cr2 = st.columns(2)
            cr1.table(df_final[['Usuario', f"Puntos {j_sel}"]].sort_values(f"Puntos {j_sel}", ascending=False))
            cr2.table(df_final[['Usuario', 'Puntos Totales']].sort_values('Puntos Totales', ascending=False))

    with tab4:
        st.header(f"🏆 Detalle de Puntos: {j_sel}")
        df_p = leer_datos("Predicciones"); df_r = leer_datos("Resultados"); df_u = leer_datos("Usuarios")
        if not df_p.empty and not df_r.empty:
            admins = df_u[df_u['Rol'] == 'admin']['Usuario'].tolist()
            df_r_j = df_r[(df_r['Jornada'] == j_sel) & (df_r['Finalizado'] == "SI")]
            if df_r_j.empty: st.warning("Sin partidos finalizados.")
            else:
                usrs = [u for u in df_p['Usuario'].unique() if u not in admins]
                pts_matriz = pd.DataFrame(index=df_r_j['Partido'].unique(), columns=usrs)
                for part in pts_matriz.index:
                    rv = df_r_j[df_r_j['Partido'] == part].iloc[0]
                    for u in usrs:
                        u_p = df_p[(df_p['Usuario'] == u) & (df_p['Jornada'] == j_sel) & (df_p['Partido'] == part)]
                        pts_matriz.at[part, u] = calcular_puntos(u_p.iloc[0]['P_L'], u_p.iloc[0]['P_V'], rv['R_L'], rv['R_V'], rv['Tipo']) if not u_p.empty else 0
                st.dataframe(pts_matriz.style.applymap(color_celulas).format("{:.2f}"))

    with tab5:
        if st.session_state.rol == "admin":
            st.header("🛠️ Configuración Admin")
            j_adm = st.selectbox("Jornada", list(JORNADAS.keys()), key="adm_js")
            h_perm = [time(h, m) for h in range(12, 23) for m in [0, 15, 30, 45]]
            conf = []
            for i, (loc, vis) in enumerate(JORNADAS[j_adm]):
                st.write(f"--- {loc} vs {vis} ---")
                c_t, c_f, c_h, c_rl, c_rv, c_fi = st.columns([2, 2, 2, 1, 1, 2])
                tipo = c_t.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], key=f"at_{j_adm}_{i}")
                fec = c_f.date_input("Fecha", key=f"af_{j_adm}_{i}")
                hor = c_h.selectbox("Hora", h_perm, format_func=lambda x: x.strftime("%H:%M"), key=f"ah_{j_adm}_{i}", index=36)
                rl = c_rl.number_input("L", 0, key=f"arl_{j_adm}_{i}")
                rv = c_rv.number_input("V", 0, key=f"arv_{j_adm}_{i}")
                fin = c_fi.checkbox("Finalizado", key=f"afi_{j_adm}_{i}")
                conf.append({"Jornada": j_adm, "Partido": f"{loc}-{vis}", "Tipo": tipo, "R_L": rl, "R_V": rv, "Hora_Inicio": datetime.combine(fec, hor).strftime("%Y-%m-%d %H:%M:%S"), "Finalizado": "SI" if fin else "NO"})
            if st.button("🚀 Actualizar Todo"):
                old = leer_datos("Resultados")
                if not old.empty: old = old[old['Jornada'] != j_adm]
                conn.update(worksheet="Resultados", data=pd.concat([old, pd.DataFrame(conf)], ignore_index=True))
                st.success("¡Datos guardados!")
