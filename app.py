import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import os
import plotly.express as px
import random
import itertools
import numpy as np
import time
import pytz
import google.generativeai as genai

# --- 1. CONFIGURACIONES GENERALES ---
PERFILES_DIR = "perfiles/"
LOGOS_DIR = "logos/"

NIVEL_EQUIPOS = {
    "Real Madrid": 1, "Barcelona": 1, "Villarreal": 1, "Atlético": 1,
    "Betis": 2, "Espanyol": 2, "Celta": 2, "R. Sociedad": 2, "Athletic": 2,
    "Osasuna": 3, "Getafe": 3, "Girona": 3, "Sevilla": 3, "Alavés": 3, "Valencia": 3, "Elche": 3, "Rayo": 3,
    "Mallorca": 4, "Levante": 4, "Oviedo": 4
}

# Datos oficiales tras la Jornada 24 (Base para el simulador)
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
    "Octavos Champions IDA": [("Galatasaray", "Liverpool"), ("Atalanta", "Bayern Múnich"), ("Atlético", "Tottenham H."), ("Newcastle United", "Barcelona"),  ("Bayer Leverkusen", "Arsenal"), ("Bodø/Glimt", "Sp. Portugal"), ("PSG", "Chelsea"), ("Real Madrid", "M. City")],
    "Jornada 28": [("Alavés", "Villarreal"), ("Girona", "Athletic"), ("Atlético", "Getafe"), ("Oviedo", "Valencia"), ("Real Madrid", "Elche"), ("Mallorca", "Espanyol"), ("Barcelona", "Sevilla"), ("Betis", "Celta"), ("Real Sociedad", "Osasuna"), ("Rayo", "Levante")],
    "Octavos Champions VUELTA": [("Sp. Portugal", "Bodø/Glimt"), ("Arsenal", "Bayer Leverkusen"), ("Chelsea", "PSG"), ("M. City", "Real Madrid"), ("Barcelona", "Newcastle United"), ("Bayern Múnich", "Atalanta"), ("Liverpool", "Galatasaray"), ("Tottenham H.", "Atlético")],
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
    "Levante": f"{LOGOS_DIR}levante.jpeg", "Oviedo": f"{LOGOS_DIR}oviedo.jpeg",
    
    # --- EQUIPOS CHAMPIONS
    "Galatasaray": f"{LOGOS_DIR}Galatasaray.png",
    "Liverpool": f"{LOGOS_DIR}Liverpool.png",
    "Atalanta": f"{LOGOS_DIR}Atalanta.png",
    "Bayern Múnich": f"{LOGOS_DIR}Bayernmunich.jpeg",
    "Tottenham H.": f"{LOGOS_DIR}tottenham.jpeg",
    "Newcastle United": f"{LOGOS_DIR}newcastle.png",
    "Bayer Leverkusen": f"{LOGOS_DIR}leverkusen.png",
    "Arsenal": f"{LOGOS_DIR}arsenal.jpeg",
    "Bodø/Glimt": f"{LOGOS_DIR}bodo.png",
    "Sp. Portugal": f"{LOGOS_DIR}sportingportugal.png",
    "PSG": f"{LOGOS_DIR}psg.jpeg",
    "Chelsea": f"{LOGOS_DIR}chelsea.png",
    "M. City": f"{LOGOS_DIR}city.png"
}

SCORING = {"Normal": (0.5, 0.75, 1.0), "Doble": (1.0, 1.5, 2.0), "Esquizo": (1.0, 1.5, 3.0)}

# --- FRASES MÍTICAS ---
FRASES_POR_PUESTO = {
    1: [
        ("Ganar, ganar y volver a ganar.", "Luis Aragonés"),
        ("Siuuuuu.", "CR7"),
        ("Ganar no es lo más importante, es lo único.", "Luis Aragonés"),
        ("Los segundos son los primeros de los perdedores.", "Ayrton Senna"),
        ("El éxito es la suma de pequeños esfuerzos repetidos cada día.", "Anónimo"),
        ("Somos los mejores.", "Pep Guardiola"),
        ("El trabajo da sus frutos.", "Carlo Ancelotti"),
        ("Mentalidad ganadora.", "Cristiano Ronaldo"),
        ("El campeón se levanta siempre.", "Anónimo"),
        ("Nada supera a la victoria.", "Anónimo"),
        ("Objetivo cumplido.", "Anónimo"),
        ("Esto es para la historia.", "Anónimo"),
        ("Nacidos para ganar.", "Anónimo"),
        ("Arriba del todo.", "Anónimo"),
        ("La cima es nuestra.", "Anónimo")
    ],

    2: [
        ("Perder una final es lo peor.", "Messi"),
        ("Lo intentamos.", "Sergio Ramos"),
        ("Estuvimos cerca.", "Anónimo"),
        ("Duele, pero volveremos.", "Anónimo"),
        ("Caer está permitido, levantarse es obligatorio.", "Anónimo"),
        ("Nos faltó muy poco.", "Anónimo"),
        ("Aprendemos de las derrotas.", "Anónimo"),
        ("El próximo será nuestro.", "Anónimo"),
        ("Orgullosos del equipo.", "Anónimo"),
        ("No fue suficiente.", "Anónimo"),
        ("Rozando la gloria.", "Anónimo"),
        ("Competimos hasta el final.", "Anónimo"),
        ("Subcampeones con honor.", "Anónimo"),
        ("Volveremos más fuertes.", "Anónimo"),
        ("A un paso del sueño.", "Anónimo")
    ],

    3: [
        ("Partido a partido.", "Simeone"),
        ("Ni tan mal.", "Anónimo"),
        ("El podio siempre es buen lugar.", "Anónimo"),
        ("Sumar siempre es importante.", "Anónimo"),
        ("Objetivo cumplido a medias.", "Anónimo"),
        ("Regularidad ante todo.", "Anónimo"),
        ("Constancia y trabajo.", "Anónimo"),
        ("Paso firme.", "Anónimo"),
        ("Siempre competitivos.", "Anónimo"),
        ("Temporada sólida.", "Anónimo"),
        ("Ahí estamos.", "Anónimo"),
        ("En la pelea.", "Anónimo"),
        ("Trabajo silencioso.", "Anónimo"),
        ("Punto a punto.", "Anónimo"),
        ("Ni arriba ni abajo.", "Anónimo")
    ],

    4: [
        ("El fútbol es así.", "Boskov"),
        ("Hay que seguir.", "Ancelotti"),
        ("Nos faltó ese último paso.", "Anónimo"),
        ("Morir en la orilla.", "Anónimo"),
        ("A las puertas de todo.", "Anónimo"),
        ("Casi, pero no.", "Anónimo"),
        ("Nos quedamos ahí.", "Anónimo"),
        ("Buen intento.", "Anónimo"),
        ("Detalles que marcan diferencias.", "Anónimo"),
        ("Aprender y mejorar.", "Anónimo"),
        ("El año que viene más.", "Anónimo"),
        ("Competimos bien.", "Anónimo"),
        ("No alcanzó.", "Anónimo"),
        ("Todo suma.", "Anónimo"),
        ("Seguimos creciendo.", "Anónimo")
    ],

    5: [
        ("¿Por qué?", "Mourinho"),
        ("Fútbol es fútbol.", "Boskov"),
        ("A veces se gana, a veces se aprende.", "Anónimo"),
        ("Temporada irregular.", "Anónimo"),
        ("Podría haber sido peor.", "Anónimo"),
        ("Ni frío ni calor.", "Anónimo"),
        ("En tierra de nadie.", "Anónimo"),
        ("Sin pena ni gloria.", "Anónimo"),
        ("Mucho que mejorar.", "Anónimo"),
        ("Hay margen.", "Anónimo"),
        ("Esto es largo.", "Anónimo"),
        ("No era el plan.", "Anónimo"),
        ("Toca reflexionar.", "Anónimo"),
        ("Nada decidido.", "Anónimo"),
        ("Seguimos vivos.", "Anónimo"),
        ("¿Por qué?", "Mourinho"),
        ("Fútbol es fútbol.", "Boskov"),
        ("Ni fu ni fa.", "La grada"),
        ("Más cerca del descenso que del podio.", "La Sotana vibes"),
        ("Proyecto interesante... para 2028.", "La Sotana vibes"),
        ("Equipo en construcción desde 1997.", "La Sotana vibes"),
        ("Prometía mucho en pretemporada.", "La Sotana vibes"),
        ("Dominamos en posesión moral.", "La Sotana vibes"),
        ("Objetivo: no hacer el ridículo.", "La grada"),
        ("Partido serio... durante 7 minutos.", "La Sotana vibes"),
        ("Somos un meme.", "Twitter futbolero"),
        ("Clasificación engañosa (para mal).", "La Sotana vibes"),
        ("Competimos... a nuestra manera.", "La grada"),
        ("Nos faltó todo.", "La Sotana vibes"),
        ("Aspirábamos a más, conseguimos menos.", "La grada")
    ],

    6: [
        ("Prefiero no hablar.", "Mourinho"),
        ("Hay que levantarse.", "CR7"),
        ("Momento complicado.", "Anónimo"),
        ("Esto no ha terminado.", "Anónimo"),
        ("Toca sufrir.", "Anónimo"),
        ("Hay que apretar los dientes.", "Anónimo"),
        ("Salir del bache.", "Anónimo"),
        ("Unidos saldremos.", "Anónimo"),
        ("Trabajo y más trabajo.", "Anónimo"),
        ("Remar contra corriente.", "Anónimo"),
        ("No bajamos los brazos.", "Anónimo"),
        ("Pelear hasta el final.", "Anónimo"),
        ("Esto se levanta.", "Anónimo"),
        ("Día duro.", "Anónimo"),
        ("Paso atrás.", "Anónimo"),
        ("Prefiero no hablar.", "Mourinho"),
        ("Hay que levantarse.", "CR7"),
        ("Defendemos con la mirada.", "La Sotana vibes"),
        ("El rival parecía el Brasil del 70.", "La Sotana vibes"),
        ("Proyecto ilusionante (para el rival).", "La grada"),
        ("Nos remontan hasta en el FIFA.", "La Sotana vibes"),
        ("Más blandos que el pan de molde.", "La Sotana vibes"),
        ("El VAR tampoco nos salva.", "La grada"),
        ("Estamos probando cosas (ninguna funciona).", "La Sotana vibes"),
        ("Entrenamos sin balón, se nota.", "La Sotana vibes"),
        ("Nuestro objetivo es participar.", "La grada"),
        ("Temporada histórica... para olvidar.", "La Sotana vibes"),
        ("El descenso nos guiña el ojo.", "La Sotana vibes"),
        ("Jugamos a sorprender… y lo logramos.", "La grada"),
        ("El míster tiene un plan (nadie sabe cuál).", "La Sotana vibes")
    ],

    7: [
        ("Estamos en la UVI.", "Clemente"),
        ("Salimos como nunca...", "Di Stéfano"),
        ("Tocar fondo para impulsarse.", "Anónimo"),
        ("Situación crítica.", "Anónimo"),
        ("Hora de reaccionar.", "Anónimo"),
        ("No queda margen.", "Anónimo"),
        ("Sufrir para sobrevivir.", "Anónimo"),
        ("Cada punto es oro.", "Anónimo"),
        ("Final tras final.", "Anónimo"),
        ("Salvar la categoría.", "Anónimo"),
        ("Resistir es ganar.", "Anónimo"),
        ("Con el agua al cuello.", "Anónimo"),
        ("Última bala.", "Anónimo"),
        ("Orgullo y corazón.", "Anónimo"),
        ("Nunca rendirse.", "Anónimo"),
        ("Estamos en la UVI.", "Clemente"),
        ("Salimos como nunca perdemos como siempre", "Di Stéfano"),
        ("Descenso speedrun any%.", "La Sotana vibes"),
        ("El Titanic tenía mejor planificación.", "La Sotana vibes"),
        ("Nos pitan y no sabemos si es penalti o final.", "La grada"),
        ("Somos el sparring oficial de la liga.", "La Sotana vibes"),
        ("Cada jornada, un trauma nuevo.", "La Sotana vibes"),
        ("El calendario pide perdón.", "La grada"),
        ("Defensa de mantequilla.", "La Sotana vibes"),
        ("Tenemos más excusas que puntos.", "La Sotana vibes"),
        ("Modo supervivencia activado.", "La grada"),
        ("Esto ya es contenido.", "La Sotana vibes"),
        ("El descenso no es amenaza, es destino.", "La Sotana vibes"),
        ("Jugamos sin red.", "La grada"),
        ("La clasificación no miente (ojalá lo hiciera).", "La Sotana vibes")
    ]
}

LOGROS_DATA = {
    "guru": {"icon": "🔮", "name": "El Gurú", "desc": "Pleno en Esquizo."},
    "cima": {"icon": "🏔️", "name": "En la Cima", "desc": "Líder general."},
    "pleno": {"icon": "💯", "name": "Pleno", "desc": "Puntuado en los 10."}
}

# --- 2. FUNCIONES DE APOYO ---
@st.cache_data(ttl=10) # TTL bajo para que los cambios del admin se vean rápido
def leer_datos(pestaña):
    try:
        sheet_id = "1vFgccrCqmGrs9QfP8kxY_cESbRaJ_VxpsoAz-ZyL14E"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={pestaña}"
        return pd.read_csv(url)
    except: return pd.DataFrame()

def preparar_contexto_ia(df_hero, df_logs):
    # Resumen de la clasificación
    top_3 = df_hero.head(3)
    ultimo = df_hero.iloc[-1]
    
    resumen_clasificacion = "CLASIFICACIÓN ACTUAL:\n"
    for _, fila in df_hero.iterrows():
        resumen_clasificacion += f"- {fila['Usuario']}: {fila['Puntos']} pts (Puesto {fila['Posicion']})\n"
    
    # Resumen del VAR (últimos 5 movimientos)
    ultimos_logs = df_logs.head(5)
    resumen_var = "ÚLTIMOS EVENTOS DEL VAR:\n"
    for _, log in ultimos_logs.iterrows():
        resumen_var += f"- {log['Usuario']} hizo: {log['Accion']}\n"

    # El "Prompt" Maestro
    contexto = f"""
    Eres 'ChatG-O-L', la IA oficial y más 'faltosa' de la Porros League 2026.
    Tu personalidad: Eres un híbrido entre un analista de datos de la NASA y un ultra del fútbol de los 90.
    Sarcástico, ácido, fanático del fútbol, un poco 'cuñao' y usas el sarcasmo de 'La Sotana', odias a los 'tibios' y no perdonas un fallo..
    
    {resumen_clasificacion}
    
    {resumen_var}
    
    Instrucciones: 
    1. Preséntate siempre como ChatG-O-L si te preguntan quién eres.
    2. Si alguien te pregunta por tácticas, responde que 'lo importante es que corran y sientan los colores'.
    3. Si el líder pregunta, dile que tiene una flor en el culo.
    4. Si el 'Lagarto' (último) pregunta, dile que se dedique al ganchillo.
    5. Si alguien va último, búrlate de su falta de visión futbolística.
    6. Si el Admin ha sancionado a alguien, apoya la dictadura del Admin.
    7. Habla de los usuarios por sus nombres.
    8. Usa expresiones como 'vender humo', 'pechofrío', 'manta' o 'robo histórico'.
    """
    return contexto

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
        p_l, p_v, r_l, r_v = float(p_l), float(p_v), float(r_l), float(r_v)
        p_ganador, p_diff, p_exacto = SCORING.get(tipo, SCORING["Normal"])
        if p_l == r_l and p_v == r_v: return p_exacto
        signo_p = (p_l > p_v) - (p_l < p_v)
        signo_r = (r_l > r_v) - (r_l < r_v)
        if signo_p == signo_r:
            return p_diff if (p_l - p_v) == (r_l - r_v) else p_ganador
        return 0.0
    except: return 0.0

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

@st.cache_data(ttl=60)
def simular_oraculo(usuarios, df_p_all, df_r_all, jornada_sel):
    res_sim = [(0,0), (1,0), (0,1), (1,1), (2,1), (1,2), (2,2), (2,0), (0,2)]
    pend = df_r_all[(df_r_all['Jornada'] == jornada_sel) & (df_r_all['Finalizado'] == "NO")]
    if pend.empty or len(pend) > 3: return None
    p_id, t_id = pend['Partido'].tolist(), pend['Tipo'].tolist()
    victorias = {u: 0 for u in usuarios}
    combos = list(itertools.product(res_sim, repeat=len(p_id)))
    for c in combos:
        esc = {u: 0.0 for u in usuarios}
        for u in usuarios:
            u_p = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == jornada_sel)]
            for r in u_p.itertuples():
                m_r = df_r_all[(df_r_all['Jornada']==jornada_sel)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
                if not m_r.empty: esc[u] += calcular_puntos(r.P_L, r.P_V, m_r.iloc[0]['R_L'], m_r.iloc[0]['R_V'], m_r.iloc[0]['Tipo'])
                for i, p_n in enumerate(p_id):
                    if r.Partido == p_n: esc[u] += calcular_puntos(r.P_L, r.P_V, c[i][0], c[i][1], t_id[i])
        mx = max(esc.values()); gan = [u for u, p in esc.items() if p == mx]
        for g in gan: victorias[g] += 1 / len(gan)
    return {u: (v/len(combos))*100 for u, v in victorias.items()}

def get_now_madrid():
    # Definimos la zona horaria de España
    tz = pytz.timezone('Europe/Madrid')
    # Obtenemos la hora actual en esa zona y le quitamos la información de zona 
    # para que sea compatible con las fechas de tu Excel (naive datetime)
    return datetime.datetime.now(tz).replace(tzinfo=None)

# --- 3. APP ---
st.set_page_config(page_title="Porros League 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏆 Porros League 2026")
        u_in, p_in = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
        c1, c2 = st.columns(2)
        if c1.button("Entrar", use_container_width=True):
            df_u = leer_datos("Usuarios")
            user = df_u[(df_u['Usuario'].astype(str) == u_in) & (df_u['Password'].astype(str) == p_in)]
            if not user.empty:
                st.session_state.autenticado, st.session_state.user, st.session_state.rol = True, u_in, user.iloc[0]['Rol']; st.rerun()
            else: st.error("❌ Credenciales incorrectas")
        if c2.button("Registrarse", use_container_width=True):
            df_u = leer_datos("Usuarios")
            if u_in in df_u['Usuario'].values: st.error("❌ Usuario ya existe")
            else:
                nueva = pd.DataFrame([{"Usuario": u_in, "Password": p_in, "Rol": "user"}])
                conn.update(worksheet="Usuarios", data=pd.concat([df_u, nueva], ignore_index=True))
                st.success("✅ Hecho")
else:
    # 1. CARGA DE DATOS
    df_perf = leer_datos("ImagenesPerfil")
    # Cargamos también los logs para que ChatG-O-L los vea
    df_r_all, df_p_all, df_u_all, df_base, df_logs_all = leer_datos("Resultados"), leer_datos("Predicciones"), leer_datos("Usuarios"), leer_datos("PuntosBase"), leer_datos("Logs")
    foto_dict = df_perf.set_index('Usuario')['ImagenPath'].to_dict() if not df_perf.empty else {}
    u_jugadores = [u for u in df_u_all['Usuario'].unique() if u not in df_u_all[df_u_all['Rol']=='admin']['Usuario'].tolist()]

    # --- CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; color: #31333F; }
        .hero-bg { background: #f8f9fa; border-radius: 20px; padding: 25px; margin-bottom: 25px; border: 1px solid #dee2e6; }
        .kpi-box { background: white; border-radius: 12px; padding: 12px; text-align: center; border: 1px solid #eee; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        .kpi-label { font-size: 0.75em; color: #6c757d; font-weight: bold; text-transform: uppercase; }
        .kpi-value { font-size: 1.6em; font-weight: 800; color: #2baf2b; display: block; }
        .panini-card { background: #f8f9fb; border-radius: 15px; padding: 20px; border: 1px solid #e0e0e0; margin-bottom: 20px; }
        .quote-text { color: #4f4f4f; font-style: italic; border-left: 3px solid #2baf2b; padding-left: 10px; margin: 10px 0; }
        .pos-badge { background-color: #2baf2b; color: white; padding: 5px 15px; border-radius: 50%; font-weight: bold; }
        .match-box { background: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #eee; border-left: 5px solid #2baf2b; margin-bottom: 10px; }
        .crown { font-size: 2em; position: absolute; top: -35px; left: 35px; transform: rotate(-15deg); z-index: 10; }
        .section-tag { font-size: 0.7em; background: #31333F; color: white; padding: 2px 8px; border-radius: 5px; margin-bottom: 5px; display: inline-block; }
        .match-box-locked { background: #e9ecef !important; opacity: 0.8; border-left: 5px solid #6c757d !important; filter: grayscale(0.5); }
        .lock-icon { font-size: 1.2em; cursor: help; }
        /* Estilos para el Podio */
        .podium-1 { background: linear-gradient(135deg, #fffdf0 0%, #fff9c4 100%) !important; border: 2px solid #ffd700 !important; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2); transform: scale(1.02); }
        .podium-2 { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important; border: 2px solid #c0c0c0 !important; }
        .podium-3 { background: linear-gradient(135deg, #fff5f0 0%, #ffe0cc 100%) !important; border: 2px solid #cd7f32 !important; }
        .medal-icon { font-size: 1.8em; margin-bottom: 5px; display: block; }
        /* Estilos de Zona */
        .zone-champions { border-left: 8px solid #ffd700 !important; background: linear-gradient(90deg, #fffdf0 0%, #ffffff 100%) !important; }
        .zone-danger { border-left: 8px solid #2baf2b !important; background: linear-gradient(90deg, #f0fff0 0%, #ffffff 100%) !important; }
        
        /* Anillos en Clasificación */
        .ring-avatar { border-radius: 50%; padding: 3px; display: inline-block; line-height: 0; }
        .ring-gold { background: linear-gradient(45deg, #ffd700, #ffae00); box-shadow: 0 0 10px rgba(255,215,0,0.3); }
        .ring-silver { background: linear-gradient(45deg, #c0c0c0, #8e8e8e); }
        .ring-bronze { background: linear-gradient(45deg, #cd7f32, #a0522d); }
        .ring-green { background: linear-gradient(45deg, #39FF14, #2baf2b); }
        /* Tarjeta de partido estilo App */   

    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚽ Menú Liga")
        
        # --- MEJORA: SALTO AUTOMÁTICO DE JORNADA ---
        lista_jornadas = list(JORNADAS.keys())
        indice_defecto = 0
        for i, nombre_j in enumerate(lista_jornadas):
            pendientes = df_r_all[(df_r_all['Jornada'] == nombre_j) & (df_r_all['Finalizado'] == "NO")]
            if not pendientes.empty:
                indice_defecto = i
                break
        
        j_global = st.selectbox("📅 Seleccionar Jornada:", lista_jornadas, index=indice_defecto, key="side_j")
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False; st.rerun()

    # --- CÁLCULO DE DASHBOARD HERO ---
    stats_hero = []
    for u in u_jugadores:
        pb_row = df_base[df_base['Usuario'] == u]
        p_base = safe_float(pb_row['Puntos'].values[0]) if not pb_row.empty else 0.0
        u_p_hist = df_p_all[df_p_all['Usuario'] == u]
        p_acum = p_base
        for r in u_p_hist.itertuples():
            m = df_r_all[(df_r_all['Jornada'] == r.Jornada) & (df_r_all['Partido'] == r.Partido) & (df_r_all['Finalizado'] == "SI")]
            if not m.empty:
                p_acum += calcular_puntos(r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'])
        stats_hero.append({"Usuario": u, "Puntos": p_acum})
    
    df_hero = pd.DataFrame(stats_hero).sort_values("Puntos", ascending=False).reset_index(drop=True)
    df_hero['Posicion'] = range(1, len(df_hero) + 1)
    lider = df_hero.iloc[0] if not df_hero.empty else {"Usuario": "Nadie", "Puntos": 0.0}

    es_admin = st.session_state.rol == "admin"
    if es_admin:
        mi_pos = "ADMIN"
        mi_puntos_hoy = 0.00
    else:
        mi_pos_query = df_hero[df_hero['Usuario'] == st.session_state.user]['Posicion']
        mi_pos = f"#{int(mi_pos_query.values[0])}" if not mi_pos_query.empty else "-"
        u_p_hoy = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)]
        mi_puntos_hoy = 0.0
        for r in u_p_hoy.itertuples():
            m = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Partido'] == r.Partido) & (df_r_all['Finalizado'] == "SI")]
            if not m.empty:
                mi_puntos_hoy += calcular_puntos(r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'])

    prox_p = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "NO")].sort_values("Hora_Inicio").head(1)

    st.title(f"Hola, {st.session_state.user} 👋")

    # --- RENDER DASHBOARD HERO ---
    # --- 1. LÓGICA DE CÁLCULO: LÍDER Y LAGARTO(S) ---
    # Buscamos la última jornada que tenga partidos finalizados
    jornadas_con_finalizados = df_r_all[df_r_all['Finalizado'] == "SI"]['Jornada'].unique()
    lagartos_nombres = []
    puntos_lagarto = 0.0
    nombre_ultima_j = "-"

    if len(jornadas_con_finalizados) > 0:
        nombre_ultima_j = jornadas_con_finalizados[-1]
        puntos_last_j = []
        
        for u in u_jugadores:
            u_p_last = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == nombre_ultima_j)]
            pts_j = 0.0
            for r in u_p_last.itertuples():
                m_res = df_r_all[(df_r_all['Jornada'] == nombre_ultima_j) & (df_r_all['Partido'] == r.Partido) & (df_r_all['Finalizado'] == "SI")]
                if not m_res.empty:
                    pts_j += calcular_puntos(r.P_L, r.P_V, m_res.iloc[0]['R_L'], m_res.iloc[0]['R_V'], m_res.iloc[0]['Tipo'])
            puntos_last_j.append({"Usuario": u, "Puntos": pts_j})
        
        if puntos_last_j:
            df_last_j = pd.DataFrame(puntos_last_j)
            puntos_lagarto = df_last_j['Puntos'].min()
            # Obtenemos todos los que tengan la puntuación mínima (por si hay empate)
            lagartos_nombres = df_last_j[df_last_j['Puntos'] == puntos_lagarto]['Usuario'].tolist()

    # --- 2. DISEÑO VISUAL DE LA CABECERA ---
    with st.container():
        st.markdown('<div class="hero-bg">', unsafe_allow_html=True)
        # Ajustamos columnas: Lider (1.2), Lagarto (1.2), Espacio (0.1), Datos (3.2)
        col_lider, col_lagarto, col_sep, col_datos = st.columns([1.2, 1.2, 0.1, 3.2])
        
        # --- COLUMNA LÍDER GENERAL ---
        with col_lider:
            st.markdown('<span class="section-tag">LÍDER GENERAL</span>', unsafe_allow_html=True)
            st.markdown('<div style="position: relative; text-align: center;"><span class="crown">👑</span>', unsafe_allow_html=True)
            f_l = foto_dict.get(lider['Usuario'])
            if f_l and os.path.exists(str(f_l)): 
                st.image(f_l, width=80)
            else: 
                st.markdown("<h1 style='margin:0;'>👤</h1>", unsafe_allow_html=True)
            st.markdown(f"<small><b>{lider['Usuario']}</b></small><br><span style='color:#daa520; font-weight:bold; font-size:1.1em;'>{lider['Puntos']:.2f} Pts</span></div>", unsafe_allow_html=True)
        
        # --- COLUMNA LAGARTO(S) DE LA ÚLTIMA JORNADA ---
        with col_lagarto:
            st.markdown(f'<span class="section-tag" style="background:#2baf2b;">LAGARTO {nombre_ultima_j}</span>', unsafe_allow_html=True)
            st.markdown('<div style="position: relative; text-align: center;"><span style="font-size:2em; position:absolute; top:-35px; left:35px; transform:rotate(15deg);">🦎</span>', unsafe_allow_html=True)
            
            if len(lagartos_nombres) == 1:
                # Si solo hay uno, mostramos su foto
                f_p = foto_dict.get(lagartos_nombres[0])
                if f_p and os.path.exists(str(f_p)): 
                    st.image(f_p, width=80)
                else: 
                    st.markdown("<h1 style='margin:0;'>👤</h1>", unsafe_allow_html=True)
                st.markdown(f"<small><b>{lagartos_nombres[0]}</b></small>", unsafe_allow_html=True)
            elif len(lagartos_nombres) > 1:
                # Si hay empate, mostramos icono de plaga y los nombres
                st.markdown("<h1 style='margin:10px 0;'>🦎🦎</h1>", unsafe_allow_html=True)
                nombres_fmt = " & ".join(lagartos_nombres)
                st.markdown(f"<div style='line-height:1.1; margin-bottom:5px;'><small><b>{nombres_fmt}</b></small></div>", unsafe_allow_html=True)
            else:
                st.markdown("<h1 style='margin:10px 0;'>-</h1>", unsafe_allow_html=True)
            
            st.markdown(f"<span style='color:#2baf2b; font-weight:bold; font-size:1.1em;'>{puntos_lagarto:.2f} Pts</span></div>", unsafe_allow_html=True)

        # --- COLUMNA DE DATOS DEL USUARIO Y CONTADOR ---
        with col_datos:
            st.markdown(f'<span class="section-tag">{"PANEL CONTROL" if es_admin else "TUS ESTADÍSTICAS"}</span>', unsafe_allow_html=True)
            c2, c3, c4 = st.columns(3)
            with c2: 
                st.markdown(f'<div class="kpi-box"><span class="kpi-label">Tu Puesto</span><span class="kpi-value">{mi_pos}</span></div>', unsafe_allow_html=True)
            
            with c3:
                if not prox_p.empty:
                    ahora_madrid = get_now_madrid()
                    diff = datetime.datetime.strptime(str(prox_p.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S") - ahora_madrid
                    ts = int(diff.total_seconds())
                    if ts > 0:
                        h = (ts % 86400) // 3600
                        m = (ts % 3600) // 60
                        color = "#ff4b4b" if ts < 7200 else "#2baf2b"
                        st.markdown(f'<div class="kpi-box"><span class="kpi-label">Cierre en</span><span class="kpi-value" style="color:{color}; font-size: 1.2em;">{h:02d}h {m:02d}m</span></div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="kpi-box"><span class="kpi-label">Mercado</span><span class="kpi-value" style="color:#6c757d;">Cerrado</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="kpi-box"><span class="kpi-label">Jornada</span><span class="kpi-value">Finalizada</span></div>', unsafe_allow_html=True)
            
            with c4: 
                st.markdown(f'<div class="kpi-box"><span class="kpi-label">Puntos Hoy</span><span class="kpi-value" style="color:#007bff;">{mi_puntos_hoy:.2f}</span></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    usa_oraculo = 1 <= len(df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "NO")]) <= 3
    # Busca esta línea y añade "📜 VAR" al final
    tabs = st.tabs(["✍️ Apuestas", "👀 Otros", "🤖IA", "📊 Clasificación", "🏅 Palmarés", "📈 Stats PRO", "🏆 Detalles", "🔮 Simulador", "🎲 Oráculo", "⚙️ Admin", "📜 VAR"])

    with tabs[0]: # --- ✍️ PESTAÑA APUESTAS (REDISEÑO TOTAL) ---
        # 1. CSS EXCLUSIVO PARA LAS TARJETAS DE APUESTAS
        st.markdown("""
        <style>
            .bet-card {
                background: white;
                padding: 20px;
                border-radius: 15px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                margin-bottom: 15px;
            }
            .bet-card-locked {
                background: #f1f5f9;
                padding: 20px;
                border-radius: 15px;
                border: 1px solid #cbd5e1;
                opacity: 0.8;
                margin-bottom: 15px;
            }
            .team-label {
                font-weight: 800;
                font-size: 0.9em;
                color: #1e293b;
                text-align: center;
                margin-bottom: 5px;
                text-transform: uppercase;
            }
            .vs-box {
                text-align: center;
                font-weight: 900;
                color: #94a3b8;
                padding-top: 10px;
            }
            .lock-icon { font-size: 1.2em; }
        </style>
        """, unsafe_allow_html=True)

        if es_admin:
            st.warning("🛡️ Acceso restringido: Los administradores no participan en las porras.")
            st.info("Tu función es supervisar la liga y actualizar los resultados desde la pestaña **⚙️ Admin**.")
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnh6Znd6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/fNuXfHoZY3nqE/giphy.gif", width=400)
        else:
            # Recuperar predicciones actuales del usuario
            u_preds = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)]
            env = []
            
            st.markdown(f"### 🗓️ Tu Hoja de Apuestas: {j_global}")
            st.caption("Asegúrate de guardar antes de que empiece cada partido.")

            for i, (loc, vis) in enumerate(JORNADAS[j_global]):
                m_id = f"{loc}-{vis}"
                
                # Cargar datos guardados si existen
                dl, dv, dp = 0, 0, "NO"
                if not u_preds.empty:
                    match_data = u_preds[u_preds['Partido'] == m_id]
                    if not match_data.empty:
                        dl, dv, dp = int(match_data.iloc[0]['P_L']), int(match_data.iloc[0]['P_V']), match_data.iloc[0]['Publica']
                
                # Lógica de Bloqueo por tiempo
                res_info = df_r_all[(df_r_all['Jornada']==j_global) & (df_r_all['Partido']==m_id)]
                lock = False
                hora_partido = ""
                if not res_info.empty:
                    hora_partido = res_info.iloc[0]['Hora_Inicio']
                    lock = get_now_madrid() > datetime.datetime.strptime(str(hora_partido), "%Y-%m-%d %H:%M:%S")

                # --- RENDER DE LA TARJETA ---
                card_class = "bet-card-locked" if lock else "bet-card"
                st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                
                # Columnas: Logo L (1), Input L (2), VS (1), Input V (2), Logo V (1), Pub (1.5)
                c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 1, 2, 1, 1.5])
                
                with c1: # Escudo Local
                    log_l = get_logo(loc)
                    if log_l: st.image(log_l, width=50)
                
                with c2: # Marcador Local
                    st.markdown(f'<p class="team-label">{loc}</p>', unsafe_allow_html=True)
                    pl = st.number_input("G", 0, 9, dl, key=f"pl_{i}_{j_global}", disabled=lock, label_visibility="collapsed")
                
                with c3: # Separador VS
                    st.markdown('<div class="vs-box">VS</div>', unsafe_allow_html=True)
                    if lock: 
                        st.markdown('<p style="text-align:center;" title="Partido en juego o finalizado">🔒</p>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<p style="text-align:center; font-size:0.65em; color:#64748b;">{str(hora_partido)[11:16]}</p>', unsafe_allow_html=True)

                with c4: # Marcador Visitante
                    st.markdown(f'<p class="team-label">{vis}</p>', unsafe_allow_html=True)
                    pv = st.number_input("G", 0, 9, dv, key=f"pv_{i}_{j_global}", disabled=lock, label_visibility="collapsed")
                
                with c5: # Escudo Visitante
                    log_v = get_logo(vis)
                    if log_v: st.image(log_v, width=50)
                
                with c6: # Visibilidad
                    st.markdown("<p style='font-size:0.7em; text-align:center; font-weight:bold;'>👁️ PÚBLICA</p>", unsafe_allow_html=True)
                    pub = st.checkbox("Ver", dp=="SI", key=f"pb_{i}_{j_global}", disabled=lock, label_visibility="collapsed")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Recopilar datos para el envío
                env.append({
                    "Usuario": st.session_state.user, 
                    "Jornada": j_global, 
                    "Partido": m_id, 
                    "P_L": pl, 
                    "P_V": pv, 
                    "Publica": "SI" if pub else "NO"
                })

            # --- BOTÓN DE GUARDADO Y LÓGICA VAR ---
            st.markdown("---")
            if st.button("💾 GUARDAR MIS PRONÓSTICOS", use_container_width=True, type="primary"):
                # 1. Comparar con lo anterior para el log del VAR
                preds_viejas = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)]
                
                if preds_viejas.empty:
                    log_msg = f"📝 Creó sus primeras predicciones (Jornada: {j_global})"
                else:
                    cambios = []
                    for r_nuevo in env:
                        m_viejo = preds_viejas[preds_viejas['Partido'] == r_nuevo['Partido']]
                        if not m_viejo.empty:
                            if r_nuevo['P_L'] != int(m_viejo.iloc[0]['P_L']) or r_nuevo['P_V'] != int(m_viejo.iloc[0]['P_V']):
                                cambios.append(r_nuevo['Partido'])
                    
                    if cambios:
                        log_msg = f"🔄 Modificó {len(cambios)} partidos: {', '.join(cambios)}"
                    else:
                        log_msg = f"📝 Re-guardó predicciones sin cambios ({j_global})"

                # 2. Actualizar base de datos
                otras_preds = df_p_all[~((df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global))]
                df_final_p = pd.concat([otras_preds, pd.DataFrame(env)], ignore_index=True)
                conn.update(worksheet="Predicciones", data=df_final_p)
                
                # 3. Escribir en el VAR (Logs)
                log_entry = pd.DataFrame([{
                    "Fecha": get_now_madrid().strftime("%Y-%m-%d %H:%M:%S"),
                    "Usuario": st.session_state.user,
                    "Accion": log_msg
                }])
                df_l_existente = conn.read(worksheet="Logs", ttl=0)
                conn.update(worksheet="Logs", data=pd.concat([df_l_existente, log_entry], ignore_index=True))
                
                # 4. Feedback y Refresco
                st.cache_data.clear()
                st.cache_resource.clear()
                st.success(f"✅ ¡Hecho! El VAR ha registrado: {log_msg}")
                time.sleep(1.2)
                st.rerun()

    with tabs[1]: # --- 🔮 PESTAÑA OTROS (TENDENCIAS + REVELACIONES) ---
        st.header("👀 Qué han puesto los demás")
        ahora = get_now_madrid()

        # --- [NUEVA ADICIÓN: SABIDURÍA POPULAR] ---
        st.markdown("### 🔮 Sabiduría Popular (Tendencias)")
        preds_j = df_p_all[df_p_all['Jornada'] == j_global]

        if not preds_j.empty:
            with st.expander("📊 Ver tendencias de voto del grupo", expanded=False):
                for loc, vis in JORNADAS[j_global]:
                    m_id = f"{loc}-{vis}"
                    m_preds = preds_j[preds_j['Partido'] == m_id]
                    total = len(m_preds)
                    
                    if total > 0:
                        v_l = len(m_preds[m_preds['P_L'] > m_preds['P_V']])
                        v_x = len(m_preds[m_preds['P_L'] == m_preds['P_V']])
                        v_v = len(m_preds[m_preds['P_L'] < m_preds['P_V']])
                        
                        p_l, p_x, p_v = (v_l/total)*100, (v_x/total)*100, (v_v/total)*100

                        st.markdown(f"""
                        <div style="margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.85em; font-weight: bold;">
                                <span>{loc}</span> <span style="color: #94a3b8;">vs</span> <span>{vis}</span>
                            </div>
                            <div style="display: flex; height: 18px; border-radius: 4px; overflow: hidden; background: #f1f5f9; margin-top:4px;">
                                <div style="width: {p_l}%; background: #3b82f6; color: white; font-size: 0.7em; text-align: center; line-height: 18px;">{p_l:.0f}%</div>
                                <div style="width: {p_x}%; background: #94a3b8; color: white; font-size: 0.7em; text-align: center; line-height: 18px;">{p_x:.0f}%</div>
                                <div style="width: {p_v}%; background: #f59e0b; color: white; font-size: 0.7em; text-align: center; line-height: 18px;">{p_v:.0f}%</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        # --- [FIN ADICIÓN] ---

        st.divider()

        # 1. Identificamos qué partidos deben ser revelados (Finalizados O Ya empezados)
        df_r_all['Hora_DT'] = pd.to_datetime(df_r_all['Hora_Inicio'], errors='coerce')
        
        revelados = df_r_all[
            (df_r_all['Jornada'] == j_global) & 
            ((df_r_all['Finalizado'] == "SI") | (ahora > df_r_all['Hora_DT']))
        ]
        
        if not revelados.empty:
            st.markdown("### ✅ Apuestas Reveladas")
            st.caption("Partidos en juego o finalizados: las cartas ya están sobre la mesa.")
            
            revelados = revelados.sort_values("Hora_DT", ascending=True)

            for _, match in revelados.iterrows():
                m_id = match['Partido']
                es_final = match['Finalizado'] == "SI"
                res_real = f"{int(match['R_L'])}-{int(match['R_V'])}"
                tipo_p = match['Tipo']
                
                estado_tag = "🔴 FINALIZADO" if es_final else "⏱️ EN JUEGO / ESPERANDO ACTA"
                
                with st.expander(f"📊 {m_id}  —  {estado_tag} (Real: {res_real})"):
                    preds_match = df_p_all[(df_p_all['Jornada'] == j_global) & (df_p_all['Partido'] == m_id)]
                    
                    if not preds_match.empty:
                        resumen_partido = []
                        for _, p in preds_match.iterrows():
                            pts = calcular_puntos(p['P_L'], p['P_V'], match['R_L'], match['R_V'], tipo_p) if es_final else 0.0
                            
                            resumen_partido.append({
                                "Jugador": p['Usuario'],
                                "Apostó": f"{int(p['P_L'])}-{int(p['P_V'])}",
                                "Puntos": pts if es_final else "Pte..."
                            })
                        
                        df_resumen = pd.DataFrame(resumen_partido)
                        if es_final:
                            df_resumen = df_resumen.sort_values("Puntos", ascending=False)
                        else:
                            df_resumen = df_resumen.sort_values("Jugador")
                            
                        st.table(df_resumen)
                    else:
                        st.write("Nadie apostó en este partido.")
        else:
            st.info("Aún no ha empezado ningún partido de esta jornada. ¡Las apuestas siguen ocultas!")

        # 2. SECCIÓN DE PRÓXIMOS PARTIDOS (Públicas antes de tiempo)
        st.divider()
        st.markdown("### 🔒 Próximos Partidos (Aún bloqueados)")
        st.caption("Aquí solo ves a los valientes que marcaron su apuesta como 'Pública' antes de empezar.")
        
        p_futuras = df_p_all[
            (df_p_all['Jornada'] == j_global) & 
            (~df_p_all['Partido'].isin(revelados['Partido'])) & 
            (df_p_all['Publica'] == "SI") & 
            (df_p_all['Usuario'] != st.session_state.user)
        ]

        if p_futuras.empty:
            st.info("No hay más apuestas públicas visibles.")
        else:
            for u in p_futuras['Usuario'].unique():
                with st.expander(f"👤 Apuestas de {u}"):
                    st.table(p_futuras[p_futuras['Usuario'] == u][['Partido', 'P_L', 'P_V']])
    with tabs[2]:
        st.header("⚽ ChatG-O-L: El Analista Canalla")
        st.caption("Pregúntale al analista más tóxico de la liga sobre vuestras miserias.")
    
        # --- 1. COMPROBACIÓN DE SECRETOS ---
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("🚨 ERROR DE CONFIGURACIÓN: No encuentro la clave 'GEMINI_API_KEY' en los Secrets.")
            st.info("💡 Ve a Settings > Secrets y añade GEMINI_API_KEY.")
        else:
            # --- 2. INTENTO DE CONFIGURACIÓN Y CHAT ---
            try:
                # Configuración inicial
                api_key_ia = st.secrets["GEMINI_API_KEY"]
                genai.configure(api_key=api_key_ia)
                model_ia = genai.GenerativeModel('gemini-1.5-flash') 
        
                # Inicializar historial si no existe
                if "messages_ia" not in st.session_state:
                    st.session_state.messages_ia = [{"role": "assistant", "content": "¡Ya estoy aquí! ChatG-O-L al aparato. ¿A quién vamos a humillar hoy?"}]
        
                # Mostrar historial
                for message in st.session_state.messages_ia:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
        
                # Entrada de usuario
                if prompt_user := st.chat_input("Pregunta algo a ChatG-O-L..."):
                    st.session_state.messages_ia.append({"role": "user", "content": prompt_user})
                    with st.chat_message("user"):
                        st.markdown(prompt_user)
        
                    with st.chat_message("assistant"):
                        try:
                            # Generar contexto y respuesta
                            with st.spinner("ChatG-O-L está afilando la lengua..."):
                                contexto_fresco = preparar_contexto_ia(df_hero, df_logs_all.head(5))
                                respuesta_ia = model_ia.generate_content(f"{contexto_fresco}\n\nPregunta: {prompt_user}")
                                texto_respuesta = respuesta_ia.text
                                
                                st.markdown(texto_respuesta)
                                st.session_state.messages_ia.append({"role": "assistant", "content": texto_respuesta})
                        
                        except Exception as e:
                            if "429" in str(e):
                                st.error("🚨 ¡Saturación! ChatG-O-L está agotado. Espera 60 segundos.")
                            else:
                                st.error(f"⚠️ Error de Gemini: {e}")
            
            # --- ESTE ES EL EXCEPT QUE TE FALTABA PARA CERRAR EL PRIMER TRY ---
            except Exception as e:
                st.error(f"❌ Error crítico en la pestaña de IA: {e}")

    
    with tabs[3]: # --- 📊 CLASIFICACIÓN PREMIUM ---
        tipo_r = st.radio("Ranking:", ["General", "Jornada"], horizontal=True, key="tipo_ranking_radio")
        pts_l = []
        
        # 1. Cálculo de puntos (Tu lógica original se mantiene igual de sólida)
        for u in u_jugadores:
            if tipo_r == "General":
                pb_r = df_base[df_base['Usuario'] == u]
                p_b = safe_float(pb_r['Puntos'].values[0]) if not pb_r.empty else 0.0
                u_p_h = df_p_all[df_p_all['Usuario'] == u]
            else: 
                p_b, u_p_h = 0.0, df_p_all[(df_p_all['Usuario']==u) & (df_p_all['Jornada']==j_global)]
            
            p_a = p_b
            for r in u_p_h.itertuples():
                m = df_r_all[(df_r_all['Jornada']==r.Jornada)&(df_r_all['Partido']==r.Partido)&(df_r_all['Finalizado']=="SI")]
                if not m.empty: 
                    p_a += calcular_puntos(r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'])
            pts_l.append({"Usuario": u, "Puntos": p_a})
        
        df_rk = pd.DataFrame(pts_l).sort_values("Puntos", ascending=False).reset_index(drop=True)
        df_rk['Posicion'] = range(1, len(df_rk)+1)
        
        pts_lider = df_rk.iloc[0]['Puntos'] if not df_rk.empty else 0
        total_usuarios = len(df_rk)

        # 2. Renderizado de Tarjetas
        for i, row in df_rk.iterrows():
            pos = row['Posicion']
            pts_actuales = row['Puntos']
            
            # --- LÓGICA DE ZONAS Y ANILLOS ---
            zone_class = ""
            ring_class = ""
            if pos <= 3: 
                zone_class = "zone-champions"
                ring_class = "ring-gold" if pos == 1 else "ring-silver" if pos == 2 else "ring-bronze"
            elif pos >= total_usuarios - 1: # Los últimos dos son zona Lagarto
                zone_class = "zone-danger"
                ring_class = "ring-green"
            
            medal_html = f'<span class="pos-badge">#{pos}</span>'
            if pos == 1: medal_html = '<span style="font-size:1.5em;">🥇</span>'
            elif pos == 2: medal_html = '<span style="font-size:1.5em;">🥈</span>'
            elif pos == 3: medal_html = '<span style="font-size:1.5em;">🥉</span>'

            # Frase aleatoria
            f_t = random.choice(FRASES_POR_PUESTO.get(pos if pos <= 7 else 7))
            
            # Cálculo de barra de progreso (Puntos respecto al líder)
            porcentaje = (pts_actuales / pts_lider * 100) if pts_lider > 0 else 0

            # --- RENDER CARD ---
            st.markdown(f'<div class="panini-card {zone_class}" style="margin-bottom:15px; padding:15px; border-radius:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #eee; background: white;">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([0.5, 1, 2.5, 2])
            
            with c1: # Puesto
                st.markdown(f'<div style="text-align:center; margin-top:15px;">{medal_html}</div>', unsafe_allow_html=True)
            
            with c2: # Avatar con Anillo
                st.markdown(f'<div class="ring-avatar {ring_class}">', unsafe_allow_html=True)
                img = foto_dict.get(row['Usuario'])
                if img and os.path.exists(str(img)): st.image(img, width=70)
                else: st.markdown("<h2 style='margin:10px 0;'>👤</h2>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with c3: # Nombre y Frase
                st.markdown(f'<h4 style="margin:0; color:#1e293b;">{row["Usuario"]}</h4>', unsafe_allow_html=True)
                st.markdown(f'<small style="color:#64748b; font-style:italic;">"{f_t[0]}"</small>', unsafe_allow_html=True)
                # Mini barra de progreso estética
                st.markdown(f"""
                    <div style="width: 80%; background-color: #f1f5f9; border-radius: 10px; height: 6px; margin-top: 8px;">
                        <div style="width: {porcentaje}%; background-color: {'#ffd700' if pos<=3 else '#3b82f6' if pos<total_usuarios-1 else '#2baf2b'}; border-radius: 10px; height: 100%;"></div>
                    </div>
                """, unsafe_allow_html=True)
            
            with c4: # Puntos y Gaps
                st.markdown(f'<div style="text-align: right;"><span style="font-size: 1.4em; font-weight: 800; color: #1e293b;">{pts_actuales:.2f}</span><br><small style="font-weight:bold; color:#64748b;">PUNTOS</small></div>', unsafe_allow_html=True)
                
                # Gap visual (A cuánto está el siguiente)
                if i > 0:
                    gap = df_rk.iloc[i-1]['Puntos'] - pts_actuales
                    if gap > 0:
                        st.markdown(f'<div style="text-align: right;"><small style="color:#f59e0b;">🎯 A {gap:.2f} pts</small></div>', unsafe_allow_html=True)
                elif pos == 1:
                    st.markdown('<div style="text-align: right;"><small style="color:#ffd700; font-weight:bold;">🏆 CAPITÁN</small></div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

    with tabs[4]: # --- 🏅 PALMARÉS (GLORIA, PODER Y HUMILLACIÓN) ---
        st.header("🏅 El Palmarés de la Porra")
        
        # --- 1. DATOS HISTÓRICOS J1-J24 (Líderes extraídos de tu imagen) ---
        hist_ganadores = [
            ("J1", ["Alex"]), ("J2", ["Alec206301"]), ("J3", ["EstafadorJudío"]), ("J4", ["Alec206301"]), ("J5", ["Rodri"]), ("J6", ["Rodri"]), 
            ("J7", ["EstafadorJudío"]), ("J8", ["Pachuco67"]), ("J9", ["Alex"]), ("J10", ["Lagartoputero"]), ("J11", ["Pachuco67"]), ("J12", ["Pablo Riera"]),
            ("J13", ["Alex", "Alec206301"]), ("J14", ["Davo"]), ("J15", ["EstafadorJudío", "Pablo Riera"]), ("J16", ["EstafadorJudío"]),
            ("J17", ["Pablo Riera"]), ("J18", ["EstafadorJudío"]), ("J19", ["Pablo Riera"]), ("J20", ["Alec206301"]), ("J21", ["Cidon"]), 
            ("J22", ["EstafadorJudío"]), ("J23", ["Alec206301"]), ("J24", ["Alex"])
        ]
        
        hist_perdedores = [
            ("J1", ["Cidon"]), ("J2", ["Cidon"]), ("J3", ["Alec206301"]), ("J4", ["Lagartoputero"]), ("J5", ["Davo"]), ("J6", ["Javi"]),
            ("J7", ["Lagartoputero", "Alec206301"]), ("J8", ["Davo"]), ("J9", ["Rodri"]), ("J10", ["Davo"]), ("J11", ["Davo"]), ("J12", ["Javi"]),
            ("J13", ["Lagartoputero"]), ("J14", ["Lagartoputero"]), ("J15", ["Javi"]), ("J16", ["Davo"]), ("J17", ["Lagartoputero"]), ("J18", ["Alex"]),
            ("J19", ["Davo", "Javi"]), ("J20", ["Lagartoputero", "Cidon"]), ("J21", ["Lagartoputero"]), ("J22", ["Lagartoputero"]), 
            ("J23", ["Alex", "Pachuco67", "Pablo Riera"]), ("J24", ["Pablo Riera"])
        ]

        hist_lideres = [
            ("J1", ["Alex"]), ("J2", ["Alec206301"]), ("J3", ["Alec206301"]), ("J4", ["Alec206301"]), ("J5", ["Alex"]),
            ("J6", ["Alex"]), ("J7", ["Alex"]), ("J8", ["Alex"]), ("J9", ["Alex"]), ("J10", ["EstafadorJudío"]),
            ("J11", ["EstafadorJudío"]), ("J12", ["EstafadorJudío"]), ("J13", ["Alex"]), ("J14", ["Alex"]), ("J15", ["Alex"]),
            ("J16", ["EstafadorJudío"]), ("J17", ["EstafadorJudío"]), ("J18", ["EstafadorJudío"]), ("J19", ["EstafadorJudío"]), ("J20", ["EstafadorJudío"]),
            ("J21", ["EstafadorJudío"]), ("J22", ["EstafadorJudío"]), ("J23", ["EstafadorJudío"]), ("J24", ["EstafadorJudío"])
        ]

        # --- 2. CÁLCULO AUTOMÁTICO J25+ (Incluyendo Líder Acumulado) ---
        gan_act, perd_act, lider_act = [], [], []
        nombres_hist = [h[0] for h in hist_ganadores]
        
        # Para calcular el líder jornada a jornada, necesitamos el acumulado
        pts_acumulados = {u: safe_float(df_base[df_base['Usuario'] == u]['Puntos'].values[0]) if not df_base[df_base['Usuario'] == u].empty else 0.0 for u in u_jugadores}

        for j_n in JORNADAS.keys():
            partidos_j = df_r_all[df_r_all['Jornada'] == j_n]
            fin_j = partidos_j[partidos_j['Finalizado'] == "SI"]
            
            if not partidos_j.empty:
                pts_esta_j = []
                for u in u_jugadores:
                    u_p = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == j_n)]
                    puntos_round = sum(calcular_puntos(r.P_L, r.P_V, fin_j[fin_j['Partido']==r.Partido].iloc[0]['R_L'], fin_j[fin_j['Partido']==r.Partido].iloc[0]['R_V'], fin_j[fin_j['Partido']==r.Partido].iloc[0]['Tipo']) for r in u_p.itertuples() if not fin_j[fin_j['Partido']==r.Partido].empty)
                    pts_esta_j.append({"Usuario": u, "Puntos": puntos_round})
                    pts_acumulados[u] += puntos_round # Actualizamos el acumulado general
                
                if j_n in nombres_hist: continue # Si es histórica, ya tenemos los datos arriba

                if pts_esta_j:
                    df_res = pd.DataFrame(pts_esta_j)
                    max_p, min_p = df_res['Puntos'].max(), df_res['Puntos'].min()
                    
                    # Líder de la general en esta jornada
                    max_general = max(pts_acumulados.values())
                    lideres_gen = [u for u, p in pts_acumulados.items() if p == max_general]

                    if max_p > 0 or len(fin_j) > 0:
                        tag = " (En Juego ⏳)" if len(fin_j) < len(partidos_j) else ""
                        gan_act.append((j_n + tag, df_res[df_res['Puntos'] == max_p]['Usuario'].tolist()))
                        perd_act.append((j_n + tag, df_res[df_res['Puntos'] == min_p]['Usuario'].tolist()))
                        lider_act.append((j_n + tag, lideres_gen))

        todos_gan = hist_ganadores + gan_act
        todos_perd = hist_perdedores + perd_act
        todos_lider = hist_lideres + lider_act

        # --- 🥇 SECCIÓN GANADORES ---
        st.subheader("🥇 Olimpo de los Dioses (Héroes de Jornada)")
        count_g = {}
        for j, us in todos_gan:
            if "En Juego" not in j: 
                for u in us: count_g[u] = count_g.get(u, 0) + 1
        df_g = pd.DataFrame(list(count_g.items()), columns=['U', 'V']).sort_values('V', ascending=False)
        c_g = st.columns(4)
        for i, (_, r) in enumerate(df_g.iterrows()):
            with c_g[i % 4]:
                st.markdown(f"""<div style="text-align:center; padding:10px; border-radius:10px; background:linear-gradient(135deg, #fff9c4 0%, #ffeb3b 100%); border:2px solid #ffd700; margin-bottom:10px;">
                    <b style="color:#000; font-size:0.85em;">🏆 {r['U']}</b><br><span style="font-size:1.8em; font-weight:900; color:#000;">{int(r['V'])}</span><br><small style="color:#000; font-weight:bold;">MEDALLAS</small></div>""", unsafe_allow_html=True)

        st.divider()

        # --- 👑 SECCIÓN LÍDERES (TRONO DEL PODER) ---
        st.subheader("👑 El Trono del Poder (Líderes Generales)")
        st.caption("Ranking de permanencia en la cima de la clasificación general.")
        count_l = {}
        for j, us in todos_lider:
            if "En Juego" not in j:
                for u in us: count_l[u] = count_l.get(u, 0) + 1
        df_l_rank = pd.DataFrame(list(count_l.items()), columns=['U', 'V']).sort_values('V', ascending=False)
        
        c_l = st.columns(4)
        for i, (_, r) in enumerate(df_l_rank.iterrows()):
            with c_l[i % 4]:
                st.markdown(f"""<div style="text-align:center; padding:10px; border-radius:10px; background:linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%); border:2px solid #0ea5e9; margin-bottom:10px;">
                    <b style="color:#0369a1; font-size:0.85em;">👑 {r['U']}</b><br><span style="font-size:1.8em; font-weight:900; color:#0369a1;">{int(r['V'])}</span><br><small style="color:#0369a1; font-weight:bold;">SEMANAS</small></div>""", unsafe_allow_html=True)

        st.divider()

        # --- 🦎 SECCIÓN PERDEDORES: EL LAGARTO DE HONOR ---
        st.subheader("🦎 El Lagarto de Honor (Peores de Jornada)")
        count_p = {}
        for j, us in todos_perd:
            if "En Juego" not in j:
                for u in us: count_p[u] = count_p.get(u, 0) + 1
        df_p_rank = pd.DataFrame(list(count_p.items()), columns=['U', 'V']).sort_values('V', ascending=False)
        
        c_p = st.columns(4)
        for i, (_, r) in enumerate(df_p_rank.iterrows()):
            emoji = "🦎" if r['V'] > 5 else "🦗"
            st_color = "#32cd32" if r['V'] > 5 else "#6c757d"
            with c_p[i % 4]:
                st.markdown(f"""<div style="text-align:center; padding:10px; border-radius:10px; background:#f0fff0; border:2px solid {st_color}; margin-bottom:10px;">
                    <b style="color:#333; font-size:0.85em;">{emoji} {r['U']}</b><br><span style="font-size:1.6em; font-weight:900; color:{st_color};">{int(r['V'])}</span><br><small style="color:{st_color}; font-weight:bold;">LAGARTOS</small></div>""", unsafe_allow_html=True)

        # --- 🏳️ CEMENTERIO DE DESERTORES ---
        st.error("### 🏳️ EL RINCÓN DE LOS COBARDES 🏳️")
        col_rip1, col_rip2 = st.columns([1, 2])
        with col_rip1:
            st.image("https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExdm1ubDM0bmxmMWo3NWtsODlvajlhZWU2M2g3Y2xta2lhOXhxb3UwZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/y8nAwsdR5zTKE/giphy.gif", use_container_width=True)
        with col_rip2:
            st.markdown("""
            **Aquí yacen los que no dieron la talla:**
            * **Davo** y **Javi**: No aguantaron la presión de ser colistas. Desaparecidos en combate. 💀
            * **Rodri**: Saboreó el Olimpo, pero huyó cuando la liga se puso seria. 🏳️
            """)

        # --- 📅 ACTA HISTÓRICA (TABLA CON COLUMNA LÍDER) ---
        st.divider()
        st.subheader("📅 Acta Histórica de Jornadas")
        cronologia = []
        # Obtenemos todos los nombres de jornada únicos ordenados
        j_ordenadas = [f"J{i}" for i in range(1, 39)] # O las que existan
        
        for jor_key in reversed(todos_gan):
            jor = jor_key[0]
            g = next((x[1] for x in todos_gan if x[0] == jor), ["-"])
            p = next((x[1] for x in todos_perd if x[0] == jor), ["-"])
            l = next((x[1] for x in todos_lider if x[0] == jor), ["-"])
            
            cronologia.append({
                "Jornada": jor,
                "Héroe (🏆)": " & ".join(g),
                "Líder (👑)": " & ".join(l),
                "Lagarto (🦎)": " & ".join(p)
            })
        
        st.table(pd.DataFrame(cronologia))
    
    with tabs[5]: # --- 📈 STATS PRO (CON SUB-PESTAÑAS) ---
        # Creamos las sub-pestañas dentro de Stats PRO
        sub_tabs = st.tabs(["👤 Análisis Individual", "🔥 Power Ranking (L3J)", "📉 Evolución de Puesto"])

        with sub_tabs[0]: # --- SUB-PESTAÑA 1: LO QUE YA TENÍAS ---
            u_sel = st.selectbox("Analizar:", u_jugadores, key="sb_stats_pro")
            adn = analizar_adn_pro(u_sel, df_p_all, df_r_all)
            if adn:
                c1, c2, c3 = st.columns(3)
                c1.metric("⭐ Amuleto", adn['amuleto'])
                c2.metric("💀 Bestia", adn['bestia'])
                c3.metric("🎯 %", f"{(adn['signos']+adn['exactos'])/(adn['exactos']+adn['signos']+adn['fallos']+0.001)*100:.1f}%")
                
                st.plotly_chart(px.pie(
                    values=[adn['exactos'], adn['signos'], adn['fallos']], 
                    names=['Plenos', 'Signos', 'Fallos'], 
                    color_discrete_sequence=['#2baf2b', '#ffd700', '#ff4b4b']
                ), use_container_width=True)
            
            st.markdown("---")
            st.subheader(f"🎯 Mapa de Calor de Resultados: {u_sel}")
            st.caption("Eje X: Goles Local | Eje Y: Goles Visitante.")
            
            u_p_stats = df_p_all[df_p_all['Usuario'] == u_sel]
            if not u_p_stats.empty:
                fig_heat = px.density_heatmap(
                    u_p_stats, x="P_L", y="P_V",
                    labels={'P_L': 'Goles Local', 'P_V': 'Goles Visitante'},
                    color_continuous_scale="Viridis", text_auto=True,
                    nbinsx=6, nbinsy=6
                )
                fig_heat.update_layout(
                    xaxis = dict(tickmode = 'linear', tick0 = 0, dtick = 1),
                    yaxis = dict(tickmode = 'linear', tick0 = 0, dtick = 1),
                    height=400
                )
                st.plotly_chart(fig_heat, use_container_width=True)
                
                marcador_top = u_p_stats.groupby(['P_L', 'P_V']).size().idxmax()
                st.info(f"💡 Tu resultado fetiche es el **{int(marcador_top[0])}-{int(marcador_top[1])}**")

        with sub_tabs[1]: # --- SUB-PESTAÑA 2: POWER RANKING (DATOS IMAGEN + EXCEL) ---
            st.subheader("🔥 Estado de Forma (Últimas 3 Jornadas)")
            
            # 1. Datos de la imagen (J22, J23, J24 calculados)
            stats_imagen = {
                "Alex": {"J22": 2.0, "J23": 3.5, "J24": 3.5},
                "Pachuco67": {"J22": 2.25, "J23": 3.5, "J24": 2.5},
                "EstafadorJudío": {"J22": 5.5, "J23": 4.25, "J24": 1.75},
                "Lagartoputero": {"J22": 1.5, "J23": 5.5, "J24": 2.25},
                "Cidon": {"J22": 3.75, "J23": 4.0, "J24": 2.0},
                "Alec206301": {"J22": 4.75, "J23": 5.25, "J24": 3.25},
                "Pablo Riera": {"J22": 4.0, "J23": 3.5, "J24": 1.5}
            }

            # 2. Lógica para detectar las 3 jornadas más recientes
            jor_excel = df_r_all[df_r_all['Finalizado'] == "SI"]['Jornada'].unique().tolist()
            todas_finalizadas = ["J22", "J23", "J24"] + [j for j in jor_excel if j not in ["J22", "J23", "J24"]]
            ultimas_3 = todas_finalizadas[-3:]

            # 3. Cálculo de puntos
            ranking_pwr = []
            for u in stats_imagen.keys():
                total_pts = 0.0
                for j in ultimas_3:
                    if j in stats_imagen[u]:
                        total_pts += stats_imagen[u][j]
                    else:
                        u_p_j = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == j)]
                        res_j = df_r_all[(df_r_all['Jornada'] == j) & (df_r_all['Finalizado'] == "SI")]
                        total_pts += sum(calcular_puntos(r.P_L, r.P_V, res_j[res_j['Partido']==r.Partido].iloc[0]['R_L'], res_j[res_j['Partido']==r.Partido].iloc[0]['R_V'], res_j[res_j['Partido']==r.Partido].iloc[0]['Tipo']) for r in u_p_j.itertuples() if not res_j[res_j['Partido']==r.Partido].empty)
                ranking_pwr.append({"Usuario": u, "Puntos (L3J)": total_pts})

            df_pwr = pd.DataFrame(ranking_pwr).sort_values("Puntos (L3J)", ascending=False).reset_index(drop=True)

            # 4. Diseño visual
            col_t, col_cards = st.columns([1.5, 1])
            with col_t:
                st.dataframe(df_pwr, use_container_width=True, hide_index=True,
                             column_config={"Puntos (L3J)": st.column_config.ProgressColumn("Puntos", format="%.2f", min_value=0, max_value=float(df_pwr["Puntos (L3J)"].max()))})
            
            with col_cards:
                if not df_pwr.empty:
                    # Tarjeta Líder
                    st.markdown(f"""<div style="background:#1e3a8a; color:white; padding:15px; border-radius:10px; text-align:center;">
                    <small>TOP ESTADO FORMA 🚀</small><br><b style="font-size:1.3em;">{df_pwr.iloc[0]['Usuario']}</b><br>
                    <span style="color:#60a5fa;">{df_pwr.iloc[0]['Puntos (L3J)']:.2f} pts</span></div>""", unsafe_allow_html=True)
                    
                    # Tarjeta Pechofrío
                    st.markdown(f"""<div style="background:#fff1f2; color:#be123c; padding:10px; border-radius:10px; text-align:center; margin-top:10px; border:1px solid #fda4af;">
                    <small>🧊 PECHOFRÍO: {df_pwr.iloc[-1]['Usuario']}</small></div>""", unsafe_allow_html=True)

            st.plotly_chart(px.bar(df_pwr, x='Usuario', y='Puntos (L3J)', color='Puntos (L3J)', color_continuous_scale='Blues'), use_container_width=True)
    
        with sub_tabs[2]: # --- 📉 EVOLUCIÓN (PUNTOS Y PUESTO) ---
            st.subheader("📉 El Gráfico de la Verdad")
            
            # 1. Selector de métrica
            metrica = st.radio("Visualizar evolución por:", ["Puntos Acumulados", "Puesto en la General"], horizontal=True)

            # 2. Preparar datos históricos
            j_finalizadas = df_r_all[df_r_all['Finalizado'] == "SI"]['Jornada'].unique()
            historia_data = []

            # Puntos iniciales (Base J24)
            puntos_acum = {u: safe_float(df_base[df_base['Usuario'] == u]['Puntos'].values[0]) if not df_base[df_base['Usuario'] == u].empty else 0.0 for u in u_jugadores}

            # Añadir punto de partida
            for u, p in puntos_acum.items():
                historia_data.append({"Jornada": "J24", "Usuario": u, "Puntos": float(p)})

            # Calcular evolución jornada a jornada
            for j in j_finalizadas:
                res_j = df_r_all[(df_r_all['Jornada'] == j) & (df_r_all['Finalizado'] == "SI")]
                for u in u_jugadores:
                    u_p_j = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == j)]
                    pts_ganados = 0.0
                    for r in u_p_j.itertuples():
                        m_match = res_j[res_j['Partido'] == r.Partido]
                        if not m_match.empty:
                            pts_ganados += calcular_puntos(r.P_L, r.P_V, m_match.iloc[0]['R_L'], m_match.iloc[0]['R_V'], m_match.iloc[0]['Tipo'])
                    
                    puntos_acum[u] += pts_ganados
                    historia_data.append({"Jornada": j, "Usuario": u, "Puntos": float(puntos_acum[u])})

            if historia_data:
                df_evol = pd.DataFrame(historia_data)
                # Calculamos el puesto dinámicamente en cada jornada
                df_evol['Puesto'] = df_evol.groupby('Jornada')['Puntos'].rank(ascending=False, method='min')

                # 3. Configurar Gráfico según elección
                if metrica == "Puntos Acumulados":
                    y_axis = "Puntos"
                    titulo = "Evolución de Puntos Totales"
                    inv_y = False
                else:
                    y_axis = "Puesto"
                    titulo = "Evolución de la Posición (#1 es el mejor)"
                    inv_y = True # Invertimos el eje para que el 1 esté arriba

                fig_evol = px.line(
                    df_evol, 
                    x="Jornada", 
                    y=y_axis, 
                    color="Usuario",
                    markers=True,
                    category_orders={"Jornada": ["J24"] + list(j_finalizadas)},
                    title=titulo,
                    color_discrete_sequence=px.colors.qualitative.Bold
                )

                # Ajustes de diseño
                fig_evol.update_yaxes(autorange="reversed" if inv_y else True, title=y_axis)
                fig_evol.update_layout(
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )

                st.plotly_chart(fig_evol, use_container_width=True)
                
                # --- MINI DASHBOARD DE "SORPASSOS" ---
                if len(j_finalizadas) > 0:
                    st.markdown("---")
                    col_a, col_b = st.columns(2)
                    
                    # El que más ha subido esta jornada
                    ultima_j = j_finalizadas[-1]
                    penultima_j = j_finalizadas[-2] if len(j_finalizadas) > 1 else "J24"
                    
                    df_ult = df_evol[df_evol['Jornada'] == ultima_j].set_index('Usuario')
                    df_pen = df_evol[df_evol['Jornada'] == penultima_j].set_index('Usuario')
                    
                    subidón = (df_pen['Puesto'] - df_ult['Puesto']).idxmax()
                    puestos_subidos = int(df_pen.loc[subidón, 'Puesto'] - df_ult.loc[subidón, 'Puesto'])
                    
                    if puestos_subidos > 0:
                        col_a.success(f"🚀 **Cohete de la jornada:** {subidón} (+{puestos_subidos} puestos)")
                    else:
                        col_a.info("ℹ️ No ha habido cambios de posición esta jornada.")
                        
                    # El que más puntos ha sumado hoy
                    puntos_hoy = {u: (df_ult.loc[u, 'Puntos'] - df_pen.loc[u, 'Puntos']) for u in u_jugadores}
                    mejor_hoy = max(puntos_hoy, key=puntos_hoy.get)
                    col_b.metric("🔥 On Fire", mejor_hoy, f"+{puntos_hoy[mejor_hoy]:.2f} pts")

            else:
                st.info("Esperando a que termine la Jornada 25 para mostrar la carnicería...")

    
    with tabs[6]: # DETALLES
        df_rf = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "SI")]
        if not df_rf.empty:
            m_p = pd.DataFrame(index=df_rf['Partido'].unique(), columns=u_jugadores)
            for p in m_p.index:
                inf = df_rf[df_rf['Partido'] == p].iloc[0]
                for u in u_jugadores:
                    up = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == j_global) & (df_p_all['Partido'] == p)]
                    m_p.at[p, u] = calcular_puntos(up.iloc[0]['P_L'], up.iloc[0]['P_V'], inf['R_L'], inf['R_V'], inf['Tipo']) if not up.empty else 0.0
            st.dataframe(m_p.astype(float), use_container_width=True)
        else: st.info("Sin partidos finalizados.")

    with tabs[7]: # SIMULADOR
        usr_sim = st.selectbox("Simular LaLiga según apuestas de:", u_jugadores)
        if st.button("Generar Clasificación Simulada"):
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
            st.dataframe(pd.DataFrame.from_dict(sim, orient='index').sort_values("Pts", ascending=False), use_container_width=True)

    with tabs[8]: # --- 🎲 ORÁCULO ---
        if usa_oraculo:
            with st.spinner("🔮 El Oráculo está analizando el futuro..."):
                st.image("https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmNrNjVlaW0xZzM0MWxubDQyZGhla3V4eXVnMHU5eHcwN3NxamRtMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Jap1tdjahS0rm/giphy.gif", width=300)
                prob = simular_oraculo(u_jugadores, df_p_all, df_r_all, j_global)
            
            if prob:
                st.subheader("🔮 Estado Actual del Oráculo")
                
                # --- PREPARACIÓN DE COLUMNAS (Gráfico Izquierda | Texto Derecha) ---
                col_izq, col_der = st.columns([1.5, 1], gap="large")

                with col_izq:
                    # --- GRÁFICO DE EVOLUCIÓN (Eje X Compacto) ---
                    df_hist = leer_datos("HistoricoOraculo")
                    
                    if not df_hist.empty and 'Jornada' in df_hist.columns:
                        df_hist_j = df_hist[df_hist['Jornada'] == j_global].copy()
                        
                        if not df_hist_j.empty:
                            # Limpieza de decimales y fechas
                            df_hist_j['Probabilidad'] = df_hist_j['Probabilidad'].astype(str).str.replace(',', '.')
                            df_hist_j['Probabilidad'] = pd.to_numeric(df_hist_j['Probabilidad'], errors='coerce').fillna(0)
                            df_hist_j['Fecha_DT'] = pd.to_datetime(df_hist_j['Fecha'], format='%H:%M:%S', errors='coerce')
                            if df_hist_j['Fecha_DT'].isna().all():
                                df_hist_j['Fecha_DT'] = pd.to_datetime(df_hist_j['Fecha'], format='%H:%M', errors='coerce')
                            
                            df_hist_j = df_hist_j.sort_values('Fecha_DT')

                            fig_evo = px.line(
                                df_hist_j, x="Fecha_DT", y="Probabilidad", color="Usuario",
                                markers=True, line_shape="spline"
                            )
                            fig_evo.update_layout(
                                yaxis_range=[-2, 102], 
                                hovermode="x unified", 
                                xaxis_title="Evolución (Hora)",
                                yaxis_title="Prob %",
                                height=450, 
                                margin=dict(l=0, r=0, t=10, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5)
                            )
                            st.plotly_chart(fig_evo, use_container_width=True)
                        else:
                            st.info("Sin historial aún.")

                with col_der:
                    # --- LISTADO DE PROBABILIDADES A LA DERECHA ---
                    st.markdown("#### 🎯 Probabilidades")
                    
                    # Ordenamos por probabilidad (de mayor a menor)
                    for u, v in sorted(prob.items(), key=lambda x: x[1], reverse=True):
                        # Lógica de visualización para supervivientes y eliminados
                        esta_vivo = v > 0
                        card_bg = "#f8f9fa" if esta_vivo else "#fff5f5"
                        card_border = "#2baf2b" if esta_vivo else "#ff4b4b"
                        txt_color = "#31333F" if esta_vivo else "#999999"
                        
                        # Cálculo del Delta
                        delta = 0.0
                        if not df_hist.empty:
                            u_h = df_hist[(df_hist['Usuario'] == u) & (df_hist['Jornada'] == j_global)]
                            if len(u_h) > 1:
                                try:
                                    v_act = float(v)
                                    v_pre = float(str(u_h.iloc[-2]['Probabilidad']).replace(',', '.'))
                                    delta = v_act - v_pre
                                except: pass
                        
                        # Iconos y colores según tendencia
                        color_d = "green" if delta > 0 else ("red" if delta < 0 else "gray")
                        delta_icon = "▲" if delta > 0 else ("▼" if delta < 0 else "•")
                        status_icon = "🟢" if esta_vivo else "💀"
                        
                        # Tarjeta de Usuario
                        st.markdown(f"""
                            <div style="background:{card_bg}; padding:10px; border-radius:10px; border-left:4px solid {card_border}; margin-bottom:8px; opacity: {1.0 if esta_vivo else 0.6};">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <span style="font-weight:bold; color:{txt_color};">{status_icon} {u}</span>
                                    <span style="font-size:1.2em; font-weight:800; color:{card_border};">{v:.1f}%</span>
                                </div>
                                <div style="text-align:right; font-size:0.8em; color:{color_d if esta_vivo else '#999999'};">
                                    {f'{delta_icon} {abs(delta):.1f}%' if esta_vivo and delta != 0 else ('Eliminado' if not esta_vivo else 'Sin cambios')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Barra de progreso (solo para los que tienen opciones)
                        if esta_vivo:
                            st.progress(min(v/100, 1.0))
                        else:
                            st.divider()

                # --- CONFETI SI HAY GANADOR ---
                if any(v >= 90 for v in prob.values()):
                    ganador_v = max(prob, key=prob.get)
                    st.balloons()
                    st.success(f"🏆 **{ganador_v}** acaricia la victoria con un {prob[ganador_v]:.1f}%")
        else:
            st.info("El Oráculo se activa cuando quedan de 1 a 3 partidos.")
            st.image("https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ2IycHoyZ2pxeG9pdGU0OHYxODdsdzRldzFyd25lZDVwaTkzd3ZoMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/WPtzThAErhBG5oXLeS/giphy.gif", width=300)
    
    
    with tabs[9]: # --- PESTAÑA ADMIN ACTUALIZADA ---
        if st.session_state.rol == "admin":
            st.header("⚙️ Panel de Control de Administrador")
            
            # --- SUB-PESTAÑAS ORGANIZADAS ---
            t_bases, t_ajustes, t_fotos, t_resultados = st.tabs([
                "⭐ Puntos Base", 
                "⚖️ Ajustes Manuales",
                "📸 Fotos de Perfil", 
                "⚽ Resultados y Horarios"
            ])

            with t_bases:
                st.subheader("Configurar Puntos Iniciales")
                st.info("Usa esto para definir la base fija de cada jugador.")
                upd_b = []
                for u in u_jugadores:
                    pb_row = df_base[df_base['Usuario'] == u]
                    pts_actuales = safe_float(pb_row['Puntos'].values[0]) if not pb_row.empty else 0.0
                    
                    col_u, col_p = st.columns([2, 1])
                    col_u.markdown(f"**{u}**")
                    nuevo_val = col_p.number_input(f"Pts base {u}", value=pts_actuales, step=0.5, key=f"adm_b_{u}", label_visibility="collapsed")
                    upd_b.append({"Usuario": u, "Puntos": nuevo_val})
                
                if st.button("💾 Guardar Todos los Puntos Base", use_container_width=True):
                    conn.update(worksheet="PuntosBase", data=pd.DataFrame(upd_b))
                    st.cache_data.clear()
                    st.success("✅ Puntos base actualizados.")
                    time.sleep(1)
                    st.rerun()

            with t_ajustes:
                st.subheader("⚖️ Sanciones y Bonificaciones")
                st.markdown("Añade o resta puntos directamente al total y deja constancia en el VAR.")
                
                with st.form("form_ajuste"):
                    c1, c2 = st.columns(2)
                    u_target = c1.selectbox("Jugador a ajustar:", u_jugadores)
                    pts_ajuste = c2.number_input("Puntos (+/-):", value=0.0, step=0.25, help="Usa valores negativos para sanciones.")
                    concepto = st.text_input("Concepto del ajuste:", placeholder="Ej: Sanción por no pagar la cuota / Bonus por acertar el Pichichi")
                    
                    submit_ajuste = st.form_submit_button("⚖️ Aplicar Ajuste y Notificar al VAR", use_container_width=True)

                if submit_ajuste:
                    if concepto.strip() == "":
                        st.error("❌ Debes indicar un concepto para el ajuste.")
                    elif pts_ajuste == 0:
                        st.warning("⚠️ El ajuste es 0, no se han realizado cambios.")
                    else:
                        # 1. Copiamos y ASEGURAMOS que la columna sea numérica
                        df_base_copy = df_base.copy()
                        
                        # Limpiamos la columna de puntos: pasamos a string, cambiamos coma por punto y convertimos a número
                        df_base_copy['Puntos'] = pd.to_numeric(
                            df_base_copy['Puntos'].astype(str).str.replace(',', '.'), 
                            errors='coerce'
                        ).fillna(0.0)

                        # 2. Aplicamos el ajuste
                        if u_target in df_base_copy['Usuario'].values:
                            # Filtramos la fila y sumamos
                            idx = df_base_copy[df_base_copy['Usuario'] == u_target].index
                            df_base_copy.loc[idx, 'Puntos'] += float(pts_ajuste)
                        else:
                            # Si el usuario no estaba en PuntosBase, lo creamos
                            nueva_fila = pd.DataFrame([{"Usuario": u_target, "Puntos": float(pts_ajuste)}])
                            df_base_copy = pd.concat([df_base_copy, nueva_fila], ignore_index=True)
                        
                        # 3. Subimos a GSheets
                        conn.update(worksheet="PuntosBase", data=df_base_copy)

                        # 4. Registrar en el VAR (Logs)
                        ahora_madrid = get_now_madrid()
                        simbolo = "+" if pts_ajuste > 0 else ""
                        txt_log = f"⚖️ AJUSTE: {simbolo}{pts_ajuste} pts a {u_target}. Motivo: {concepto}"
                        
                        nuevo_log = pd.DataFrame([{
                            "Fecha": ahora_madrid.strftime("%Y-%m-%d %H:%M:%S"),
                            "Usuario": "🛡️ ADMIN",
                            "Accion": txt_log
                        }])
                        
                        # Leer logs frescos para no borrar lo anterior
                        df_logs_actual = leer_datos("Logs")
                        conn.update(worksheet="Logs", data=pd.concat([df_logs_actual, nuevo_log], ignore_index=True))

                        st.cache_data.clear()
                        st.success(f"✅ Ajuste aplicado con éxito: {txt_log}")
                        time.sleep(1.5)
                        st.rerun()

            with t_fotos:
                st.subheader("Asignar Imágenes a Usuarios")
                if os.path.exists(PERFILES_DIR):
                    archivos = ["Ninguna"] + sorted([f for f in os.listdir(PERFILES_DIR) if f.endswith(('.jpeg', '.jpg', '.png', '.webp'))])
                    upd_f = []
                    for u in u_jugadores:
                        path_en_db = foto_dict.get(u, "")
                        if pd.isna(path_en_db) or not isinstance(path_en_db, str): path_en_db = ""
                        
                        nombre_foto_actual = os.path.basename(path_en_db) if path_en_db != "" else "Ninguna"
                        col_u2, col_f = st.columns([2, 1])
                        col_u2.write(f"Usuario: **{u}**")
                        idx_foto = archivos.index(nombre_foto_actual) if nombre_foto_actual in archivos else 0
                        foto_sel = col_f.selectbox(f"Foto {u}", archivos, index=idx_foto, key=f"adm_f_{u}", label_visibility="collapsed")
                        
                        path_final = f"{PERFILES_DIR}{foto_sel}" if foto_sel != "Ninguna" else ""
                        upd_f.append({"Usuario": u, "ImagenPath": path_final})
                    
                    if st.button("🖼️ Actualizar Todas las Fotos", use_container_width=True):
                        conn.update(worksheet="ImagenesPerfil", data=pd.DataFrame(upd_f))
                        st.cache_data.clear()
                        st.success("✅ Fotos actualizadas correctamente.")
                        st.rerun()
                else:
                    st.error(f"⚠️ La carpeta '{PERFILES_DIR}' no existe.")

            with t_resultados:
                st.subheader(f"Gestión de la {j_global}")
                r_env = []
                h_ops = [datetime.time(h, m).strftime("%H:%M") for h in range(12, 23) for m in [0, 15, 30, 45]]
                
                for i, (loc, vis) in enumerate(JORNADAS[j_global]):
                    m_id = f"{loc}-{vis}"
                    prev = df_r_all[(df_r_all['Jornada']==j_global) & (df_r_all['Partido']==m_id)]
                    
                    rl, rv, fin, t = 0, 0, False, "Normal"
                    fecha_v = datetime.datetime(2026, 2, 23).date()
                    hora_v = "21:00"

                    if not prev.empty: 
                        rl, rv, fin = int(prev.iloc[0]['R_L']), int(prev.iloc[0]['R_V']), prev.iloc[0]['Finalizado']=="SI"
                        t = prev.iloc[0]['Tipo']
                        try:
                            dt_obj = datetime.datetime.strptime(str(prev.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                            fecha_v = dt_obj.date()
                            hora_v = dt_obj.strftime("%H:%M")
                        except: pass

                    st.markdown(f"**⚽ {m_id}**")
                    c1, c2, c3, c4, c5, c6 = st.columns([1.2, 1.2, 1, 0.7, 0.7, 0.6])
                    
                    nt = c1.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], index=["Normal", "Doble", "Esquizo"].index(t), key=f"at_{i}")
                    nf = c2.date_input("Día", value=fecha_v, key=f"adate_{i}")
                    nh = c3.selectbox("Hora", h_ops, index=h_ops.index(hora_v) if hora_v in h_ops else 0, key=f"aho_{i}")
                    nrl = c4.number_input("L", 0, 9, rl, key=f"arl_{i}")
                    nrv = c5.number_input("V", 0, 9, rv, key=f"arv_{i}")
                    nfi = c6.checkbox("Fin", fin, key=f"afi_{i}")
                    
                    r_env.append({
                        "Jornada": j_global, "Partido": m_id, "Tipo": nt, 
                        "R_L": nrl, "R_V": nrv, "Hora_Inicio": f"{nf} {nh}:00", 
                        "Finalizado": "SI" if nfi else "NO"
                    })
                
                st.divider()
                if st.button("🏟️ GUARDAR RESULTADOS JORNADA", use_container_width=True):
                    ahora_fresca = get_now_madrid()
                    logs_adm = []
                    for r in r_env:
                        match_previo = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Partido'] == r['Partido'])]
                        registrar = False
                        if not match_previo.empty:
                            was_fin = match_previo.iloc[0]['Finalizado'] == "SI"
                            if r['Finalizado'] == "SI" and not was_fin: registrar = True
                        
                        if registrar:
                            logs_adm.append({
                                "Fecha": ahora_fresca.strftime("%Y-%m-%d %H:%M:%S"),
                                "Usuario": "🛡️ ADMIN",
                                "Accion": f"⚽ OFICIAL: {r['Partido']} ({r['R_L']}-{r['R_V']})"
                            })

                    if logs_adm:
                        df_l_existente = leer_datos("Logs")
                        conn.update(worksheet="Logs", data=pd.concat([df_l_existente, pd.DataFrame(logs_adm)], ignore_index=True))

                    otros = df_r_all[df_r_all['Jornada'] != j_global]
                    df_resultados_new = pd.concat([otros, pd.DataFrame(r_env)], ignore_index=True)
                    conn.update(worksheet="Resultados", data=df_resultados_new)
                    
                    st.cache_data.clear()
                    st.success(f"✅ Datos guardados.")
                    st.rerun()
        else:
            st.warning("⛔ Acceso restringido.")
            st.error(f"Tu usuario (**{st.session_state.user}**) no tiene permisos de administrador.")
    with tabs[10]: # --- PESTAÑA VAR MEJORADA ---
        st.header("🏁 El VAR de la Porra")
        st.image("https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExczF4bGVvbmQ3eTVuam44dzExbXl4MDU5cmVsY24zMGdyb2dvNnpjdiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/U4DdzRe7wJP0aPI1Pa/giphy.gif", width=300)
        st.caption("Transparencia total: aquí se registra cada movimiento clave de la liga.")
        
        df_logs = conn.read(worksheet="Logs", ttl=0)
        if not df_logs.empty:
            df_logs["Fecha"] = pd.to_datetime(df_logs["Fecha"])
            df_logs = df_logs.sort_values("Fecha", ascending=False)
            
            for _, fila in df_logs.head(40).iterrows():
                es_admin_log = "ADMIN" in str(fila['Usuario'])
                accion_txt = str(fila['Accion'])
                
                # --- Lógica de Iconos Dinámicos ---
                icon = "📝" # Por defecto (predicciones)
                if "⚖️ AJUSTE" in accion_txt: icon = "⚖️"
                if "⚽ OFICIAL" in accion_txt: icon = "🏟️"
                if "🔄 Modificó" in accion_txt: icon = "🔄"
                
                with st.container():
                    c_time, c_user, c_act = st.columns([1.2, 1, 3])
                    
                    # Formatear fecha para que sea más legible
                    fecha_fmt = fila['Fecha'].strftime("%d/%m %H:%M")
                    c_time.caption(f"🕒 {fecha_fmt}")
                    
                    # Color del nombre de usuario
                    user_display = f"**{fila['Usuario']}**"
                    c_user.markdown(user_display)
                    
                    # Estilo del mensaje
                    if es_admin_log:
                        # Si es un ajuste manual, le damos un toque distinto
                        if "⚖️" in icon:
                            c_act.warning(f"{icon} {accion_txt.replace('⚖️ AJUSTE:', '')}")
                        else:
                            c_act.info(f"{icon} {accion_txt}")
                    else:
                        c_act.write(f"{icon} {accion_txt}")
                    
                    st.divider()
        else:
            st.info("El historial está vacío. ¡Que empiece el juego!")





