import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURACIÓN DE PUNTUACIONES ---
# Sistema: (Ganador, Diferencia, Exacto)
SCORING = {
    "Normal": (0.5, 0.75, 1.0),
    "Doble": (1.0, 1.5, 2.0),
    "Esquizo": (1.0, 1.5, 3.0)
}

# --- LÓGICA DE CÁLCULO ---
def calcular_puntos(p_l, p_v, r_l, r_v, tipo="Normal"):
    if pd.isna(r_l) or pd.isna(r_v): return 0
    
    p_ganador, p_diff, p_exacto = SCORING.get(tipo, SCORING["Normal"])

    # 1. Resultado exacto
    if p_l == r_l and p_v == r_v:
        return p_exacto
    
    # Signos (1: local, 0: empate, -1: visitante)
    signo_p = (p_l > p_v) - (p_l < p_v)
    signo_r = (r_l > r_v) - (r_l < r_v)
    
    if signo_p == signo_r:
        # 2. Diferencia de goles
        if (p_l - p_v) == (r_l - r_v):
            return p_diff
        # 3. Acierto simple
        return p_ganador
            
    return 0.0

# --- CONEXIÓN Y LOGIN ---
st.set_page_config(page_title="Liga Pro", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# Sidebar de Login
with st.sidebar:
    st.title("🔐 Acceso")
    if not st.session_state.autenticado:
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
                st.error("Usuario o contraseña incorrectos")
    else:
        st.write(f"Bienvenido, **{st.session_state.user}**")
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

# --- CONTENIDO PRINCIPAL ---
if st.session_state.autenticado:
    # (Aquí definimos las JORNADAS como en el código anterior...)
    # [Insertar aquí el diccionario JORNADAS del mensaje anterior]

    tab1, tab2, tab3 = st.tabs(["✍️ Mis Apuestas", "📊 Clasificación", "🛠️ Panel Admin"])

    # --- TAB 1: APUESTAS (Solo usuarios/admin) ---
    with tab1:
        jornada_sel = st.selectbox("Jornada", list(JORNADAS.keys()))
        partidos = JORNADAS[jornada_sel]
        df_r = conn.read(worksheet="Resultados")
        df_r_j = df_r[df_r['Jornada'] == jornada_sel]
        
        st.info("💡 Fíjate en el tipo de partido para saber cuánto puntúa.")
        
        preds_actuales = []
        for i, (loc, vis) in enumerate(partidos):
            match_name = f"{loc}-{vis}"
            # Ver qué tipo de partido es según el Admin
            tipo_row = df_r_j[df_r_j['Partido'] == match_name]
            tipo_p = tipo_row.iloc[0]['Tipo'] if not tipo_row.empty else "Normal"
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            col1.write(f"**{loc} vs {vis}**")
            pl = col2.number_input("L", min_value=0, step=1, key=f"l_{i}")
            pv = col3.number_input("V", min_value=0, step=1, key=f"v_{i}")
            col4.caption(f"Tipo: {tipo_p}")
            preds_actuales.append({"Usuario": st.session_state.user, "Jornada": jornada_sel, "Partido": match_name, "P_L": pl, "P_V": pv})

        if st.button("Guardar mi Porra"):
            df_p = conn.read(worksheet="Predicciones")
            df_final = df_p[~((df_p['Usuario'] == st.session_state.user) & (df_p['Jornada'] == jornada_sel))]
            df_final = pd.concat([df_final, pd.DataFrame(preds_actuales)], ignore_index=True)
            conn.update(worksheet="Predicciones", data=df_final)
            st.success("¡Apuestas guardadas!")

    # --- TAB 3: ADMIN (Solo Rol == 'admin') ---
    with tab3:
        if st.session_state.rol == "admin":
            st.header("Configuración de Jornada")
            j_admin = st.selectbox("Configurar Jornada:", list(JORNADAS.keys()), key="j_admin")
            
            config_partidos = []
            for i, (loc, vis) in enumerate(JORNADAS[j_admin]):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                col1.write(f"{loc}-{vis}")
                tipo = col2.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], key=f"tipo_{i}")
                rl = col3.number_input("Real L", min_value=0, step=1, key=f"rl_{i}")
                rv = col4.number_input("Real V", min_value=0, step=1, key=f"rv_{i}")
                config_partidos.append({"Jornada": j_admin, "Partido": f"{loc}-{vis}", "Tipo": tipo, "R_L": rl, "R_V": rv})
            
            if st.button("Publicar Resultados y Tipos"):
                df_res_all = conn.read(worksheet="Resultados")
                df_res_all = df_res_all[df_res_all['Jornada'] != j_admin]
                df_res_all = pd.concat([df_res_all, pd.DataFrame(config_partidos)], ignore_index=True)
                conn.update(worksheet="Resultados", data=df_res_all)
                st.success("Jornada actualizada para todos.")
        else:
            st.error("No tienes permisos de administrador.")

    # (El TAB 2 de Clasificación usaría la misma lógica que el código anterior 
    # pero pasando el 'tipo' a la función calcular_puntos)
