import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time
import os
import plotly.express as px
import random
import itertools
import pytz
import gspread
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURACIONES GENERALES ---
PERFILES_DIR = "perfiles/"
LOGOS_DIR = "logos/"

NIVEL_EQUIPOS = {
    "Real Madrid": 1, "Barcelona": 1, "Villarreal": 1, "Atlético": 1,
    "Betis": 2, "Espanyol": 2, "Celta": 2, "R. Sociedad": 2, "Athletic": 2,
    "Osasuna": 3, "Getafe": 3, "Girona": 3, "Sevilla": 3, "Alavés": 3, "Valencia": 3, "Elche": 3, "Rayo": 3,
    "Mallorca": 4, "Levante": 4, "Oviedo": 4
}

# Datos oficiales tras la Jornada 24
STATS_LALIGA_BASE = {
    "Real Madrid": {"PJ": 24, "V": 19, "E": 3, "D": 2, "GF": 53, "GC": 19, "Pts": 60},
    "Barcelona": {"PJ": 24, "V": 19, "E": 1, "D": 4, "GF": 64, "GC": 25, "Pts": 58},
    "Villarreal": {"PJ": 24, "V": 15, "E": 3, "D": 6, "GF": 45, "GC": 26, "Pts": 48},
    "Atlético": {"PJ": 24, "V": 13, "E": 6, "D": 5, "GF": 38, "GC": 21, "Pts": 45},
    "Betis": {"PJ": 24, "V": 11, "E": 8, "D": 5, "GF": 39, "GC": 29, "Pts": 41},
    "Espanyol": {"PJ": 24, "V": 10, "E": 5, "D": 9, "GF": 29, "GC": 33, "Pts": 35},
    "Celta": {"PJ": 24, "V": 8, "E": 10, "D": 6, "GF": 32, "GC": 27, "Pts": 34},
    "R. Sociedad": {"PJ": 24, "V": 8, "E": 7, "D": 9, "GF": 34, "GC": 35, "Pts": 31},
    "Athletic": {"PJ": 24, "V": 9, "E": 4, "D": 11, "GF": 27, "GC": 34, "Pts": 31},
    "Osasuna": {"PJ": 24, "V": 8, "E": 6, "D": 10, "GF": 28, "GC": 28, "Pts": 30},
    "Getafe": {"PJ": 24, "V": 8, "E": 5, "D": 11, "GF": 20, "GC": 28, "Pts": 29},
    "Girona": {"PJ": 24, "V": 7, "E": 8, "D": 9, "GF": 24, "GC": 38, "Pts": 29},
    "Sevilla": {"PJ": 24, "V": 7, "E": 5, "D": 12, "GF": 31, "GC": 39, "Pts": 26},
    "Alavés": {"PJ": 24, "V": 7, "E": 5, "D": 12, "GF": 21, "GC": 30, "Pts": 26},
    "Valencia": {"PJ": 24, "V": 6, "E": 8, "D": 10, "GF": 25, "GC": 37, "Pts": 26},
    "Elche": {"PJ": 24, "V": 5, "E": 10, "D": 9, "GF": 31, "GC": 35, "Pts": 25},
    "Rayo": {"PJ": 23, "V": 6, "E": 7, "D": 10, "GF": 21, "GC": 30, "Pts": 25},
    "Mallorca": {"PJ": 24, "V": 6, "E": 6, "D": 12, "GF": 29, "GC": 39, "Pts": 24},
    "Levante": {"PJ": 24, "V": 4, "E": 6, "D": 14, "GF": 26, "GC": 41, "Pts": 18},
    "Oviedo": {"PJ": 23, "V": 3, "E": 7, "D": 13, "GF": 13, "GC": 36, "Pts": 16},
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

# --- FRASES MÍTICAS ---
FRASES_POR_PUESTO = {
    1: [
        ("Ganar, ganar, ganar y volver a ganar.", "Luis Aragonés"),
        ("Yo soy el mejor.", "Cristiano Ronaldo"),
        ("El éxito no es un accidente.", "Pelé"),
        ("Cuando eres el mejor, no necesitas decirlo.", "Zlatan Ibrahimović"),
        ("Cuanto más difícil es la victoria, mayor es la felicidad.", "Pelé"),
        ("I am the Special One.", "José Mourinho"),
        ("Yo no busco los récords, los récords me buscan a mí.", "Cristiano Ronaldo"),
        ("Si hubiera querido un trabajo fácil, me habría quedado en el Oporto.", "José Mourinho"),
        ("Zlatan no hace audiciones.", "Zlatan Ibrahimović"),
        ("Vuestra envidia es mi motor.", "Cristiano Ronaldo"),
        ("¿Presión? Presión es la que tienen los padres que no pueden dar de comer a sus hijos. Esto es fútbol.", "José Mourinho"),
        ("No digo que sea el mejor entrenador del mundo, pero no creo que haya nadie mejor que yo.", "José Mourinho"),
        ("Vuestro odio me hace imparable.", "Cristiano Ronaldo"),
        ("Ganar no es lo más importante, es lo único. Ser segundo no vale.", "Carlos Bilardo"),
        ("El fútbol es un deporte simple en el que a algunos les gusta hablar… a mí me encanta ganar.", "Fabio Capello"),
        ("No me gusta perder a nada, siempre trato de ganar.", "Lionel Messi"),
        ("Las finales no se juegan, se ganan.", "Luis Aragonés"),
        ("Moriré con 90 años metiendo la polla en la boca de una puta y siendo feliz", "Lagarto Putero")
    ],
    2: [
        ("Perder una final es lo peor que hay.", "Lionel Messi"),
        ("Estuvimos cerca.", "Sergio Ramos"),
        ("Prefiero perder un partido que perder mi pasión.", "Zinedine Zidane"),
        ("El fútbol siempre da otra oportunidad.", "Diego Simeone"),
        ("A lo mejor me tienen envidia porque soy muy bueno.", "Cristiano Ronaldo"),
        ("Ser segundo es ser el primero de los perdedores.", "Ayrton Senna"),
        ("El VAR nos tiene manía.", ""),
        ("Merecimos ganar, pero el fútbol no es justicia, es gol.", "Unai Emery"),
        ("Jugamos como nunca, pero nos faltó la suerte del campeón.", "Xavi Hernández"),
        ("Nos vamos con la cara alta, pero con las manos vacías.", "Sergio Ramos"),
        ("Si perdemos seremos los mejores, si ganamos seremos eternos.", "Pep Guardiola"),
        ("Perdimos porque no ganamos.", "Ronaldo Nazário"),
        ("Reconocer la derrota es la primera etapa de la victoria.", "Vittorio Pozzo"),
        ("Las victorias son de todos y las derrotas solo de uno: yo.", "José Mourinho"),
        ("El éxito sin honor es un fracaso.", "Vicente del Bosque"),
        ("Prefiero perder un partido por nueve goles que nueve partidos por un gol.", "Vujadin Boškov")
    ],
    3: [
        ("Predicción a predicción.", "Diego Simeone"),
        ("El fútbol es un juego de errores.", "Johan Cruyff"),
        ("Siempre positivo, nunca negativo.", "Louis van Gaal"),
        ("Disfruten lo votado.", "Diego Simeone"),
        ("El fútbol siempre es el mañana.", "Diego Simeone"),
        ("No ganan siempre los buenos, ganan los que luchan.", "Diego Simeone"),
        ("Jugar al fútbol es muy sencillo, pero jugar un fútbol sencillo es lo más difícil que hay.", "Johan Cruyff"),
        ("El fútbol es lo más importante de lo menos importante.", "Jorge Valdano"),
        ("El secreto de un buen equipo está en el orden.", "Pep Guardiola"),
        ("Ningún jugador es tan bueno como todos juntos.", "Alfredo Di Stéfano"),
        ("Ni ahora somos el Leverkusen ni antes éramos la última mierda que cagó Pilatos", "Don Manolo Preciado")
    ],
    4: [
        ("El fútbol es así.", "Vujadin Boškov"),
        ("Hay que seguir trabajando.", "Carlo Ancelotti"),
        ("Esto es muy largo.", "Pep Guardiola"),
        ("Estoy muy feliz.", "Cristiano Ronaldo"),
        ("Mi mayor logro fue quedar cuarto.", "Arsène Wenger"),
        ("Firmaba este puesto al principio de la liga.", ""),
        ("Puntuar fuera de casa siempre es bueno.", "Entrenador amarrategui"),
        ("Ni frío ni calor.", "Anónimo"),
        ("Perdonaré que no acierten, pero nunca que no se esfuercen.", "Pep Guardiola"),
        ("Lo que te hace crecer es la derrota.", "Pep Guardiola"),
        ("El talento depende de la inspiración, pero el esfuerzo depende de cada uno.", "Pep Guardiola"),
        ("Hay que ganar con un fútbol espectacular.", "Carlo Ancelotti"),
        ("Hay que tener autocrítica para seguir ganando.", "Marcelo Bielsa"),
        ("Valorad lo que tenéis, nunca sabes cuándo llega tu momento.", "Tito Vilanova"),
        ("Ni ahora somos el Leverkusen ni antes éramos la última mierda que cagó Pilatos", "Don Manolo Preciado")
    ],
    5: [
        ("Un partido dura 90 minutos.", "Sepp Herberger"),
        ("Sin sufrimiento no hay gloria.", "José Mourinho"),
        ("El fútbol es estado de ánimo.", "Jorge Valdano"),
        ("¿Por qué?", "José Mourinho"),
        ("Felicidades por vuestro título de posesión.", "José Mourinho"),
        ("A este paso, no vamos ni a la Intertoto.", ""),
        ("Este equipo tiene menos gol que el coche de los Picapiedra.", "Manolo Preciado"),
        ("Ni fu, ni fa.", "Luis Aragonés"),
        ("En el fútbol, como en la vida, hay que aprender de las derrotas.", "Iván Zamorano"),
        ("El fútbol no perdona. Hay que ser el mejor todos los días.", "Luís Figo"),
        ("Lo que te hace crecer es la derrota, el error.", "Pep Guardiola"),
        ("Si no tienes suerte y gente que te ayude, nunca llegarás a ser el mejor.", "Zinedine Zidane"),
        ("El fútbol es así, igual que la vida, te da sorpresas.", "Luis Enrique"),
        ("Si perdemos seguiremos siendo el mejor equipo del mundo.", "Pep Guardiola")
    ],
    6: [
        ("Prefiero no hablar.", "José Mourinho"),
        ("Hay que levantarse.", "Cristiano Ronaldo"),
        ("Esto es fútbol.", "Pep Guardiola"),
        ("Es una situación de mierda.", "Joaquín"),
        ("A este equipo le falta alma.", "Guti"),
        ("Estamos tocando fondo.", "Lionel Messi"),
        ("Nos han faltado 11 jugadores y el entrenador.", "{usuario}"),
        ("Si no puedes ganar, asegúrate de no perder... y ni eso hemos hecho.", "Johan Cruyff"),
        ("Hay quien ríe después de una victoria, para mí no hay tiempo para festejar los éxitos.", "José Mourinho"),
        ("El entrenador tiene que pensar en todo.", "Diego Simeone"),
        ("Hay que levantarse tras no haber hecho bien las cosas y esforzarse para hacerlo mejor.", "Pep Guardiola"),
        ("El equipo es como un ejército, hay que dejarse la vida para ganar.", "Louis van Gaal"),
        ("Si tú tienes el balón, el rival no la tiene.", "Johan Cruyff"),
        ("El día que no disfrute en el campo, voy a dejar el fútbol.", "Lionel Messi")
    ],
    7: [
        ("Salimos como nunca, perdimos como siempre.", "Alfredo Di Stéfano"),
        ("La pelota no se mancha.", "Diego Maradona"),
        ("El fútbol es fútbol.", "Vujadin Boškov"),
        ("A veces se gana, a veces se aprende.", "Zinedine Zidane"),
        ("Estamos en la UVI, pero todavía estamos vivos.", "Javier Clemente"),
        ("¡Poned a los juveniles!", "Grito de la grada"),
        ("He fallado más de 9000 tiros... y hoy he sumado uno más.", "Michael Jordan"),
        ("Nuestra defensa tiene más agujeros que un queso suizo.", "{usuario}"),
        ("¡Vete ya! ¡Vete ya!", "La afición a {usuario}"),
        ("El fútbol es un deporte que inventaron los ingleses, juegan 11 contra 11 y siempre pierdo yo.", "Gary Lineker"),
        ("El fútbol es así, igual que la vida… si solo ganaran los mejores, esto sería más aburrido que bailar con tu hermana.", "Luis Enrique"),
        ("El fútbol es lo más importante de lo menos importante.", "Jorge Valdano"),
        ("Si perdemos seremos los mejores, si ganamos seremos eternos.", "Pep Guardiola"),
        ("Estoy arrepentido del 99% de todo lo que hice en mi vida, pero el 1% que es el fútbol salva el resto.", "Diego Maradona"),
        ("Ser segundo es ser el primero de los últimos.", "Alfredo Di Stéfano"),
        ("El asunto más difícil es encontrar algo para reemplazar al fútbol, porque no hay nada.", "Kevin Keegan"),
        ("Eu farei 10x se for preciso. Eles não estão preparados", "Vinicius Jr"),
        ("Fallaste el 100% de los tiros que no intentas” -Wayne Gretzky", "Michael Scott"),
        ("El gol es como las chicas en la discoteca, cuanto más te acercas, ellas más se alejan", "Miguel Angel Ramirez (MAR)")
    ]
}

LOGROS_DATA = {
    "guru": {"icon": "🔮", "name": "El Gurú", "desc": "Pleno en partido Esquizo."},
    "hattrick": {"icon": "🎯", "name": "Hat-Trick", "desc": "3+ plenos en la jornada."},
    "cima": {"icon": "🏔️", "name": "En la Cima", "desc": "Líder de la general."},
    "amarrategui": {"icon": "🧱", "name": "Amarrategui", "desc": "Puntuar con 1-0, 0-1 o 0-0."},
    "pleno": {"icon": "💯", "name": "Pleno", "desc": "Puntuar en los 10 partidos."}
}

# --- 2. FUNCIONES DE APOYO ---

@st.cache_data(ttl=60)
def leer_datos(pestaña):

    try:

        sheet_id = "1vFgccrCqmGrs9QfP8kxY_cESbRaJ_VxpsoAz-ZyL14E"

        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={pestaña}"

        return pd.read_csv(url)

    except:

        return pd.DataFrame()


def safe_float(valor):

    try:

        if pd.isna(valor):

            return 0.0

        return float(str(valor).replace(",", "."))

    except:

        return 0.0


def calcular_puntos(p_l, p_v, r_l, r_v, tipo="Normal"):

    try:

        p_l, p_v, r_l, r_v = float(p_l), float(p_v), float(r_l), float(r_v)

        p_ganador, p_diff, p_exacto = SCORING.get(tipo, SCORING["Normal"])

        if p_l == r_l and p_v == r_v:

            return p_exacto

        signo_p = (p_l > p_v) - (p_l < p_v)

        signo_r = (r_l > r_v) - (r_l < r_v)

        if signo_p == signo_r:

            if (p_l - p_v) == (r_l - r_v):

                return p_diff

            return p_ganador

        return 0.0

    except:

        return 0.0


@st.cache_data
def calcular_ranking(df_p_all, df_r_all, df_base, usuarios, tipo_r, jornada):

    ranking = []

    for u in usuarios:

        if tipo_r == "General":

            base = safe_float(

                df_base[df_base['Usuario']==u]['Puntos'].values[0]

            ) if not df_base[df_base['Usuario']==u].empty else 0

            preds = df_p_all[df_p_all['Usuario']==u]

        else:

            base = 0

            preds = df_p_all[

                (df_p_all['Usuario']==u)
                &
                (df_p_all['Jornada']==jornada)

            ]

        total = base

        for r in preds.itertuples():

            res = df_r_all[

                (df_r_all['Jornada']==r.Jornada)
                &
                (df_r_all['Partido']==r.Partido)
                &
                (df_r_all['Finalizado']=="SI")

            ]

            if not res.empty:

                total += calcular_puntos(

                    r.P_L,

                    r.P_V,

                    res.iloc[0]['R_L'],

                    res.iloc[0]['R_V'],

                    res.iloc[0]['Tipo']

                )

        ranking.append({

            "Usuario": u,

            "Puntos": round(total,2)

        })

    df = pd.DataFrame(ranking)

    df = df.sort_values("Puntos", ascending=False).reset_index(drop=True)

    df['Posicion'] = df.index + 1

    return df


# --- 3. APP ---

st.set_page_config(

    page_title="Porra League 2026",

    page_icon="⚽",

    layout="wide"

)

conn = st.connection("gsheets", type=GSheetsConnection)


if 'autenticado' not in st.session_state:

    st.session_state.autenticado = False


# --- LOGIN ---

if not st.session_state.autenticado:

    st.title("Porra League 2026")

    u = st.text_input("Usuario")

    p = st.text_input("Password", type="password")

    if st.button("Entrar"):

        df_u = leer_datos("Usuarios")

        ok = df_u[

            (df_u['Usuario']==u)
            &
            (df_u['Password']==p)

        ]

        if not ok.empty:

            st.session_state.autenticado = True

            st.session_state.user = u

            st.session_state.rol = ok.iloc[0]['Rol']

            st.rerun()

        else:

            st.error("Credenciales incorrectas")

else:

    # --- CARGA DATOS ---

    df_r_all = leer_datos("Resultados")

    df_p_all = leer_datos("Predicciones")

    df_u_all = leer_datos("Usuarios")

    df_base = leer_datos("PuntosBase")

    admins = df_u_all[

        df_u_all['Rol']=="admin"

    ]['Usuario'].tolist()

    usuarios = [

        u for u in df_u_all['Usuario'].unique()

        if u not in admins

    ]


    st.title(f"Hola {st.session_state.user}")


    jornada = st.selectbox(

        "Jornada",

        list(JORNADAS.keys())

    )


    tabs = st.tabs([

        "Apuestas",

        "Clasificación",

        "Detalles"

    ])


    # --- APUESTAS ---

    with tabs[0]:

        mis = df_p_all[

            (df_p_all['Usuario']==st.session_state.user)
            &
            (df_p_all['Jornada']==jornada)

        ]

        nuevas = []

        for i,(l,v) in enumerate(JORNADAS[jornada]):

            match = f"{l}-{v}"

            dl = 0

            dv = 0

            if not mis.empty:

                m = mis[mis['Partido']==match]

                if not m.empty:

                    dl = int(m.iloc[0]['P_L'])

                    dv = int(m.iloc[0]['P_V'])

            c1,c2,c3 = st.columns(3)

            with c1:

                pl = st.number_input(

                    l,

                    0,

                    value=dl,

                    key=f"l{i}"

                )

            with c2:

                pv = st.number_input(

                    v,

                    0,

                    value=dv,

                    key=f"v{i}"

                )

            nuevas.append({

                "Usuario":st.session_state.user,

                "Jornada":jornada,

                "Partido":match,

                "P_L":pl,

                "P_V":pv,

                "Publica":"SI"

            })

        if st.button("Guardar"):

            old = df_p_all[

                ~(

                    (df_p_all['Usuario']==st.session_state.user)
                    &
                    (df_p_all['Jornada']==jornada)

                )

            ]

            conn.update(

                worksheet="Predicciones",

                data=pd.concat(

                    [old,pd.DataFrame(nuevas)],

                    ignore_index=True

                )

            )

            st.success("Guardado")


    # --- CLASIFICACIÓN PRO ---

    with tabs[1]:

        tipo = st.radio(

            "Tipo",

            ["General","Jornada"]

        )

        df_rank = calcular_ranking(

            df_p_all,

            df_r_all,

            df_base,

            usuarios,

            tipo,

            jornada

        )

        st.dataframe(df_rank)


    # --- DETALLES ---

    with tabs[2]:

        final = df_r_all[

            (df_r_all['Jornada']==jornada)
            &
            (df_r_all['Finalizado']=="SI")

        ]

        tabla = pd.DataFrame(

            index=final['Partido'],

            columns=usuarios

        )

        for p in tabla.index:

            res = final[final['Partido']==p].iloc[0]

            for u in usuarios:

                pred = df_p_all[

                    (df_p_all['Usuario']==u)
                    &
                    (df_p_all['Jornada']==jornada)
                    &
                    (df_p_all['Partido']==p)

                ]

                if not pred.empty:

                    tabla.loc[p,u] = calcular_puntos(

                        pred.iloc[0]['P_L'],

                        pred.iloc[0]['P_V'],

                        res['R_L'],

                        res['R_V'],

                        res['Tipo']

                    )

                else:

                    tabla.loc[p,u] = 0

        st.dataframe(tabla)


    if st.button("Salir"):

        st.session_state.autenticado = False

        st.rerun()
