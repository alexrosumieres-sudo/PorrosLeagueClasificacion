import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

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
    ],
    "Jornada 27": [
        ("Osasuna", "Mallorca"), ("Getafe", "Betis"), ("Levante", "Girona"),
        ("Atlético", "R. Sociedad"), ("Celta", "Real Madrid"), ("Villarreal", "Elche"),
        ("Athletic", "Barcelona"), ("Sevilla", "Rayo"), ("Valencia", "Alavés"),
        ("Espanyol", "Oviedo")
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

# --- FUNCIÓN DE LECTURA ROBUSTA (PARA EVITAR EL HTTPERROR) ---
def leer_datos(pestaña):
    try:
        # Forzamos ttl=0 para que siempre lea datos frescos y no use caché corrupta
        return conn.read(worksheet=pestaña, ttl=0)
    except Exception as e:
        # Si falla la lectura por nombre, intentamos lectura general
        st.error(f"Error al leer la pestaña {pestaña}. Revisa que el nombre sea exacto.")
        return pd.DataFrame()

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- LÓGICA DE ACCESO ---
if not st.session_state.autenticado:
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
                    # Convertimos a string por seguridad
                    user_db = df_u[(df_u['Usuario'].astype(str) == str(user_input)) & 
                                   (df_u['Password'].astype(str) == str(pass_input))]
                    if not user_db.empty:
                        st.session_state.autenticado = True
                        st.session_state.user = user_input
                        st.session_state.rol = user_db.iloc[0]['Rol']
                        st.rerun()
                    else:
                        st.error("❌ Datos incorrectos")
        
        else: # Registro
            cod_inv = st.text_input("Código de Invitación")
            if st.button("Crear Cuenta"):
                df_u = leer_datos("Usuarios")
                if cod_inv != CODIGO_INVITACION:
                    st.error("🚫 Código de invitación incorrecto")
                elif not user_input or not pass_input:
                    st.error("Rellena todos los campos")
                elif not df_u.empty and user_input in df_u['Usuario'].values:
                    st.warning("Ese usuario ya existe")
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

    tab1, tab2, tab3 = st.tabs(["✍️ Mis Apuestas", "📊 Clasificación", "⚙️ Admin"])

    with tab1:
        j_sel = st.selectbox("Elegir Jornada", list(JORNADAS.keys()))
        df_r = leer_datos("Resultados")
        df_r_j = df_r[df_r['Jornada'] == j_sel] if not df_r.empty else pd.DataFrame()
        
        st.write(f"### Tus predicciones para la {j_sel}")
        preds_actuales = []
        for i, (loc, vis) in enumerate(JORNADAS[j_sel]):
            match_name = f"{loc}-{vis}"
            tipo = "Normal"
            if not df_r_j.empty and match_name in df_r_j['Partido'].values:
                tipo = df_r_j[df_r_j['Partido'] == match_name]['Tipo'].values[0]
            
            st.markdown(f"**{loc} vs {vis}** ({tipo})")
            col_l, col_v = st.columns(2)
            pl = col_l.number_input(f"Goles {loc}", min_value=0, step=1, key=f"pl_{i}_{j_sel}")
            pv = col_v.number_input(f"Goles {vis}", min_value=0, step=1, key=f"pv_{i}_{j_sel}")
            preds_actuales.append({"Usuario": st.session_state.user, "Jornada": j_sel, "Partido": match_name, "P_L": pl, "P_V": pv})
            st.divider()

        if st.button("💾 Guardar Porra"):
            df_p = leer_datos("Predicciones")
            # Limpiar anteriores del usuario
            if not df_p.empty:
                df_p = df_p[~((df_p['Usuario'] == st.session_state.user) & (df_p['Jornada'] == j_sel))]
            df_p = pd.concat([df_p, pd.DataFrame(preds_actuales)], ignore_index=True)
            conn.update(worksheet="Predicciones", data=df_p)
            st.success("¡Predicciones enviadas!")

    with tab2:
        st.header("Ranking")
        df_p = leer_datos("Predicciones")
        df_r = leer_datos("Resultados")
        
        if df_r.empty or j_sel not in df_r['Jornada'].values:
            st.info("Esperando resultados del Admin...")
        else:
            df_p_j = df_p[df_p['Jornada'] == j_sel]
            df_r_j = df_r[df_r['Jornada'] == j_sel]
            puntos_list = []
            for user in df_p_j['Usuario'].unique():
                total = 0
                u_preds = df_p_j[df_p_j['Usuario'] == user]
                for row in u_preds.itertuples():
                    res_r = df_r_j[df_r_j['Partido'] == row.Partido]
                    if not res_r.empty:
                        total += calcular_puntos(row.P_L, row.P_V, res_r.iloc[0]['R_L'], res_r.iloc[0]['R_V'], res_r.iloc[0]['Tipo'])
                puntos_list.append({"Usuario": user, "Puntos": total})
            st.table(pd.DataFrame(puntos_list).sort_values("Puntos", ascending=False))

    with tab3:
        if st.session_state.rol == "admin":
            st.header("🛠️ Panel de Administración")
            j_admin = st.selectbox("Gestionar Jornada", list(JORNADAS.keys()), key="admin_j")
            config = []
            for i, (loc, vis) in enumerate(JORNADAS[j_admin]):
                st.write(f"**{loc} - {vis}**")
                c1, c2, c3 = st.columns(3)
                tipo = c1.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], key=f"t_{i}")
                rl = c2.number_input("Real L", min_value=0, step=1, key=f"rl_{i}")
                rv = c3.number_input("Real V", min_value=0, step=1, key=f"rv_{i}")
                config.append({"Jornada": j_admin, "Partido": f"{loc}-{vis}", "Tipo": tipo, "R_L": rl, "R_V": rv})
            
            if st.button("🚀 Publicar Resultados"):
                df_res_old = leer_datos("Resultados")
                if not df_res_old.empty:
                    df_res_old = df_res_old[df_res_old['Jornada'] != j_admin]
                df_new = pd.concat([df_res_old, pd.DataFrame(config)], ignore_index=True)
                conn.update(worksheet="Resultados", data=df_new)
                st.success("¡Resultados publicados!")
        else:
            st.error("Área restringida.")
