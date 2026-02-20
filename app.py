import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time
import os
import plotly.express as px

# --- 1. CONFIGURACIÓN ---
PERFILES_DIR = "perfiles/" # Carpeta para las fotos de los usuarios

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

# --- 2. FUNCIONES ---
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
    if df_usuario.empty: return "Novato 🐣", "Sin datos.", 0.0
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
    if pct_locuras > 0.15: return "EL VISIONARIO / ESQUIZO 🔮", f"Apuesta por el débil ({locuras} veces).", riesgo
    if avg_goles > 3.4: return "BUSCADOR DE PLENOS 🤪", "Busca el ataque total.", riesgo
    if avg_goles < 2.1: return "CONSERVADOR / AMARRETE 🛡️", "Fiel al 1-0.", riesgo
    return "ESTRATEGA ⚖️", "Apuesta con lógica.", riesgo

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
    c_h1, c_h2 = st.columns([6, 1])
    c_h1.title(f"Hola, {st.session_state.user} 👋")
    if c_h2.button("Salir"):
        st.session_state.autenticado = False
        st.rerun()

    j_global = st.selectbox("📅 Seleccionar Jornada:", list(JORNADAS.keys()), key="global_j")
    st.divider()

    tabs = st.tabs(["✍️ Apuestas", "👀 Otros", "📊 Clasificación", "🏆 Detalles", "🔮 Simulador", "⚙️ Admin"])

    df_r_all = leer_datos("Resultados")
    df_p_all = leer_datos("Predicciones")
    df_u_all = leer_datos("Usuarios")
    df_base = leer_datos("PuntosBase")
    df_perfiles = leer_datos("ImagenesPerfil")

    with tabs[2]: # Clasificación
        if not df_r_all.empty and not df_p_all.empty:
            admins = df_u_all[df_u_all['Rol'] == 'admin']['Usuario'].tolist()
            res_dict = df_r_all.set_index(['Jornada', 'Partido']).to_dict('index')
            jornadas_fin = sorted(df_r_all[df_r_all['Finalizado'] == "SI"]['Jornada'].unique())
            usuarios_jug = [u for u in df_p_all['Usuario'].unique() if u not in admins]
            
            # (Lógica de Ranking igual a la anterior...)
            historia = []
            for j_prog in jornadas_fin:
                temp = []
                for u in usuarios_jug:
                    pts_base = 0.0
                    if not df_base.empty:
                        m_b = df_base[df_base['Usuario'] == u]
                        if not m_b.empty: pts_base = float(m_b.iloc[0]['Puntos'])
                    pts_acum = pts_base
                    for r in df_p_all[df_p_all['Usuario'] == u].itertuples():
                        if r.Jornada in jornadas_fin[:jornadas_fin.index(j_prog)+1]:
                            k = (r.Jornada, r.Partido)
                            if k in res_dict and str(res_dict[k].get('Finalizado')) == "SI":
                                pts_acum += calcular_puntos(r.P_L, r.P_V, res_dict[k]['R_L'], res_dict[k]['R_V'], res_dict[k]['Tipo'])
                    temp.append({"Usuario": u, "Puntos": pts_acum})
                df_temp = pd.DataFrame(temp).sort_values("Puntos", ascending=False)
                df_temp['Posicion'] = range(1, len(df_temp) + 1)
                for row in df_temp.itertuples(): historia.append({"Jornada": j_prog, "Usuario": row.Usuario, "Posicion": row.Posicion, "Puntos": row.Puntos})
            
            if historia:
                df_hist = pd.DataFrame(historia)
                fig = px.line(df_hist, x="Jornada", y="Posicion", color="Usuario", markers=True)
                fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.subheader("👤 Perfiles")
            foto_dict = df_perfiles.set_index('Usuario')['ImagenPath'].to_dict() if not df_perfiles.empty else {}
            cols_p = st.columns(3)
            for idx, u in enumerate(usuarios_jug):
                nom_p, desc_p, riesgo = obtener_perfil_apostador(df_p_all[df_p_all['Usuario'] == u])
                with cols_p[idx % 3]:
                    c_f1, c_f2 = st.columns([1, 2])
                    with c_f1:
                        f_path = foto_dict.get(u)
                        if f_path and os.path.exists(f_path): st.image(f_path, width=80)
                        else: st.markdown("👤")
                    with c_f2:
                        st.markdown(f"**{u}**")
                        st.progress(min(riesgo, 1.0))
                    st.caption(nom_p)
                    st.info(desc_p)

    with tabs[4]: # Simulador
        st.header("🔮 Simulador")
        usr_sim = st.selectbox("Simular según:", [u for u in df_p_all['Usuario'].unique() if u not in df_u_all[df_u_all['Rol'] == 'admin']['Usuario'].tolist()])
        if st.button("🚀 Simular"):
            clasif = PUNTOS_LALIGA_BASE.copy() # Iniciamos con los puntos de la J24
            for p in df_p_all[df_p_all['Usuario'] == usr_sim].itertuples():
                try:
                    t_l, t_v = p.Partido.split('-')
                    if p.P_L > p.P_V: clasif[t_l] += 3
                    elif p.P_V > p.P_L: clasif[t_v] += 3
                    else: clasif[t_l] += 1; clasif[t_v] += 1
                except: continue
            st.table(pd.DataFrame(list(clasif.items()), columns=['Equipo', 'Pts']).sort_values('Pts', ascending=False))

    with tabs[5]: # Admin
        if st.session_state.rol == "admin":
            st.header("🛠️ Panel Admin")
            adm_tabs = st.tabs(["⭐ Puntos Base", "📸 Avatares", "⚽ Resultados"])
            
            with adm_tabs[0]: # Puntos Base
                base_upd = []
                for u in [usr for usr in df_u_all['Usuario'].unique() if usr not in df_u_all[df_u_all['Rol'] == 'admin']['Usuario'].tolist()]:
                    val = st.number_input(f"Base {u}", key=f"base_{u}")
                    base_upd.append({"Usuario": u, "Puntos": val})
                if st.button("Guardar Bases"): conn.update(worksheet="PuntosBase", data=pd.DataFrame(base_upd))

            with adm_tabs[1]: # Avatares
                st.subheader("Asociar fotos de perfil")
                if os.path.exists(PERFILES_DIR):
                    fotos = os.listdir(PERFILES_DIR)
                    perfil_data = []
                    for u in [usr for usr in df_u_all['Usuario'].unique() if usr not in df_u_all[df_u_all['Rol'] == 'admin']['Usuario'].tolist()]:
                        f_sel = st.selectbox(f"Imagen para {u}", ["Ninguna"] + fotos, key=f"img_{u}")
                        perfil_data.append({"Usuario": u, "ImagenPath": f"{PERFILES_DIR}{f_sel}" if f_sel != "Ninguna" else ""})
                    if st.button("Guardar Avatares"): conn.update(worksheet="ImagenesPerfil", data=pd.DataFrame(perfil_data))
                else: st.error(f"⚠️ La carpeta '{PERFILES_DIR}' no existe en el repositorio.")

            with adm_tabs[2]: # Resultados
                # (Lógica de resultados igual...)
                st.info("Introduce aquí los resultados finales de los partidos.")
        else: st.error("Acceso solo para administradores.")
