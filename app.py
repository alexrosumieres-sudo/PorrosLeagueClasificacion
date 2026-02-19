import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time

# --- CONFIGURACIÓN DE LAS JORNADAS (25 a 38) ---
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

# --- PUNTUACIONES ---
SCORING = {"Normal": (0.5, 0.75, 1.0), "Doble": (1.0, 1.5, 2.0), "Esquizo": (1.0, 1.5, 3.0)}
CODIGO_INVITACION = "LIGA2026"

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
    if val == 0: color = '#ff4b4b' # Rojo
    elif val >= 1.5: color = '#00f2ff' # Azul
    elif val >= 1.0: color = '#2baf2b' # Verde
    else: color = '#ffd700' # Amarillo
    return f'background-color: {color}; color: black'

st.set_page_config(page_title="Liga de Fútbol", page_icon="⚽", layout="wide")

# --- CONEXIÓN ---
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

# --- ACCESO ---
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

# --- CONTENIDO ---
else:
    c1, c2 = st.columns([6, 1])
    c1.title(f"Hola, {st.session_state.user} 👋")
    if c2.button("Salir"):
        st.session_state.autenticado = False
        st.rerun()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["✍️ Mis Apuestas", "👀 Ver Otras", "📊 Ranking", "🏆 Detalles", "⚙️ Admin"])

    with tab1:
        j_sel = st.selectbox("Elegir Jornada", list(JORNADAS.keys()))
        df_r = leer_datos("Resultados")
        df_r_j = df_r[df_r['Jornada'] == j_sel] if not df_r.empty else pd.DataFrame()
        ahora = datetime.now()
        
        preds_enviar = []
        for i, (loc, vis) in enumerate(JORNADAS[j_sel]):
            match_name = f"{loc}-{vis}"
            bloqueado, tipo = False, "Normal"
            if not df_r_j.empty and match_name in df_r_j['Partido'].values:
                info = df_r_j[df_r_j['Partido'] == match_name].iloc[0]
                tipo = info['Tipo']
                limite = datetime.strptime(str(info['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                if ahora > limite: bloqueado = True

            st.markdown(f"**{loc} vs {vis}** ({tipo})")
            col_l, col_v, col_pub = st.columns([2, 2, 2])
            pl = col_l.number_input(f"Goles {loc}", 0, key=f"pl_{i}_{j_sel}", disabled=bloqueado)
            pv = col_v.number_input(f"Goles {vis}", 0, key=f"pv_{i}_{j_sel}", disabled=bloqueado)
            pub = col_pub.checkbox("Hacer público", key=f"pub_{i}_{j_sel}", disabled=bloqueado)
            preds_enviar.append({"Usuario": st.session_state.user, "Jornada": j_sel, "Partido": match_name, "P_L": pl, "P_V": pv, "Publica": "SI" if pub else "NO"})

        if st.button("💾 Guardar Cambios"):
            df_p = leer_datos("Predicciones")
            df_p = df_p[~((df_p['Usuario'] == st.session_state.user) & (df_p['Jornada'] == j_sel))] if not df_p.empty else pd.DataFrame()
            conn.update(worksheet="Predicciones", data=pd.concat([df_p, pd.DataFrame(preds_enviar)], ignore_index=True))
            st.success("¡Guardado!")

    with tab2:
        st.header("🔍 Predicciones públicas")
        df_all_p = leer_datos("Predicciones")
        if not df_all_p.empty:
            p_j = df_all_p[(df_all_p['Jornada'] == j_sel) & (df_all_p['Publica'] == "SI")]
            if p_j.empty: st.info("Nada público todavía.")
            for u in p_j['Usuario'].unique():
                with st.expander(f"Apuestas de {u}"):
                    st.table(p_j[p_j['Usuario'] == u][['Partido', 'P_L', 'P_V']])

    with tab3:
        st.header("📊 Clasificaciones")
        df_p = leer_datos("Predicciones")
        df_r = leer_datos("Resultados")
        if not df_r.empty and not df_p.empty:
            res_dict = df_r.set_index(['Jornada', 'Partido']).to_dict('index')
            ranking = []
            for user in df_p['Usuario'].unique():
                u_p = df_p[df_p['Usuario'] == user]
                pj, pt = 0, 0
                for r in u_p.itertuples():
                    if (r.Jornada, r.Partido) in res_dict:
                        rd = res_dict[(r.Jornada, r.Partido)]
                        if str(rd.get('Finalizado')) == "SI":
                            pts = calcular_puntos(r.P_L, r.P_V, rd['R_L'], rd['R_V'], rd['Tipo'])
                            pt += pts
                            if r.Jornada == j_sel: pj += pts
                ranking.append({"Usuario": user, f"Puntos {j_sel}": pj, "Puntos Totales": pt})
            df_rank = pd.DataFrame(ranking)
            c_r1, c_r2 = st.columns(2)
            c_r1.subheader(f"Jornada")
            c_r1.table(df_rank[['Usuario', f"Puntos {j_sel}"]].sort_values(f"Puntos {j_sel}", ascending=False))
            c_r2.subheader("General")
            c_r2.table(df_rank[['Usuario', 'Puntos Totales']].sort_values('Puntos Totales', ascending=False))

    with tab4:
        st.header(f"⚽ Detalle de Puntos: {j_sel}")
        df_p = leer_datos("Predicciones"); df_r = leer_datos("Resultados")
        if not df_p.empty and not df_r.empty:
            df_r_j = df_r[(df_r['Jornada'] == j_sel) & (df_r['Finalizado'] == "SI")]
            if df_r_j.empty: st.warning("Sin partidos finalizados.")
            else:
                matriz = pd.DataFrame(index=df_r_j['Partido'].unique(), columns=df_p['Usuario'].unique())
                for p in matriz.index:
                    res = df_r_j[df_r_j['Partido'] == p].iloc[0]
                    for u in matriz.columns:
                        u_p = df_p[(df_p['Usuario'] == u) & (df_p['Jornada'] == j_sel) & (df_p['Partido'] == p)]
                        matriz.at[p, u] = calcular_puntos(u_p.iloc[0]['P_L'], u_p.iloc[0]['P_V'], res['R_L'], res['R_V'], res['Tipo']) if not u_p.empty else 0
                st.dataframe(matriz.style.applymap(color_celulas).format("{:.2f}"))

    with tab5:
        if st.session_state.rol == "admin":
            st.header("🛠️ Configuración Admin")
            j_adm = st.selectbox("Jornada", list(JORNADAS.keys()), key="adm_j")
            horas = [time(h, m) for h in range(12, 23) for m in [0, 15, 30, 45]]
            conf = []
            for i, (loc, vis) in enumerate(JORNADAS[j_adm]):
                st.write(f"--- {loc} vs {vis} ---")
                c_t, c_f, c_h, c_rl, c_rv, c_fi = st.columns([2, 2, 2, 1, 1, 2])
                tipo = c_t.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], key=f"at_{i}")
                fecha = c_f.date_input("Fecha", key=f"af_{i}")
                hora = c_h.selectbox("Hora", horas, format_func=lambda x: x.strftime("%H:%M"), key=f"ah_{i}", index=36)
                rl = c_rl.number_input("L", 0, key=f"arl_{i}")
                rv = c_rv.number_input("V", 0, key=f"arv_{i}")
                fin = c_fi.checkbox("Finalizado", key=f"afi_{i}")
                conf.append({"Jornada": j_adm, "Partido": f"{loc}-{vis}", "Tipo": tipo, "R_L": rl, "R_V": rv, "Hora_Inicio": datetime.combine(fecha, hora).strftime("%Y-%m-%d %H:%M:%S"), "Finalizado": "SI" if fin else "NO"})
            if st.button("🚀 Actualizar"):
                df_old = leer_datos("Resultados")
                if not df_old.empty: df_old = df_old[df_old['Jornada'] != j_adm]
                conn.update(worksheet="Resultados", data=pd.concat([df_old, pd.DataFrame(conf)], ignore_index=True))
                st.success("¡Datos guardados!")
