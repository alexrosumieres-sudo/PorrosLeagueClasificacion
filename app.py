import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time

# --- CONFIGURACIÓN DE LAS JORNADAS ---
JORNADAS = {
    "Jornada 25": [
        ("Athletic", "Elche"), ("R. Sociedad", "Oviedo"), ("Betis", "Rayo"),
        ("Osasuna", "Real Madrid"), ("Atlético", "Espanyol"), ("Getafe", "Sevilla"),
        ("Barcelona", "Levante"), ("Celta", "Mallorca"), ("Villarreal", "Valencia"),
        ("Alavés", "Girona")
    ],
    "Jornada 26": [
        ("Levante", "Alavés"), ("Rayo", "Athletic"), ("Barcelona", "Villarreal"),
        ("Mallorca", "R. Sociedad"), ("Oviedo", "Atlético"), ("Elche", "Espanyol"),
        ("Valencia", "Osasuna"), ("Betis", "Sevilla"), ("Girona", "Celta"),
        ("Real Madrid", "Getafe")
    ]
}

# --- CONFIGURACIÓN DE PUNTUACIONES ---
SCORING = {
    "Normal": (0.5, 0.75, 1.0),
    "Doble": (1.0, 1.5, 2.0),
    "Esquizo": (1.0, 1.5, 3.0)
}

CODIGO_INVITACION = "LIGA2026"

def calcular_puntos(p_l, p_v, r_l, r_v, tipo="Normal"):
    if pd.isna(r_l) or pd.isna(r_v): return 0
    p_ganador, p_diff, p_exacto = SCORING.get(tipo, SCORING["Normal"])
    if p_l == r_l and p_v == r_v: return p_exacto
    signo_p = (p_l > p_v) - (p_l < p_v)
    signo_r = (r_l > r_v) - (r_l < r_v)
    if signo_p == signo_r:
        if (p_l - p_v) == (r_l - r_v): return p_diff
        return p_ganador
    return 0.0

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Liga de Fútbol", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white;}
        .main-title {text-align: center; color: #1E1E1E;}
    </style>
""", unsafe_allow_html=True)

# CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos(pestaña):
    try:
        sheet_id = "1vFgccrCqmGrs9QfP8kxY_cESbRaJ_VxpsoAz-ZyL14E"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={pestaña}"
        return pd.read_csv(url)
    except Exception:
        return pd.DataFrame()

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- LÓGICA DE ACCESO ---
if not st.session_state.autenticado:
    # ... (Se mantiene igual que el anterior para login/registro)
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.markdown("<h1 class='main-title'>🏆 Porra League</h1>", unsafe_allow_html=True)
        modo = st.radio("Selecciona", ["Iniciar Sesión", "Registrarse"], horizontal=True)
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        
        if modo == "Iniciar Sesión":
            if st.button("Entrar"):
                df_u = leer_datos("Usuarios")
                if not df_u.empty:
                    user_db = df_u[(df_u['Usuario'].astype(str) == str(user_input)) & 
                                   (df_u['Password'].astype(str) == str(pass_input))]
                    if not user_db.empty:
                        st.session_state.autenticado = True
                        st.session_state.user = user_input
                        st.session_state.rol = user_db.iloc[0]['Rol']
                        st.rerun()
                    else:
                        st.error("❌ Datos incorrectos")
        
        else:
            cod_inv = st.text_input("Código de Invitación")
            if st.button("Crear Cuenta"):
                df_u = leer_datos("Usuarios")
                if cod_inv != CODIGO_INVITACION:
                    st.error("🚫 Código de invitación incorrecto")
                elif not user_input or not pass_input:
                    st.error("Rellena todos los campos")
                else:
                    nueva_fila = pd.DataFrame([{"Usuario": user_input, "Password": pass_input, "Rol": "user"}])
                    df_u_final = pd.concat([df_u, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Usuarios", data=df_u_final)
                    st.success("✅ ¡Registrado! Inicia sesión ahora.")

# --- APP PRINCIPAL ---
else:
    c1, c2 = st.columns([6, 1])
    c1.title(f"Hola, {st.session_state.user} 👋")
    if c2.button("Salir"):
        st.session_state.autenticado = False
        st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["✍️ Mis Apuestas", "👀 Ver Predicciones", "📊 Clasificación", "⚙️ Admin"])

    with tab1:
        j_sel = st.selectbox("Elegir Jornada", list(JORNADAS.keys()))
        df_r = leer_datos("Resultados")
        df_r_j = df_r[df_r['Jornada'] == j_sel] if not df_r.empty else pd.DataFrame()
        ahora = datetime.now()
        
        st.write(f"### Tus predicciones para la {j_sel}")
        
        preds_enviar = []
        for i, (loc, vis) in enumerate(JORNADAS[j_sel]):
            match_name = f"{loc}-{vis}"
            bloqueado = False
            tipo = "Normal"
            
            # Verificar si el partido ya empezó
            if not df_r_j.empty and match_name in df_r_j['Partido'].values:
                info_p = df_r_j[df_r_j['Partido'] == match_name].iloc[0]
                tipo = info_p['Tipo']
                if 'Hora_Inicio' in info_p and pd.notna(info_p['Hora_Inicio']):
                    hora_limite = datetime.strptime(str(info_p['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                    if ahora > hora_limite: bloqueado = True

            # Layout: Partido | Goles | Checkbox Público
            st.markdown(f"**{loc} vs {vis}** ({tipo})")
            col_l, col_v, col_pub = st.columns([2, 2, 2])
            
            with col_l:
                pl = st.number_input(f"Goles {loc}", 0, key=f"pl_{i}_{j_sel}", disabled=bloqueado)
            with col_v:
                pv = st.number_input(f"Goles {vis}", 0, key=f"pv_{i}_{j_sel}", disabled=bloqueado)
            with col_pub:
                publico = st.checkbox("Hacer público", key=f"pub_{i}_{j_sel}", disabled=bloqueado)
            
            preds_enviar.append({
                "Usuario": st.session_state.user, 
                "Jornada": j_sel, 
                "Partido": match_name, 
                "P_L": pl, 
                "P_V": pv, 
                "Publica": "SI" if publico else "NO"
            })
            st.divider()

        if st.button("💾 Guardar Cambios"):
            df_p = leer_datos("Predicciones")
            if not df_p.empty:
                # Borramos solo las predicciones del usuario para esta jornada antes de re-insertar
                df_p = df_p[~((df_p['Usuario'] == st.session_state.user) & (df_p['Jornada'] == j_sel))]
            df_p = pd.concat([df_p, pd.DataFrame(preds_actuales)], ignore_index=True)
            conn.update(worksheet="Predicciones", data=df_p)
            st.success("¡Tus apuestas se han guardado!")

    with tab2:
        st.header("🔍 Predicciones públicas de la comunidad")
        j_view = st.selectbox("Ver jornada:", list(JORNADAS.keys()), key="view_j")
        df_all_p = leer_datos("Predicciones")
        
        if not df_all_p.empty:
            # Filtrar solo las que son públicas ("SI")
            ver_publicas = df_all_p[(df_all_p['Jornada'] == j_view) & (df_all_p['Publica'] == "SI")]
            
            if ver_publicas.empty:
                st.info("No hay predicciones públicas compartidas para esta jornada.")
            else:
                # Agrupamos por usuario para mostrarlo mejor
                for user in ver_publicas['Usuario'].unique():
                    with st.expander(f"Predicciones de {user}"):
                        user_p = ver_publicas[ver_publicas['Usuario'] == user]
                        # Creamos una tabla pequeñita para cada usuario
                        tabla_user = user_p[['Partido', 'P_L', 'P_V']].copy()
                        tabla_user.columns = ['Partido', 'Local', 'Visitante']
                        st.table(tabla_user)
        else:
            st.write("Aún no hay predicciones en el sistema.")

    with tab3:
        # ... (Se mantiene igual que el anterior para el Ranking de la jornada)
        st.header("Ranking de la Jornada")
        df_p = leer_datos("Predicciones")
        df_r = leer_datos("Resultados")
        if not df_r.empty and j_sel in df_r['Jornada'].values:
            df_p_j = df_p[df_p['Jornada'] == j_sel] if not df_p.empty else pd.DataFrame()
            df_r_j = df_r[df_r['Jornada'] == j_sel]
            
            puntos_list = []
            if not df_p_j.empty:
                for user in df_p_j['Usuario'].unique():
                    total = 0
                    u_preds = df_p_j[df_p_j['Usuario'] == user]
                    for row in u_preds.itertuples():
                        res_r = df_r_j[df_r_j['Partido'] == row.Partido]
                        if not res_r.empty:
                            total += calcular_puntos(row.P_L, row.P_V, res_r.iloc[0]['R_L'], res_r.iloc[0]['R_V'], res_r.iloc[0]['Tipo'])
                    puntos_list.append({"Usuario": user, "Puntos": total})
                st.table(pd.DataFrame(puntos_list).sort_values("Puntos", ascending=False))

    with tab4:
        # ... (Se mantiene igual que el anterior para el Panel de Admin con selectbox de horas)
        if st.session_state.rol == "admin":
            st.header("🛠️ Configuración Admin")
            j_admin = st.selectbox("Gestionar Jornada", list(JORNADAS.keys()), key="admin_j")
            
            horas_permitidas = [time(h, m) for h in range(12, 23) for m in [0, 15, 30, 45]]
            config = []
            for i, (loc, vis) in enumerate(JORNADAS[j_admin]):
                st.write(f"--- {loc} vs {vis} ---")
                c_t, c_f, c_h, c_rl, col_rv = st.columns(5)
                tipo = c_t.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], key=f"at_{i}")
                fecha = c_f.date_input("Fecha", key=f"af_{i}")
                hora = c_h.selectbox("Hora", horas_permitidas, format_func=lambda x: x.strftime("%H:%M"), key=f"ah_{i}", index=36)
                rl = c_rl.number_input("R. L", 0, key=f"arl_{i}")
                rv = col_rv.number_input("R. V", 0, key=f"arv_{i}")
                
                dt_inicio = datetime.combine(fecha, hora).strftime("%Y-%m-%d %H:%M:%S")
                config.append({"Jornada": j_admin, "Partido": f"{loc}-{vis}", "Tipo": tipo, "R_L": rl, "R_V": rv, "Hora_Inicio": dt_inicio})
            
            if st.button("🚀 Actualizar Resultados"):
                df_res_old = leer_datos("Resultados")
                if not df_res_old.empty:
                    df_res_old = df_res_old[df_res_old['Jornada'] != j_admin]
                df_new = pd.concat([df_res_old, pd.DataFrame(config)], ignore_index=True)
                conn.update(worksheet="Resultados", data=df_new)
                st.success("¡Datos actualizados!")
