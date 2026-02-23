import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time
import os
import plotly.express as px
import random
import itertools
import numpy as np

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

@st.cache_data(ttl=600)
def leer_datos(pestaña):
    try:
        sheet_id = "1vFgccrCqmGrs9QfP8kxY_cESbRaJ_VxpsoAz-ZyL14E"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={pestaña}"
        return pd.read_csv(url)
    except: return pd.DataFrame()

def safe_float(valor):
    try:
        if pd.isna(valor) or str(valor).strip() == "": return 0.0
        return float(str(valor).replace(',', '.'))
    except: return 0.0

def get_logo(equipo):
    path = LOGOS.get(equipo)
    return path if path and os.path.exists(path) else None

def calcular_puntos(p_l, p_v, r_l, r_v, tipo="Normal"):
    try:
        p_l, p_v, r_l, r_v = float(p_l), float(p_v), float(r_l), float(r_v)
        p_ganador, p_diff, p_exacto = SCORING.get(tipo, SCORING["Normal"])
        if p_l == r_l and p_v == r_v: return p_exacto
        signo_p = (p_l > p_v) - (p_l < p_v)
        signo_r = (r_l > r_v) - (r_l < r_v)
        if signo_p == signo_r:
            return p_diff if (p_l - p_v) == (r_l - r_v) else p_ganador
        return 0.0
    except: return 0.0

def obtener_perfil_apostador(df_u):
    if df_u is None or df_u.empty: return "Novato 🐣", "Sin datos.", 0.0
    avg_g = (df_u['P_L'] + df_u['P_V']).mean()
    riesgo = min(avg_g / 5.0, 1.0)
    if avg_g > 3.4: return "BUSCADOR DE PLENOS 🤪", "Ataque total.", riesgo
    if avg_g < 2.1: return "CONSERVADOR 🛡️", "Fiel al 1-0.", riesgo
    return "ESTRATEGA ⚖️", "Apuestas equilibradas.", riesgo

def calcular_logros_u(usuario, df_p_all, df_r_all, jornada_sel, ranking):
    logros = []
    if not ranking.empty and ranking.iloc[0]['Usuario'] == usuario: logros.append("cima")
    u_p = df_p_all[(df_p_all['Usuario'] == usuario) & (df_p_all['Jornada'] == jornada_sel)]
    res_j = df_r_all[(df_r_all['Jornada'] == jornada_sel) & (df_r_all['Finalizado'] == "SI")]
    if u_p.empty or res_j.empty: return logros
    pts_j, exactos, amarra = [], 0, 0
    for row in u_p.itertuples():
        m = res_j[res_j['Partido'] == row.Partido]
        if not m.empty:
            inf = m.iloc[0]
            pts = calcular_puntos(row.P_L, row.P_V, inf['R_L'], inf['R_V'], inf['Tipo'])
            pts_j.append(pts)
            if pts == SCORING.get(inf['Tipo'])[2]: exactos += 1
            if pts > 0 and sorted([row.P_L, row.P_V]) in [[0,0], [0,1]]: amarra += 1
    if len(pts_j) == 10:
        if all(p > 0 for p in pts_j): logros.append("pleno")
        if exactos >= 3: logros.append("hattrick")
    return list(set(logros))

def analizar_adn_pro(usuario, df_p, df_r):
    df_m = pd.merge(df_p[df_p['Usuario'] == usuario], df_r[df_r['Finalizado'] == "SI"], on=['Jornada', 'Partido'])
    if df_m.empty: return None
    df_m['Pts'] = df_m.apply(lambda x: calcular_puntos(x.P_L, x.P_V, x.R_L, x.R_V, x.Tipo), axis=1)
    pts_eq = {}
    for _, r in df_m.iterrows():
        l, v = r['Partido'].split('-')
        pts_eq[l] = pts_eq.get(l, 0) + r['Pts']
        pts_eq[v] = pts_eq.get(v, 0) + r['Pts']
    ex = len(df_m[df_m.apply(lambda x: x.P_L == x.R_L and x.P_V == x.R_V, axis=1)])
    sig = len(df_m[df_m['Pts'] > 0]) - ex
    return {
        "amuleto": max(pts_eq, key=pts_eq.get) if pts_eq else "N/A",
        "bestia": min(pts_eq, key=pts_eq.get) if pts_eq else "N/A",
        "exactos": ex, "signos": sig, "fallos": len(df_m)-(ex+sig),
        "avg_g": (df_m['P_L']+df_m['P_V']).mean(), "real_g": (df_m['R_L']+df_m['R_V']).mean()
    }

def simular_oraculo(usuarios, df_p_all, df_r_all, jornada_sel):
    res_sim = [(0,0), (1,0), (0,1), (1,1), (2,1), (1,2), (2,0), (0,2), (2,2), (3,1)]
    pend = df_r_all[(df_r_all['Jornada'] == jornada_sel) & (df_r_all['Finalizado'] == "NO")]
    if pend.empty or len(pend) > 3: return None
    p_id, t_id = pend['Partido'].tolist(), pend['Tipo'].tolist()
    vics = {u: 0 for u in usuarios}
    combos = list(itertools.product(res_sim, repeat=len(p_id)))
    for c in combos:
        esc = {u: 0.0 for u in usuarios}
        for u in usuarios:
            u_p = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == jornada_sel)]
            for r in u_p.itertuples():
                m_r = df_r_all[(df_r_all['Jornada']==jornada_sel)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
                if not m_r.empty: esc[u] += calcular_puntos(r.P_L, r.P_V, m_r.iloc[0]['R_L'], m_r.iloc[0]['R_V'], m_r.iloc[0]['Tipo'])
                for i, p_match in enumerate(p_id):
                    if r.Partido == p_match: esc[u] += calcular_puntos(r.P_L, r.P_V, c[i][0], c[i][1], t_id[i])
        mx = max(esc.values()); gans = [u for u, p in esc.items() if p == mx]
        for g in gans: vics[g] += 1 / len(gans)
    return {u: (v/len(combos))*100 for u, v in vics.items()}

# --- 3. APP ---
st.set_page_config(page_title="Porra League 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏆 Porra League 2026")
        u_in = st.text_input("Usuario")
        p_in = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            df_u = leer_datos("Usuarios")
            user_db = df_u[(df_u['Usuario'].astype(str) == str(u_in)) & (df_u['Password'].astype(str) == str(p_in))]
            if not user_db.empty:
                st.session_state.autenticado, st.session_state.user, st.session_state.rol = True, u_in, user_db.iloc[0]['Rol']
                st.rerun()
            else: st.error("❌ Credenciales incorrectas")
        if st.button("Registrarse"):
            df_u = leer_datos("Usuarios")
            if u_in in df_u['Usuario'].values:
                st.error("❌ El usuario ya existe")
            else:
                nueva = pd.DataFrame([{"Usuario": u_in, "Password": p_in, "Rol": "user"}])
                conn.update(worksheet="Usuarios", data=pd.concat([df_u, nueva], ignore_index=True))
                st.success("✅ Registro completado. Ya puedes entrar.")
else:
    df_perf = leer_datos("ImagenesPerfil")
    df_r_all, df_p_all, df_u_all, df_base = leer_datos("Resultados"), leer_datos("Predicciones"), leer_datos("Usuarios"), leer_datos("PuntosBase")
    
    foto_dict = df_perf.set_index('Usuario')['ImagenPath'].to_dict() if not df_perf.empty else {}
    u_jugadores = [u for u in df_u_all['Usuario'].unique() if u not in df_u_all[df_u_all['Rol'] == 'admin']['Usuario'].tolist()]

    st.markdown("""
        <style>
        /* Fondo blanco y texto oscuro estándar */
        .stApp { background-color: #ffffff; color: #31333F; }
        
        /* Tarjetas con fondo gris muy claro para que resalten sobre el blanco */
        .panini-card {
            background: #f8f9fb; border-radius: 15px; padding: 20px;
            border: 1px solid #e0e0e0; margin-bottom: 20px; transition: 0.3s;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        }
        .panini-card:hover { border-color: #2baf2b; background: #f1f3f6; }
        
        /* Texto de citas en gris oscuro */
        .quote-text { color: #4f4f4f; font-style: italic; border-left: 3px solid #2baf2b; padding-left: 10px; margin: 10px 0; }
        
        /* Badge de posición y cajas de partidos */
        .pos-badge { background-color: #2baf2b; color: white; padding: 5px 15px; border-radius: 50%; font-weight: bold; }
        .match-box { 
            background: #ffffff; border-radius: 10px; padding: 15px; 
            border: 1px solid #eee; border-left: 5px solid #2baf2b; 
            margin-bottom: 10px; box-shadow: 1px 1px 4px rgba(0,0,0,0.03); 
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚽ Menú Liga")
        j_sel = st.selectbox("📅 Jornada:", list(JORNADAS.keys()), key="side_j")
        st.divider()
        p_p = df_r_all[(df_r_all['Jornada'] == j_sel) & (df_r_all['Finalizado'] == "NO")]
        if 1 <= len(p_p) <= 3: st.warning(f"🔮 Oráculo Activo: {len(p_p)} partidos")
        if st.button("Cerrar Sesión"): st.session_state.autenticado = False; st.rerun()

    c1, c2 = st.columns([1, 5])
    with c2: st.title(f"Hola, {st.session_state.user} 👋")

    usa_oraculo = 1 <= len(p_p) <= 3
    tabs_labels = ["✍️ Apuestas", "👀 Otros", "📊 Clasificación", "📈 Stats PRO", "🏆 Detalles"]
    if usa_oraculo: tabs_labels.append("🎲 Oráculo")
    tabs_labels.append("⚙️ Admin")
    tabs = st.tabs(tabs_labels)

    with tabs[0]: # APUESTAS
        u_preds = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_sel)]
        env = []
        for i, (loc, vis) in enumerate(JORNADAS[j_sel]):
            m_id = f"{loc}-{vis}"
            dl, dv, dp, lock = 0, 0, "NO", False
            if not u_preds.empty:
                row = u_preds[u_preds['Partido'] == m_id]
                if not row.empty: dl, dv, dp = int(row.iloc[0]['P_L']), int(row.iloc[0]['P_V']), row.iloc[0]['Publica']
            
            inf = df_r_all[(df_r_all['Jornada']==j_sel) & (df_r_all['Partido']==m_id)]
            if not inf.empty:
                lock = datetime.now() > datetime.strptime(str(inf.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
            
            st.markdown(f'<div class="match-box">', unsafe_allow_html=True)
            col1, col2, col3, col4, col5 = st.columns([2, 1, 0.5, 1, 2])
            with col1: 
                logo = get_logo(loc)
                if logo: st.image(logo, width=40)
                st.write(f"**{loc}**")
            with col2: l = st.number_input("", 0, 9, dl, key=f"l_{i}", disabled=lock, label_visibility="collapsed")
            with col3: st.write("—")
            with col4: v = st.number_input("", 0, 9, dv, key=f"v_{i}", disabled=lock, label_visibility="collapsed")
            with col5:
                logo_v = get_logo(vis)
                if logo_v: st.image(logo_v, width=40)
                st.write(f"**{vis}**")
            pub = st.checkbox("Pública", dp=="SI", key=f"p_{i}", disabled=lock)
            st.markdown('</div>', unsafe_allow_html=True)
            env.append({"Usuario": st.session_state.user, "Jornada": j_sel, "Partido": m_id, "P_L": l, "P_V": v, "Publica": "SI" if pub else "NO"})
        
        if st.button("💾 Guardar Jornada"):
            ahora = datetime.now()
            invalidos = []
            for pred in env:
                inf_p = df_r_all[(df_r_all['Partido']==pred['Partido']) & (df_r_all['Jornada']==j_sel)].iloc[0]
                if ahora > datetime.strptime(str(inf_p['Hora_Inicio']), "%Y-%m-%d %H:%M:%S"):
                    invalidos.append(pred['Partido'])
            if invalidos:
                st.error(f"❌ No puedes guardar. Estos partidos ya empezaron: {', '.join(invalidos)}")
            else:
                old = df_p_all[~((df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_sel))]
                conn.update(worksheet="Predicciones", data=pd.concat([old, pd.DataFrame(env)], ignore_index=True))
                st.cache_data.clear()
                st.success("¡Porra guardada!")

    with tabs[2]: # CLASIFICACIÓN
        tipo_r = st.radio("Ver Ranking:", ["General", "Jornada"], horizontal=True)
        pts_list = []
        for u in u_jugadores:
            if tipo_r == "General":
                pb_row = df_base[df_base['Usuario'] == u]
                p_base = safe_float(pb_row['Puntos'].values[0]) if not pb_row.empty else 0.0
                u_p = df_p_all[df_p_all['Usuario'] == u]
            else:
                p_base = 0.0
                u_p = df_p_all[(df_p_all['Usuario']==u) & (df_p_all['Jornada']==j_sel)]
            p_ac = p_base
            if not u_p.empty:
                for r in u_p.itertuples():
                    m_k = df_r_all[(df_r_all['Jornada']==r.Jornada)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
                    if not m_k.empty: 
                        p_ac += calcular_puntos(r.P_L, r.P_V, m_k.iloc[0]['R_L'], m_k.iloc[0]['R_V'], m_k.iloc[0]['Tipo'])
            pts_list.append({"Usuario": u, "Puntos": p_ac})
        df_rank = pd.DataFrame(pts_list).sort_values("Puntos", ascending=False)
        df_rank['Posicion'] = range(1, len(df_rank)+1)
        for _, row in df_rank.iterrows():
            pos = row['Posicion']
            f_t = random.choice(FRASES_POR_PUESTO[pos if pos in FRASES_POR_PUESTO else 7])
            st.markdown(f'<div class="panini-card">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([0.6, 1.2, 3.5, 1.5])
            with c1: st.markdown(f'<br><span class="pos-badge">{pos}</span>', unsafe_allow_html=True)
            with c2:
                img = foto_dict.get(row['Usuario'])
                if img and os.path.exists(str(img)): st.image(img, width=80)
                else: st.markdown("### 👤")
            with c3:
                st.markdown(f"### {row['Usuario']}")
                st.markdown(f'<div class="quote-text">"{f_t[0]}"<br><small>— {f_t[1]}</small></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<br><span style="font-size: 2em; font-weight: bold; color: #2baf2b;">{row["Puntos"]:.2f}</span><br>Pts', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tabs[-1]: # ADMIN
        if st.session_state.rol == "admin":
            st.write("### ⚙️ Administrar Resultados")
            r_env = []
            for i, (l, v) in enumerate(JORNADAS[j_sel]):
                m_id = f"{l}-{v}"
                prev = df_r_all[(df_r_all['Jornada']==j_sel) & (df_r_all['Partido']==m_id)]
                rl, rv, fin, t, hor = 0, 0, False, "Normal", "2026-02-23 21:00:00"
                if not prev.empty: 
                    rl, rv, fin = int(prev.iloc[0]['R_L']), int(prev.iloc[0]['R_V']), prev.iloc[0]['Finalizado']=="SI"
                    t, hor = prev.iloc[0]['Tipo'], prev.iloc[0]['Hora_Inicio']
                c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
                with c1: st.write(m_id)
                nt = c2.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], index=["Normal", "Doble", "Esquizo"].index(t), key=f"at_{i}")
                nrl = c3.number_input("L", 0, 9, rl, key=f"arl_{i}")
                nrv = c4.number_input("V", 0, 9, rv, key=f"arv_{i}")
                nfi = c5.checkbox("Fin", fin, key=f"afi_{i}")
                r_env.append({"Jornada": j_sel, "Partido": m_id, "Tipo": nt, "R_L": nrl, "R_V": nrv, "Hora_Inicio": hor, "Finalizado": "SI" if nfi else "NO"})
            if st.button("Actualizar Resultados"):
                otros = df_r_all[df_r_all['Jornada'] != j_sel]
                conn.update(worksheet="Resultados", data=pd.concat([otros, pd.DataFrame(r_env)], ignore_index=True))
                st.cache_data.clear()
                st.success("Resultados actualizados.")

