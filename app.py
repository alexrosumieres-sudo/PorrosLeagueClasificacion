import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time
import os
import plotly.express as px
import random
import itertools

# --- 1. CONFIGURACIONES GENERALES ---
PERFILES_DIR = "perfiles/"
LOGOS_DIR = "logos/"

NIVEL_EQUIPOS = {"Real Madrid": 1, "Barcelona": 1, "Villarreal": 1, "Atlético": 1,
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
def safe_float(valor):
    try:
        if pd.isna(valor) or str(valor).strip() == "": return 0.0
        return float(str(valor).replace(',', '.'))
    except: return 0.0

def get_logo(equipo):
    path = LOGOS.get(equipo)
    if path and os.path.exists(path): return path
    return None

def calcular_puntos(p_l, p_v, r_l, r_v, tipo="Normal"):
    try:
        # Esto convierte cualquier texto o vacío en número real. 
        # Si falla (porque hay texto de verdad), devuelve 0 puntos y no rompe la app.
        p_l, p_v, r_l, r_v = float(p_l), float(p_v), float(r_l), float(r_v)
        
        p_ganador, p_diff, p_exacto = SCORING.get(tipo, SCORING["Normal"])
        
        if p_l == r_l and p_v == r_v: return p_exacto
        
        signo_p = (p_l > p_v) - (p_l < p_v)
        signo_r = (r_l > r_v) - (r_l < r_v)
        
        if signo_p == signo_r:
            return p_diff if (p_l - p_v) == (r_l - r_v) else p_ganador
        return 0.0
    except:
        return 0.0

def obtener_perfil_apostador(df_u):
    if df_u is None or df_u.empty: return "Novato 🐣", "Sin datos.", 0.0
    avg_g = (df_u['P_L'] + df_u['P_V']).mean()
    riesgo = min(avg_g / 5.0, 1.0)
    if avg_g > 3.4: return "BUSCADOR DE PLENOS 🤪", "Ataque total.", riesgo
    if avg_g < 2.1: return "CONSERVADOR / AMARRETE 🛡️", "Fiel al 1-0.", riesgo
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
            if pts == SCORING.get(inf['Tipo'])[2]:
                exactos += 1
                if inf['Tipo'] == "Esquizo": logros.append("guru")
            if pts > 0 and sorted([row.P_L, row.P_V]) in [[0,0], [0,1]]: amarra += 1
    if len(pts_j) == 10:
        if all(p > 0 for p in pts_j): logros.append("pleno")
        if exactos >= 3: logros.append("hattrick")
        if amarra >= 5: logros.append("amarrategui")
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
    exactos = len(df_m[df_m.apply(lambda x: x.P_L == x.R_L and x.P_V == x.R_V, axis=1)])
    signos = len(df_m[df_m['Pts'] > 0]) - exactos
    return {
        "amuleto": max(pts_eq, key=pts_eq.get) if pts_eq else "N/A",
        "bestia": min(pts_eq, key=pts_eq.get) if pts_eq else "N/A",
        "exactos": exactos, "signos": signos, "fallos": len(df_m)-(exactos+signos),
        "avg_g": (df_m['P_L']+df_m['P_V']).mean(), "real_g": (df_m['R_L']+df_m['R_V']).mean()
    }

def simular_oraculo(usuarios, df_p_all, df_r_all, jornada_sel):
    res_sim = [(0,0), (1,0), (0,1), (1,1), (2,1), (1,2), (2,0), (0,2), (2,2), (3,0), (0,3), (3,1), (1,3), (3,2), (2,3)]
    pendientes = df_r_all[(df_r_all['Jornada'] == jornada_sel) & (df_r_all['Finalizado'] == "NO")]
    if pendientes.empty or len(pendientes) > 3: return None
    p_id = pendientes['Partido'].tolist()
    t_id = pendientes['Tipo'].tolist()
    pts_base = {u: 0.0 for u in usuarios}
    for u in usuarios:
        u_p = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == jornada_sel)]
        for r in u_p.itertuples():
            m_r = df_r_all[(df_r_all['Jornada']==jornada_sel) & (df_r_all['Partido']==r.Partido) & (df_r_all['Finalizado']=="SI")]
            if not m_r.empty:
                pts_base[u] += calcular_puntos(r.P_L, r.P_V, m_r.iloc[0]['R_L'], m_r.iloc[0]['R_V'], m_r.iloc[0]['Tipo'])
    victorias = {u: 0 for u in usuarios}
    combos = list(itertools.product(res_sim, repeat=len(p_id)))
    for c in combos:
        escenario = pts_base.copy()
        for i, res in enumerate(c):
            for u in usuarios:
                u_pred = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == jornada_sel) & (df_p_all['Partido'] == p_id[i])]
                if not u_pred.empty:
                    escenario[u] += calcular_puntos(u_pred.iloc[0]['P_L'], u_pred.iloc[0]['P_V'], res[0], res[1], t_id[i])
        max_p = max(escenario.values())
        ganadores = [u for u, p in escenario.items() if p == max_p]
        for g in ganadores: victorias[g] += 1 / len(ganadores)
    return {u: (v/len(combos))*100 for u, v in victorias.items()}

# --- 3. APP ---
st.set_page_config(page_title="Porros League 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos(pestaña):
    try:
        sheet_id = "1vFgccrCqmGrs9QfP8kxY_cESbRaJ_VxpsoAz-ZyL14E"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={pestaña}"
        return pd.read_csv(url)
    except: return pd.DataFrame()

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏆 Porros League 2026")
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
            nueva = pd.DataFrame([{"Usuario": u_in, "Password": p_in, "Rol": "user"}])
            conn.update(worksheet="Usuarios", data=pd.concat([df_u, nueva], ignore_index=True))
            st.success("✅ Registro completado")
else:
    # CARGA CENTRAL
    df_perfiles = leer_datos("ImagenesPerfil")
    df_r_all, df_p_all, df_u_all, df_base = leer_datos("Resultados"), leer_datos("Predicciones"), leer_datos("Usuarios"), leer_datos("PuntosBase")
    foto_dict = df_perfiles.set_index('Usuario')['ImagenPath'].to_dict() if not df_perfiles.empty else {}
    admins = df_u_all[df_u_all['Rol'] == 'admin']['Usuario'].tolist() if not df_u_all.empty else []
    u_jugadores = [u for u in df_u_all['Usuario'].unique() if u not in admins]
    c_h1, c_h2, c_h3 = st.columns([1, 5, 1])
    with c_h1:
        mi_f = foto_dict.get(st.session_state.user)
        if mi_f and pd.notna(mi_f) and os.path.exists(str(mi_f)): 
            st.image(str(mi_f), width=75)
        else: 
            st.subheader("👤")
    with c_h2: 
        st.title(f"Hola, {st.session_state.user} 👋")
    with c_h3: 
        if st.button("Salir"): 
            st.session_state.autenticado = False
            st.rerun()

    j_global = st.selectbox("📅 Jornada:", list(JORNADAS.keys()), key="global_j")
    p_pend = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "NO")]
    usa_oraculo = 1 <= len(p_pend) <= 3
    
    st.divider()
    tabs_labels = ["✍️ Apuestas", "👀 Otros", "📊 Clasificación", "📈 Stats PRO", "🏆 Detalles", "🔮 Simulador"]
    if usa_oraculo: tabs_labels.append("🎲 Escenarios")
    tabs_labels.append("⚙️ Admin")
    tabs = st.tabs(tabs_labels)

    # --- TABS ---
    with tabs[0]: # APUESTAS
        if st.session_state.rol != "admin":
            mis_p = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)]
            df_rj = df_r_all[df_r_all['Jornada'] == j_global]
            env = []
            for i, (loc, vis) in enumerate(JORNADAS[j_global]):
                m_id, b, t = f"{loc}-{vis}", False, "Normal"
                dl, dv, dp = 0, 0, False
                if not mis_p.empty:
                    pr = mis_p[mis_p['Partido'] == m_id]
                    if not pr.empty: dl, dv, dp = int(pr.iloc[0]['P_L']), int(pr.iloc[0]['P_V']), str(pr.iloc[0]['Publica']) == "SI"
                if not df_rj.empty and m_id in df_rj['Partido'].values:
                    inf = df_rj[df_rj['Partido'] == m_id].iloc[0]
                    t, b = inf['Tipo'], datetime.now() > datetime.strptime(str(inf['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                st.markdown(f"#### {t} {'🔒' if b else '🔓'}")
                c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 0.5, 2, 1, 2])
                with c1:
                    lg = get_logo(loc)
                    if lg: st.image(lg, width=65)
                    else: st.write("⚽")
                with c2: pl = st.number_input(f"{loc}", 0, value=dl, key=f"pl_{i}", disabled=b)
                with c4: pv = st.number_input(f"{vis}", 0, value=dv, key=f"pv_{i}", disabled=b)
                with c5:
                    lv = get_logo(vis)
                    if lv: st.image(lv, width=65)
                    else: st.write("⚽")
                with c6: pub = st.checkbox("Público", value=dp, key=f"pb_{i}", disabled=b)
                env.append({"Usuario": st.session_state.user, "Jornada": j_global, "Partido": m_id, "P_L": pl, "P_V": pv, "Publica": "SI" if pub else "NO"})
            if st.button("💾 Guardar"):
                old = df_p_all[~((df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global))]
                conn.update(worksheet="Predicciones", data=pd.concat([old, pd.DataFrame(env)], ignore_index=True))
                st.success("Guardado")

    with tabs[1]: # OTROS
        p_pub = df_p_all[(df_p_all['Jornada'] == j_global) & (df_p_all['Publica'] == "SI")]
        if p_pub.empty: st.info("Sin apuestas públicas aún.")
        for u in p_pub['Usuario'].unique():
            if u != st.session_state.user:
                with st.expander(f"Apuestas de {u}"): st.table(p_pub[p_pub['Usuario'] == u][['Partido', 'P_L', 'P_V']])

    with tabs[2]: # CLASIFICACIÓN
        tipo_r = st.radio("Ranking:", ["General", "Jornada"], horizontal=True)
        pts_list = []
        
        for u in u_jugadores:
            # Puntos base iniciales
            p_base = safe_float(df_base[df_base['Usuario']==u].iloc[0]['Puntos']) if tipo_r == "General" else 0.0
            
            # Filtramos las predicciones de este usuario para esta jornada
            u_p = df_p_all[(df_p_all['Usuario']==u) & (df_p_all['Jornada']==j_global)]
            
            p_acumulado = p_base

            # LÓGICA DE VALIDACIÓN:
            # Si u_p está vacío, el usuario no ha guardado nada. No entra al bucle de puntos.
            if not u_p.empty:
                for r in u_p.itertuples():
                    # Buscamos si el partido de la predicción ya está finalizado
                    m_finalizado = df_r_all[(df_r_all['Jornada']==r.Jornada) & 
                                           (df_r_all['Partido']==r.Partido) & 
                                           (df_r_all['Finalizado']=="SI")]
                    
                    if not m_finalizado.empty:
                        # Solo sumamos si existe la predicción real
                        p_acumulado += calcular_puntos(
                            r.P_L, r.P_V, 
                            m_finalizado.iloc[0]['R_L'], 
                            m_finalizado.iloc[0]['R_V'], 
                            m_finalizado.iloc[0]['Tipo']
                        )
            
            pts_list.append({"Usuario": u, "Puntos": p_acumulado})
        
        # Ordenar ranking
        df_rank = pd.DataFrame(pts_list).sort_values("Puntos", ascending=False)
        df_rank['Posicion'] = range(1, len(df_rank)+1)
        
        # Renderizado de la tabla
        for _, row in df_rank.iterrows():
            pos = row['Posicion']
            key_pos = pos if pos in FRASES_POR_PUESTO else 7
            f_t = random.choice(FRASES_POR_PUESTO[key_pos])
            
            l_u = calcular_logros_u(row['Usuario'], df_p_all, df_r_all, j_global, df_rank)
            icons = "".join([LOGROS_DATA[lid]['icon'] for lid in l_u])
            n, d, r_v = obtener_perfil_apostador(df_p_all[df_p_all['Usuario']==row['Usuario']])
            
            c1, c2, c3, c4 = st.columns([0.5, 1.2, 4, 1.5])
            with c1: 
                st.markdown(f"### #{pos}")
            with c2:
                fp = foto_dict.get(row['Usuario'])
                if fp and os.path.exists(str(fp)): st.image(fp, width=80)
                else: st.subheader("👤")
            with c3:
                # Nombre limpio, sin etiquetas de texto extra
                st.markdown(f"**{row['Usuario']}** {icons}")
                st.info(f"_{f_t[0]}_ \n\n **— {f_t[1]}**")
                st.progress(min(r_v, 1.0))
                st.caption(f"{n} | {d}")
            with c4: 
                st.markdown(f"#### {row['Puntos']:.2f} pts")
            st.divider()

    with tabs[3]: # STATS PRO
        st.header("📊 ADN del Apostador")
        u_sel = st.selectbox("Analizar a:", u_jugadores)
        adn = analizar_adn_pro(u_sel, df_p_all, df_r_all)
        if adn:
            c1, c2, c3 = st.columns(3)
            c1.metric("⭐ Amuleto", adn['amuleto']); c2.metric("💀 Bestia Negra", adn['bestia']); c3.metric("🎯 % Precisión", f"{(adn['signos']+adn['exactos'])/(adn['exactos']+adn['signos']+adn['fallos'])*100:.1f}%")
            f1, f2 = st.columns(2)
            with f1: st.plotly_chart(px.pie(values=[adn['exactos'], adn['signos'], adn['fallos']], names=['Plenos', 'Signos', 'Fallos'], color_discrete_sequence=['#2baf2b', '#ffd700', '#ff4b4b']), use_container_width=True)
            with f2:
                st.write(f"Predicción media: {adn['avg_g']:.2f} goles")
                if adn['avg_g'] - adn['real_g'] > 0.5: st.warning("Optimista del Gol")
                elif adn['avg_g'] - adn['real_g'] < -0.5: st.info("Amarrategui")
        else: st.info("Faltan datos finalizados.")

    with tabs[4]: # DETALLES
        df_rf = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "SI")]
        if not df_rf.empty:
            m_p = pd.DataFrame(index=df_rf['Partido'].unique(), columns=u_jugadores)
            for p in m_p.index:
                inf = df_rf[df_rf['Partido'] == p].iloc[0]
                for u in u_jugadores:
                    up = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == j_global) & (df_p_all['Partido'] == p)]
                    m_p.at[p, u] = calcular_puntos(up.iloc[0]['P_L'], up.iloc[0]['P_V'], inf['R_L'], inf['R_V'], inf['Tipo']) if not up.empty else 0.0
            st.dataframe(m_p.astype(float))
        else: st.warning("Sin partidos finalizados.")

    with tabs[5]: # SIMULADOR
        st.header("🔮 Simulador")
        usr_sim = st.selectbox("Según:", u_jugadores)
        if st.button("Simular"):
            sim = {k: v.copy() for k, v in STATS_LALIGA_BASE.items()}
            for p in df_p_all[df_p_all['Usuario']==usr_sim].itertuples():
                try:
                    tl, tv = p.Partido.split('-')
                    if tl in sim and tv in sim:
                        sim[tl]["PJ"]+=1; sim[tv]["PJ"]+=1
                        if p.P_L > p.P_V: sim[tl]["Pts"]+=3; sim[tl]["V"]+=1; sim[tv]["D"]+=1
                        elif p.P_V > p.P_L: sim[tv]["Pts"]+=3; sim[tv]["V"]+=1; sim[tl]["D"]+=1
                        else: sim[tl]["Pts"]+=1; sim[tv]["Pts"]+=1; sim[tl]["E"]+=1; sim[tv]["E"]+=1
                except: continue
            df_s = pd.DataFrame.from_dict(sim, orient='index').reset_index().sort_values("Pts", ascending=False)
            df_s['Pos'] = range(1, 21)
            st.dataframe(df_s[['Pos', 'index', 'Pts']], hide_index=True)

    if usa_oraculo:
        with tabs[6]: # ESCENARIOS
            st.header("🔮 Oráculo de Probabilidades")
            probs = simular_oraculo(u_jugadores, df_p_all, df_r_all, j_global)
            if probs:
                for u, v in sorted(probs.items(), key=lambda x: x[1], reverse=True):
                    if v > 0: st.write(f"**{u}**: {v:.1f}%"); st.progress(v/100)

    # --- ADMIN (AL FINAL) ---
    with tabs[-1]:
        if st.session_state.rol == "admin":
            st.header("⚙️ Admin")
            a_t = st.tabs(["⭐ Bases", "📸 Fotos", "⚽ Resultados"])
            with a_t[0]:
                upd_b = []
                for u in u_jugadores:
                    pts_ex = safe_float(df_base[df_base['Usuario'] == u].iloc[0]['Puntos']) if not df_base.empty and u in df_base['Usuario'].values else 0.0
                    val = st.number_input(f"Base {u}", value=pts_ex, key=f"adm_b_{u}")
                    upd_b.append({"Usuario": u, "Puntos": val})
                if st.button("Guardar Bases"): conn.update(worksheet="PuntosBase", data=pd.DataFrame(upd_b)); st.success("OK")
            with a_t[1]:
                if os.path.exists(PERFILES_DIR):
                    fotos = sorted(os.listdir(PERFILES_DIR))
                    upd_f = []
                    for u in u_jugadores:
                        db_p = foto_dict.get(u, "")
                        idx = (fotos.index(os.path.basename(db_p)) + 1) if (db_p and os.path.basename(db_p) in fotos) else 0
                        fs = st.selectbox(f"Foto {u}", ["Ninguna"] + fotos, index=idx, key=f"adm_f_{u}")
                        upd_f.append({"Usuario": u, "ImagenPath": f"{PERFILES_DIR}{fs}" if fs != "Ninguna" else ""})
                    if st.button("Asociar Fotos"): conn.update(worksheet="ImagenesPerfil", data=pd.DataFrame(upd_f)); st.success("OK")
            with a_t[2]:
                r_env, h_ops = [], [time(h, m) for h in range(12, 23) for m in [0, 15, 30, 45]]
                for i, (l, v) in enumerate(JORNADAS[j_global]):
                    m_id = f"{l}-{v}"
                    st.subheader(f"⚽ {m_id}")
                    prev = df_r_all[(df_r_all['Jornada']==j_global) & (df_r_all['Partido']==m_id)]
                    dt, t_p, rl, rv, f = datetime.now(), "Normal", 0, 0, False
                    if not prev.empty:
                        t_p, rl, rv, f = prev.iloc[0]['Tipo'], int(prev.iloc[0]['R_L']), int(prev.iloc[0]['R_V']), prev.iloc[0]['Finalizado'] == "SI"
                        try: dt = datetime.strptime(str(prev.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                        except: pass
                    c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 1, 1, 1])
                    nt = c1.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], index=["Normal", "Doble", "Esquizo"].index(t_p), key=f"adm_t_{i}")
                    nf = c2.date_input("D", value=dt.date(), key=f"adm_d_{i}")
                    nh = c3.selectbox("H", h_ops, index=h_ops.index(dt.time()) if dt.time() in h_ops else 0, key=f"adm_h_{i}")
                    nrl = c4.number_input("L", 0, value=rl, key=f"adm_rl_{i}")
                    nrv = c5.number_input("V", 0, value=rv, key=f"adm_rv_{i}")
                    nfi = c6.checkbox("Fin", value=f, key=f"adm_fi_{i}")
                    r_env.append({"Jornada": j_global, "Partido": m_id, "Tipo": nt, "R_L": nrl, "R_V": nrv, "Hora_Inicio": datetime.combine(nf, nh).strftime("%Y-%m-%d %H:%M:%S"), "Finalizado": "SI" if nfi else "NO"})
                if st.button("Actualizar Jornada"):
                    otros = df_r_all[df_r_all['Jornada'] != j_global]
                    conn.update(worksheet="Resultados", data=pd.concat([otros, pd.DataFrame(r_env)], ignore_index=True))
                    st.success("Resultados actualizados")

