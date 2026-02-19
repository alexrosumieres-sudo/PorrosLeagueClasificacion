import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

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

# --- INICIO DE APP ---
st.set_page_config(page_title="Liga Pro", page_icon="⚽", layout="centered")

# Ocultar la barra lateral por defecto con CSS
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%;}
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- LÓGICA DE ACCESO (CENTRO DE PANTALLA) ---
if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Acceso a la Liga")
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            df_users = conn.read(worksheet="Usuarios")
            user_db = df_users[(df_users['Usuario'] == user_input) & (df_users['Password'] == str(pass_input))]
            if not user_db.empty:
                st.session_state.autenticado = True
                st.session_state.user = user_input
                st.session_state.rol = user_db.iloc[0]['Rol']
                st.rerun()
            else:
                st.error("⚠️ Usuario o contraseña incorrectos")
else:
    # --- APP UNA VEZ LOGUEADO ---
    st.title(f"⚽ ¡Bienvenido, {st.session_state.user}!")
    
    # Botón de cerrar sesión arriba a la derecha
    c1, c2 = st.columns([7, 1])
    if c2.button("Salir"):
        st.session_state.autenticado = False
        st.rerun()

    tab1, tab2, tab3 = st.tabs(["✍️ Mis Apuestas", "📊 Clasificación", "🛠️ Admin"])

    with tab1:
        jornada_sel = st.selectbox("Selecciona la Jornada", list(JORNADAS.keys()))
        partidos = JORNADAS[jornada_sel]
        df_r = conn.read(worksheet="Resultados")
        df_r_j = df_r[df_r['Jornada'] == jornada_sel]
        
        st.divider()
        preds_actuales = []
        for i, (loc, vis) in enumerate(partidos):
            match_name = f"{loc}-{vis}"
            tipo_row = df_r_j[df_r_j['Partido'] == match_name]
            tipo_p = tipo_row.iloc[0]['Tipo'] if not tipo_row.empty else "Normal"
            
            # Etiqueta de color según tipo
            color = "blue" if tipo_p == "Doble" else ("red" if tipo_p == "Esquizo" else "gray")
            st.markdown(f"**{loc} vs {vis}** :{color}[({tipo_p})]")
            
            col_l, col_v = st.columns(2)
            pl = col_l.number_input(f"Goles {loc}", min_value=0, step=1, key=f"l_{jornada_sel}_{i}")
            pv = col_v.number_input(f"Goles {vis}", min_value=0, step=1, key=f"v_{jornada_sel}_{i}")
            preds_actuales.append({"Usuario": st.session_state.user, "Jornada": jornada_sel, "Partido": match_name, "P_L": pl, "P_V": pv})
            st.divider()

        if st.button("💾 Guardar mis predicciones"):
            df_p = conn.read(worksheet="Predicciones")
            df_final = df_p[~((df_p['Usuario'] == st.session_state.user) & (df_p['Jornada'] == jornada_sel))]
            df_final = pd.concat([df_final, pd.DataFrame(preds_actuales)], ignore_index=True)
            conn.update(worksheet="Predicciones", data=df_final)
            st.success("✅ ¡Guardado correctamente!")

    with tab2:
        st.header("Ranking de la Jornada")
        # Aquí se aplica la lógica de puntos sumando el 'tipo' de partido
        # (Lógica simplificada para visualización)
        st.info("La clasificación se actualiza cuando el Admin sube los resultados.")

    with tab3:
        if st.session_state.rol == "admin":
            st.header("🛠️ Panel de Control")
            j_admin = st.selectbox("Configurar Jornada:", list(JORNADAS.keys()), key="j_admin")
            
            config_partidos = []
            for i, (loc, vis) in enumerate(JORNADAS[j_admin]):
                st.write(f"--- {loc} vs {vis} ---")
                c1, c2, c3 = st.columns(3)
                tipo = c1.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], key=f"t_{i}")
                rl = c2.number_input("R. Local", min_value=0, step=1, key=f"rl_{i}")
                rv = c3.number_input("R. Visitante", min_value=0, step=1, key=f"rv_{i}")
                config_partidos.append({"Jornada": j_admin, "Partido": f"{loc}-{vis}", "Tipo": tipo, "R_L": rl, "R_V": rv})
            
            if st.button("🚀 Publicar Resultados"):
                df_res_all = conn.read(worksheet="Resultados")
                df_res_all = df_res_all[df_res_all['Jornada'] != j_admin]
                df_res_all = pd.concat([df_res_all, pd.DataFrame(config_partidos)], ignore_index=True)
                conn.update(worksheet="Resultados", data=df_res_all)
                st.success("Resultados publicados.")
        else:
            st.warning("🔒 Esta sección es solo para administradores.")
