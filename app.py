import streamlit as st
import pandas as pd
from sqlalchemy import text
import datetime
import os
import plotly.express as px
import random
import itertools
import numpy as np
import time
import pytz
from streamlit_gsheets import GSheetsConnection
 
# --- 1. CONFIGURACIONES GENERALES ---
PERFILES_DIR = "perfiles/"
LOGOS_DIR = "logos/"


NIVEL_EQUIPOS = {
    "Francia": 1, "Argentina": 1, "Brasil": 1, "Inglaterra": 1, "España": 1, "Portugal": 1,
    "Alemania": 2, "Países Bajos": 2, "Uruguay": 2, "Croacia": 2, "Bélgica": 2, "Colombia": 2,
    "Italia": 2, "Marruecos": 2, "Suiza": 3, "Japón": 3, "México": 3, "Estados Unidos": 3, 
    "Senegal": 3, "Corea del Sur": 3, "República Checa": 3, "Turquía": 3, "Suecia": 3, "Austria": 3,
    "Dinamarca": 3, "Ecuador": 3, "Noruega": 4, "Canadá": 4, "Paraguay": 4, "Australia": 4, 
    "Costa de Marfil": 4, "Argelia": 4, "Egipto": 4, "Irán": 4, "Ghana": 4, "Bosnia Herzegovina": 4,
    "Sudáfrica": 5, "Qatar": 5, "Haití": 5, "Escocia": 5, "Curaçao": 5, "Túnez": 5,
    "Cabo Verde": 5, "Arabia Saudí": 5, "Iraq": 5, "Nueva Zelanda": 5, "Jordania": 5, 
    "Congo": 5, "Uzbekistán": 5, "Panamá": 5
}
CONTINENTES = {
    "Francia": "UEFA", "España": "UEFA", "Inglaterra": "UEFA", "Alemania": "UEFA", "Países Bajos": "UEFA",
    "Portugal": "UEFA", "Croacia": "UEFA", "Bélgica": "UEFA", "Suiza": "UEFA", "República Checa": "UEFA",
    "Turquía": "UEFA", "Suecia": "UEFA", "Austria": "UEFA", "Bosnia Herzegovina": "UEFA", "Escocia": "UEFA",
    "Argentina": "CONMEBOL", "Brasil": "CONMEBOL", "Uruguay": "CONMEBOL", "Colombia": "CONMEBOL", 
    "Ecuador": "CONMEBOL", "Paraguay": "CONMEBOL",
    "México": "CONCACAF", "Estados Unidos": "CONCACAF", "Canadá": "CONCACAF", "Panamá": "CONCACAF", 
    "Haití": "CONCACAF", "Curaçao": "CONCACAF",
    "Marruecos": "CAF", "Senegal": "CAF", "Costa de Marfil": "CAF", "Argelia": "CAF", "Egipto": "CAF", 
    "Ghana": "CAF", "Sudáfrica": "CAF", "Cabo Verde": "CAF", "Congo": "CAF", "Túnez": "CAF",
    "Japón": "AFC", "Corea del Sur": "AFC", "Irán": "AFC", "Arabia Saudí": "AFC", "Qatar": "AFC", 
    "Iraq": "AFC", "Uzbekistán": "AFC", "Jordania": "AFC",
    "Australia": "AFC", "Nueva Zelanda": "OFC"
}

COLORES_BANDERAS = {
    "México": ["#006847", "#CE1126"], "Sudáfrica": ["#007A4D", "#FFCD00"], 
    "Corea del Sur": ["#CD2E3A", "#0047A0"], "República Checa": ["#D7141A", "#11457E"],
    "Canadá": ["#FF0000", "#FFFFFF"], "Bosnia Herzegovina": ["#002395", "#FECB00"], 
    "Qatar": ["#8D1B3D", "#FFFFFF"], "Suiza": ["#FF0000", "#FFFFFF"],
    "Brasil": ["#009739", "#FEDD00"], "Marruecos": ["#C1272D", "#006233"], 
    "Haití": ["#00209F", "#D21034"], "Escocia": ["#0065BF", "#FFFFFF"],
    "Estados Unidos": ["#B22234", "#3C3B6E"], "Paraguay": ["#D52B1E", "#0038A8"], 
    "Australia": ["#00008B", "#FF0000"], "Turquía": ["#E30A17", "#FFFFFF"],
    "Alemania": ["#000000", "#FFCE00"], "Curaçao": ["#002B7F", "#F9E814"], 
    "Costa de Marfil": ["#FF8200", "#009E60"], "Ecuador": ["#FFDD00", "#0046AE"],
    "Países Bajos": ["#AE1C28", "#21468B"], "Japón": ["#BC002D", "#FFFFFF"], 
    "Suecia": ["#006AA7", "#FECC00"], "Túnez": ["#E70013", "#FFFFFF"],
    "España": ["#AA151B", "#F1BF00"], "Cabo Verde": ["#003893", "#FFD700"], 
    "Arabia Saudí": ["#006C35", "#FFFFFF"], "Uruguay": ["#0038A8", "#FFFFFF"],
    "Bélgica": ["#000000", "#FFD935"], "Egipto": ["#CE1126", "#000000"], 
    "Irán": ["#239F40", "#DA0000"], "Nueva Zelanda": ["#00247D", "#FFFFFF"],
    "Francia": ["#002395", "#ED2939"], "Senegal": ["#00853F", "#E31B23"], 
    "Iraq": ["#CE1126", "#007A3D"], "Noruega": ["#BA0C2F", "#00205B"],
    "Argentina": ["#74ACDF", "#FFFFFF"], "Argelia": ["#006233", "#D21034"], 
    "Austria": ["#ED2939", "#FFFFFF"], "Jordania": ["#000000", "#CE1126"],
    "Portugal": ["#FF0000", "#006600"], "Congo": ["#002B7F", "#F7D117"], 
    "Uzbekistán": ["#0099B5", "#1EB53A"], "Colombia": ["#FCD116", "#003893"],
    "Inglaterra": ["#CE1126", "#FFFFFF"], "Croacia": ["#FF0000", "#171796"], 
    "Ghana": ["#EF3340", "#FFCD00"], "Panamá": ["#DA121A", "#072357"]
}

GRUPOS_2026 = {
    "Grupo A": ["México", "Sudáfrica", "Corea del Sur", "Chequia"],
    "Grupo B": ["Canadá", "Bosnia y Hezegovina", "Qatar", "Suiza"],
    "Grupo C": ["Brasil", "Marruecos", "Haití", "Escocia"],
    "Grupo D": ["Estados Unidos", "Paraguay", "Australia", "Turquía"],
    "Grupo E": ["Alemania", "Curazao", "Costa de Marfil", "Ecuador"],
    "Grupo F": ["Países Bajos", "Japón", "Suecia", "Túnez"],
    "Grupo G": ["Bélgica", "Egipto", "Irán", "Nueva Zelanda"],
    "Grupo H": ["España", "Cabo Verde", "Arabia Saudita", "Uruguay"],
    "Grupo I": ["Francia", "Senegal", "Irak", "Noruega"],
    "Grupo J": ["Argentina", "Argelia", "Austria", "Jordania"],
    "Grupo K": ["Portugal", "R.D. Congo", "Uzbekistán", "Colombia"],
    "Grupo L": ["Inglaterra", "Croacia", "Ghana", "Panamá"]
}

JORNADAS = {
    "Jornada 1": [
        ("México", "Sudáfrica"), ("Corea del Sur", "República Checa"),
        ("Canadá", "Bosnia Herzegovina"), ("Estados Unidos", "Paraguay"),
        ("Qatar", "Suiza"), ("Brasil", "Marruecos"),
        ("Haití", "Escocia"), ("Australia", "Turquía"),
        ("Alemania", "Curaçao"), ("Países Bajos", "Japón"),
        ("Costa de Marfil", "Ecuador"), ("Suecia", "Túnez"),
        ("España", "Cabo Verde"), ("Bélgica", "Egipto"),
        ("Arabia Saudí", "Uruguay"), ("Irán", "Nueva Zelanda"),
        ("Francia", "Senegal"), ("Iraq", "Noruega"),
        ("Argentina", "Argelia"), ("Austria", "Jordania"),
        ("Portugal", "Congo"), ("Inglaterra", "Croacia"),
        ("Ghana", "Panamá"), ("Uzbekistán", "Colombia")
    ],
    "Jornada 2": [
        ("República Checa", "Sudáfrica"), ("Suiza", "Bosnia Herzegovina"),
        ("Canadá", "Qatar"), ("México", "Corea del Sur"),
        ("Estados Unidos", "Australia"), ("Escocia", "Marruecos"),
        ("Brasil", "Haití"), ("Turquía", "Paraguay"),
        ("Países Bajos", "Suecia"), ("Alemania", "Costa de Marfil"),
        ("Ecuador", "Curaçao"), ("Túnez", "Japón"),
        ("España", "Arabia Saudí"), ("Bélgica", "Irán"),
        ("Uruguay", "Cabo Verde"), ("Nueva Zelanda", "Egipto"),
        ("Argentina", "Austria"), ("Francia", "Iraq"),
        ("Noruega", "Senegal"), ("Jordania", "Argelia"),
        ("Portugal", "Uzbekistán"), ("Inglaterra", "Ghana"),
        ("Panamá", "Croacia"), ("Colombia", "Congo")
    ],
    "Jornada 3": [
        ("Bosnia Herzegovina", "Qatar"), ("Suiza", "Canadá"),
        ("Marruecos", "Haití"), ("Escocia", "Brasil"),
        ("República Checa", "México"), ("Sudáfrica", "Corea del Sur"),
        ("Curaçao", "Costa de Marfil"), ("Ecuador", "Alemania"),
        ("Japón", "Suecia"), ("Túnez", "Países Bajos"),
        ("Paraguay", "Australia"), ("Turquía", "Estados Unidos"),
        ("Noruega", "Francia"), ("Senegal", "Iraq"),
        ("Cabo Verde", "Arabia Saudí"), ("Uruguay", "España"),
        ("Egipto", "Irán"), ("Nueva Zelanda", "Bélgica"),
        ("Croacia", "Ghana"), ("Panamá", "Inglaterra"),
        ("Colombia", "Portugal"), ("Congo", "Uzbekistán"),
        ("Argelia", "Austria"), ("Jordania", "Argentina")
    ]
}

LOGOS = {
    "Athletic": f"{LOGOS_DIR}athletic.jpeg", "Elche": f"{LOGOS_DIR}elche.jpeg", "R. Sociedad": f"{LOGOS_DIR}sociedad.jpeg",
    "Real Madrid": f"{LOGOS_DIR}madrid.jpeg", "Barcelona": f"{LOGOS_DIR}barca.jpeg", "Atlético": f"{LOGOS_DIR}atletico.jpeg",
    "Rayo": f"{LOGOS_DIR}rayo.jpeg", "Sevilla": f"{LOGOS_DIR}sevilla.jpeg", "Valencia": f"{LOGOS_DIR}valencia.jpeg",
    "Girona": f"{LOGOS_DIR}girona.jpeg", "Osasuna": f"{LOGOS_DIR}osasuna.jpeg", "Getafe": f"{LOGOS_DIR}getafe.jpeg",
    "Celta": f"{LOGOS_DIR}celta.jpeg", "Mallorca": f"{LOGOS_DIR}mallorca.jpeg", "Villarreal": f"{LOGOS_DIR}villarreal.jpeg",
    "Alavés": f"{LOGOS_DIR}alaves.jpeg", "Espanyol": f"{LOGOS_DIR}espanyol.jpeg", "Betis": f"{LOGOS_DIR}betis.jpeg",
    "Levante": f"{LOGOS_DIR}levante.jpeg", "Oviedo": f"{LOGOS_DIR}oviedo.jpeg",
}

SCORING_WC = {
    "Normal": {"signo": 0.5, "diff": 0.75, "exacto": 1.0, "pasa": 0.5},
    "Esquizo": {"signo": 1.0, "diff": 1.5, "exacto": 3.0, "pasa": 1.0}
}

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

# Colores de bandera para el anillo dinámico
# Formato: "Selección": [Color1, Color2]
COLORES_BANDERAS = {
    "España": ["#FF0000", "#FFFF00"],      # Rojo y Amarillo
    "Argentina": ["#74ACDF", "#FFFFFF"],   # Celeste y Blanco
    "México": ["#006847", "#CE1126"],      # Verde y Rojo
    "Brasil": ["#009739", "#FEDD00"],      # Verde y Amarillo
    "Francia": ["#002395", "#ED2939"],     # Azul y Rojo
    # ... seguiremos con las demás
}

# Diccionario para las Stats por continente

# --- 2. FUNCIONES DE APOYO ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=10)
def leer_datos(pestaña):
    try:
        # Tu ID de hoja actual
        # 1. El ID que sacamos de tu enlace
        sheet_id = "1TL2MTxCixfAKs_3EuhVc0ENZSWub3lF7LBey3BT62-A"       
        # 2. La URL formateada para descargar cada pestaña como CSV
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={pestaña}"
        df = pd.read_csv(url)
        
        if not df.empty:
            # 1. Blindaje de Usuario: Siempre a texto para evitar errores con nombres numéricos
            if 'Usuario' in df.columns:
                df['Usuario'] = df['Usuario'].astype(str)
            
            # 2. Blindaje de Puntos: Aseguramos que sean números por si hay comas en el Excel
            columnas_numericas = ['P_L', 'P_V', 'R_L', 'R_V', 'Puntos']
            for col in columnas_numericas:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)
            
            # 3. Normalización de Prórroga (Opcional pero recomendado para tu nueva lógica)
            if 'Hubo_Prorroga' in df.columns:
                df['Hubo_Prorroga'] = df['Hubo_Prorroga'].astype(str).str.upper().str.strip()

        return df
    except Exception as e:
        # En caso de error, devolvemos un DataFrame vacío para que la App no "pete"
        return pd.DataFrame()

def safe_float(valor):
    try:
        if pd.isna(valor) or str(valor).strip() == "": return 0.0
        return float(str(valor).replace(',', '.'))
    except: return 0.0

def get_logo(equipo):
    path = LOGOS.get(equipo)
    if path and os.path.exists(path): return path
    return None

def calcular_puntos_wc(p_l, p_v, r_l, r_v, tipo="Normal", p_pasa=None, r_pasa=None, hubo_prorroga=False):
    """
    p_l, p_v: Predicción marcador 90'
    r_l, r_v: Resultado real 90'
    p_pasa: Equipo que el usuario dijo que pasaba
    r_pasa: Equipo que pasó realmente
    hubo_prorroga: Booleano que indica si el partido terminó en empate tras los 90'
    """
    puntos_totales = 0.0
    config = SCORING_WC.get(tipo, SCORING_WC["Normal"])
    
    # 1. PUNTUACIÓN 90 MINUTOS (Misma lógica de siempre)
    if p_l == r_l and p_v == r_v:
        puntos_totales += config["exacto"]
    else:
        signo_p = (p_l > p_v) - (p_l < p_v)
        signo_r = (r_l > r_v) - (r_l < r_v)
        if signo_p == signo_r:
            if (p_l - p_v) == (r_l - r_v):
                puntos_totales += config["diff"]
            else:
                puntos_totales += config["signo"]
                
    # 2. LÓGICA DE ELIMINATORIAS (EL EXTRA)
    # Solo sumamos si hubo prórroga/penaltis y el usuario acertó quién clasifica
    if hubo_prorroga and p_pasa and r_pasa:
        if p_pasa == r_pasa:
            puntos_totales += config["pasa"]
            
    return puntos_totales

def simular_temporada_completa(df_hero, df_p_all, df_r_all):
    """
    Simulación de Montecarlo: Proyecta el final de la porra 5.000 veces.
    Considera: Puntos actuales, partidos pendientes (Normal/Esquizo) y 
    una estimación de puntos de Bracket.
    """
    # 1. Puntos actuales de cada usuario
    usuarios = df_hero['Usuario'].tolist()
    puntos_actuales = df_hero.set_index('Usuario')['Puntos'].to_dict()
    
    # 2. Identificar partidos que faltan por jugar
    pendientes = df_r_all[df_r_all['Finalizado'] == "NO"]
    num_pend_normal = len(pendientes[pendientes['Tipo'] != "Esquizo"])
    num_pend_esquizo = len(pendientes[pendientes['Tipo'] == "Esquizo"])
    
    # 3. Calcular el "ADN de acierto" de cada usuario (puntos medios por tipo)
    # Si el usuario es nuevo, le asignamos una media estándar
    perfil_usuario = {}
    df_terminados = df_r_all[df_r_all['Finalizado'] == "SI"]
    
    for u in usuarios:
        # Puntos conseguidos en partidos normales y esquizos para sacar su media
        u_p = df_p_all[df_p_all['Usuario'] == u]
        m_fin = pd.merge(u_p, df_terminados, on=['Jornada', 'Partido'])
        
        if not m_fin.empty:
            m_fin['Pts'] = m_fin.apply(lambda x: calcular_puntos_wc(
                x.P_L, x.P_V, x.R_L, x.R_V, x.Tipo, 
                getattr(x, 'P_Pasa', None), x.get('R_Pasa'), x.get('Hubo_Prorroga') == "SI"
            ), axis=1)
            
            media_n = m_fin[m_fin['Tipo'] != "Esquizo"]['Pts'].mean() if not m_fin[m_fin['Tipo'] != "Esquizo"].empty else 0.4
            media_e = m_fin[m_fin['Tipo'] == "Esquizo"]['Pts'].mean() if not m_fin[m_fin['Tipo'] == "Esquizo"].empty else 0.8
            desvio = m_fin['Pts'].std() if len(m_fin) > 1 else 0.2
        else:
            media_n, media_e, desvio = 0.45, 0.9, 0.25 # Valores promedio base
            
        perfil_usuario[u] = {'n': media_n, 'e': media_e, 'std': desvio}

    # 4. Bucle de Simulación (5.000 iteraciones)
    conteo_puestos = {u: [0] * len(usuarios) for u in usuarios}
    suma_puestos = {u: 0 for u in usuarios}
    
    for _ in range(5000):
        resultados_iteracion = []
        
        for u in usuarios:
            # Puntos por partidos Normales
            pts_n = np.random.normal(perfil_usuario[u]['n'], perfil_usuario[u]['std'], num_pend_normal).sum()
            # Puntos por partidos Esquizos
            pts_e = np.random.normal(perfil_usuario[u]['e'], perfil_usuario[u]['std'] * 1.5, num_pend_esquizo).sum()
            
            # Estimación de Puntos de Bracket (esto es azaroso pero basado en competencia)
            # Acertar campeón, pichichi, y avances da picos de puntos
            pts_bracket = random.uniform(0, 5.0) if num_pend_normal > 10 else random.uniform(0, 1.5)
            
            total_sim = puntos_actuales[u] + max(0, pts_n) + max(0, pts_e) + pts_bracket
            resultados_iteracion.append((u, total_sim))
            
        # Ordenar por puntos de mayor a menor
        resultados_iteracion.sort(key=lambda x: x[1], reverse=True)
        
        # Registrar posiciones
        for i, (u, pts) in enumerate(resultados_iteracion):
            conteo_puestos[u][i] += 1
            suma_puestos[u] += (i + 1)

    # 5. Formatear resultados para la tabla
    data_final = []
    for u in usuarios:
        fila = {"Usuario": u}
        fila["Puesto Medio"] = suma_puestos[u] / 5000
        # Convertir conteos a porcentajes
        for i in range(len(usuarios)):
            fila[f"P{i+1}"] = (conteo_puestos[u][i] / 5000) * 100
        data_final.append(fila)
        
    df_sim = pd.DataFrame(data_final).sort_values("Puesto Medio")
    return df_sim



def analizar_adn_pro(usuario, df_p, df_r):
    df_m = pd.merge(df_p[df_p['Usuario'] == usuario], df_r[df_r['Finalizado'] == "SI"], on=['Jornada', 'Partido'])
    if df_m.empty: return None
    df_m['Pts'] = df_m.apply(lambda x: calcular_puntos_wc(x.P_L, x.P_V, x.R_L, x.R_V, x.Tipo), axis=1)
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
    # 1. Resultados posibles a los 90'
    res_sim = [(0,0), (1,0), (0,1), (1,1), (2,1), (1,2), (2,2), (2,0), (0,2)]
    
    pend = df_r_all[(df_r_all['Jornada'] == jornada_sel) & (df_r_all['Finalizado'] == "NO")]
    if pend.empty or len(pend) > 3: return None
    
    # Identificamos los equipos de cada partido pendiente
    p_id = pend['Partido'].tolist()
    t_id = pend['Tipo'].tolist()
    
    # ¿Es jornada de eliminatorias? (Check simple por nombre de jornada)
    es_ko = any(x in jornada_sel for x in ["Dieciseisavos", "Octavos", "Cuartos", "Semis", "Final"])

    victorias = {u: 0 for u in usuarios}
    
    # Creamos los combos de resultados
    combos = list(itertools.product(res_sim, repeat=len(p_id)))
    
    total_escenarios = 0

    for c in combos:
        # Si es KO, para cada empate en el combo tenemos 2 posibilidades (Pasa A o Pasa B)
        # Para simplificar y no hacer explotar el procesador, simulamos el pase de ronda
        # de forma lógica: si el marcador no es empate, pasa el que ha ganado.
        # Si es empate, simulamos ambos pases.
        
        escenarios_internos = [[]]
        for i, marcador in enumerate(c):
            g_l, g_v = marcador
            loc, vis = p_id[i].split('-')
            
            if es_ko and g_l == g_v:
                # Si es empate en KO, añadimos dos variantes: pasa uno o pasa otro
                nuevos = []
                for esc in escenarios_internos:
                    nuevos.append(esc + [(g_l, g_v, loc, True)]) # Pasa Local
                    nuevos.append(esc + [(g_l, g_v, vis, True)]) # Pasa Visitante
                escenarios_internos = nuevos
            else:
                # Si no es empate o no es KO, el pase es el lógico o no existe
                quien_pasa = loc if g_l > g_v else (vis if g_v > g_l else None)
                for esc in escenarios_internos:
                    esc.append((g_l, g_v, quien_pasa, False))

        for esc_final in escenarios_internos:
            total_escenarios += 1
            puntos_escenario = {u: 0.0 for u in usuarios}
            
            for u in usuarios:
                u_p = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == jornada_sel)]
                
                # Puntos de partidos ya finalizados en la jornada
                fin_j = df_r_all[(df_r_all['Jornada'] == jornada_sel) & (df_r_all['Finalizado'] == "SI")]
                for r_fin in fin_j.itertuples():
                    pred = u_p[u_p['Partido'] == r_fin.Partido]
                    if not pred.empty:
                        # Usamos la nueva función de puntos
                        puntos_escenario[u] += calcular_puntos_wc(
                            pred.iloc[0]['P_L'], pred.iloc[0]['P_V'], 
                            r_fin.R_L, r_fin.R_V, r_fin.Tipo,
                            pred.iloc[0].get('P_Pasa'), r_fin.R_Pasa, 
                            r_fin.Hubo_Prorroga == "SI"
                        )

                # Puntos de partidos simulados
                for i, (sim_l, sim_v, sim_pasa, prorroga) in enumerate(esc_final):
                    pred = u_p[u_p['Partido'] == p_id[i]]
                    if not pred.empty:
                        puntos_escenario[u] += calcular_puntos_wc(
                            pred.iloc[0]['P_L'], pred.iloc[0]['P_V'],
                            sim_l, sim_v, t_id[i],
                            pred.iloc[0].get('P_Pasa'), sim_pasa, prorroga
                        )
            
            # Ganador del escenario
            mx = max(puntos_escenario.values())
            ganadores = [u for u, p in puntos_escenario.items() if p == mx]
            for g in ganadores:
                victorias[g] += 1 / len(ganadores)

    return {u: (v / total_escenarios) * 100 for u, v in victorias.items()}

def get_now_madrid():
    # Definimos la zona horaria de España
    tz = pytz.timezone('Europe/Madrid')
    # Obtenemos la hora actual en esa zona y le quitamos la información de zona 
    # para que sea compatible con las fechas de tu Excel (naive datetime)
    return datetime.datetime.now(tz).replace(tzinfo=None)

# Fecha y hora del partido inaugural (Ejemplo: 11 de Junio a las 21:00)
FECHA_INAUGURAL = datetime.datetime(2026, 6, 11, 21, 0, 0)
mercado_abierto = get_now_madrid() < FECHA_INAUGURAL

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
            
            # 1. Validaciones previas
            if u_in == "" or p_in == "":
                st.warning("⚠️ No seas 'pechofrío', pon un usuario y contraseña.")
            elif u_in in df_u['Usuario'].values:
                st.error("❌ Este usuario ya está en la convocatoria.")
            else:
                try:
                    # 2. Registro en la pestaña "Usuarios"
                    nueva_cuenta = pd.DataFrame([{"Usuario": u_in, "Password": p_in, "Rol": "user"}])
                    df_u_act = pd.concat([df_u, nueva_cuenta], ignore_index=True)
                    conn.update(worksheet="Usuarios", data=df_u_act)

                    # 3. CREACIÓN DE FILA EN PuntosBase (EL ARREGLO)
                    # Leemos la tabla de puntos actual para no borrar a nadie
                    df_pb_actual = leer_datos("PuntosBase")
                    nueva_fila_puntos = pd.DataFrame([{"Usuario": u_in, "Puntos": 0.0}])
                    df_pb_act = pd.concat([df_pb_actual, nueva_fila_puntos], ignore_index=True)
                    conn.update(worksheet="PuntosBase", data=df_pb_act)

                    # 4. Feedback y limpieza
                    st.success(f"✅ ¡Fichado! {u_in}, ya puedes loguearte.")
                    st.balloons()
                    
                    # Limpiamos caché para que el login reconozca al nuevo usuario inmediatamente
                    st.cache_data.clear()
                    time.sleep(1.5)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error crítico en el registro: {e}")
else:
    # 1. CARGA DE DATOS
    df_perf = leer_datos("ImagenesPerfil")
    # Cargamos también los logs para que ChatG-O-L los vea
    df_r_all, df_p_all, df_u_all, df_base, df_logs_all = leer_datos("Resultados"), leer_datos("Predicciones"), leer_datos("Usuarios"), leer_datos("PuntosBase"), leer_datos("Logs")
    # --- 🛡️ MURO DE SEGURIDAD ACTUALIZADO ---
    # Verificamos si las variables son None (error de carga) o si falta la tabla crítica de Usuarios
    if df_u_all is None or df_u_all.empty:
        st.error("❌ No se pudo cargar la tabla de Usuarios. Revisa la conexión con GSheets.")
        st.stop()
    
    # Si Resultados o Predicciones están vacíos, creamos un DataFrame vacío con sus columnas 
    # para que el resto de la lógica no explote, pero permitimos que la App siga.
    if df_r_all.empty:
        st.warning("⚠️ La tabla de Resultados está vacía. El Admin debe inicializar los partidos.")
        # Opcional: df_r_all = pd.DataFrame(columns=['Jornada', 'Partido', 'R_L', 'R_V', 'Finalizado', 'Tipo', 'Hora_Inicio'])
    
    if df_p_all.empty:
        # Esto es normal si nadie ha apostado aún. No detenemos la app.
        pass
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

    # --- CÁLCULO DE DASHBOARD HERO (Versión Mundial) ---
    stats_hero = []
    for u in u_jugadores:
        pb_row = df_base[df_base['Usuario'] == u]
        p_base = safe_float(pb_row['Puntos'].values[0]) if not pb_row.empty else 0.0
        
        u_p_hist = df_p_all[df_p_all['Usuario'] == u]
        p_acum = p_base
        
        for r in u_p_hist.itertuples():
            # Buscamos el resultado real del partido
            m = df_r_all[(df_r_all['Jornada'] == r.Jornada) & (df_r_all['Partido'] == r.Partido) & (df_r_all['Finalizado'] == "SI")]
            
            if not m.empty:
                # --- CAMBIO AQUÍ: Llamamos a calcular_puntos_wc con los nuevos campos ---
                p_acum += calcular_puntos_wc(
                    r.P_L, r.P_V, 
                    m.iloc[0]['R_L'], m.iloc[0]['R_V'], 
                    m.iloc[0]['Tipo'],
                    getattr(r, 'P_Pasa', None),         # Quién puso el usuario que pasaba
                    m.iloc[0].get('R_Pasa'),            # Quién pasó realmente
                    m.iloc[0].get('Hubo_Prorroga') == "SI" # Si hubo prórroga real
                )
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
                mi_puntos_hoy += calcular_puntos_wc(r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'])

    prox_p = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "NO")].sort_values("Hora_Inicio").head(1)
    # Verificamos si hay partidos antes de calcular el tiempo
    hay_proximo = not prox_p.empty
    
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
                    pts_j += calcular_puntos_wc(r.P_L, r.P_V,m_res.iloc[0]['R_L'], m_res.iloc[0]['R_V'], m_res.iloc[0]['Tipo'], getattr(r, 'P_Pasa', None), m_res.iloc[0].get('R_Pasa'), m_res.iloc[0].get('Hubo_Prorroga') == "SI")
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
            # 1. Sacamos qué equipo puso el líder como campeón en su Bracket
            # (Asumiendo que tenemos una tabla llamada df_brackets)
            try:
                equipo_fav = df_brackets[df_brackets['Usuario'] == lider['Usuario']]['Campeon'].values[0]
                colores = COLORES_BANDERAS.get(equipo_fav, ["#ffd700", "#ffae00"]) # Oro si no hay
                estilo_anillo = f"background: linear-gradient(45deg, {colores[0]}, {colores[1]});"
            except:
                estilo_anillo = "" # Clase por defecto
            
            # 2. En el HTML del Avatar
            st.markdown(f'<div class="ring-avatar" style="{estilo_anillo}">', unsafe_allow_html=True)
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
                nombres_fmt = " & ".join(map(str, lagartos_nombres))
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
                if hay_proximo:
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
    tabs = st.tabs([
    "✍️ Apuestas", 
    "🌳 Bracket",      # <--- NUEVA: Para rellenar el cuadro
    "👀 Otros", 
    "📊 Clasificación", 
    "🏅 Palmarés", 
    "📈 Stats PRO", 
    "🔮 Simulador", 
    "🎲 Oráculo", 
    "⚙️ Admin", 
    "📜 VAR"
    ])

    with tabs[0]: # --- ✍️ PESTAÑA APUESTAS (ADAPTADA MUNDIAL) ---
        st.markdown("""
        <style>
            .bet-card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 15px; }
            .bet-card-locked { background: #f1f5f9; padding: 20px; border-radius: 15px; border: 1px solid #cbd5e1; opacity: 0.8; margin-bottom: 15px; }
            .team-label { font-weight: 800; font-size: 0.9em; color: #1e293b; text-align: center; margin-bottom: 5px; text-transform: uppercase; }
            .vs-box { text-align: center; font-weight: 900; color: #94a3b8; padding-top: 10px; }
            .ko-tag { background: #fee2e2; color: #ef4444; font-size: 0.7em; padding: 2px 8px; border-radius: 10px; font-weight: bold; margin-bottom: 5px; display: inline-block; }
        </style>
        """, unsafe_allow_html=True)

        if es_admin:
            st.warning("🛡️ Acceso restringido: Los administradores no participan en las porras.")
            st.info("Tu función es supervisar el Mundial y actualizar los resultados desde la pestaña **⚙️ Admin**.")
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnh6Znd6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/fNuXfHoZY3nqE/giphy.gif", width=400)
        else:
            # Recuperar predicciones actuales del usuario
            u_preds = df_p_all[(df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global)]
            
            # --- [LÓGICA DE ORDENACIÓN] ---
            df_partidos_ordenados = df_r_all[df_r_all['Jornada'] == j_global].copy()
            df_partidos_ordenados['Hora_DT'] = pd.to_datetime(df_partidos_ordenados['Hora_Inicio'])
            df_partidos_ordenados = df_partidos_ordenados.sort_values('Hora_DT', ascending=True)
            
            lista_partidos_cronologica = []
            for _, row in df_partidos_ordenados.iterrows():
                try:
                    loc, vis = row['Partido'].split('-')
                    lista_partidos_cronologica.append((loc, vis))
                except: continue 
            
            env = []
            st.markdown(f"### 🗓️ Tu Hoja de Apuestas: {j_global}")
            
            # Detectamos si es ronda de eliminación (KO)
            es_ronda_ko = any(x in j_global for x in ["Dieciseisavos", "Octavos", "Cuartos", "Semis", "Final"])

            for i, (loc, vis) in enumerate(lista_partidos_cronologica):
                m_id = f"{loc}-{vis}"
                
                # Cargar datos guardados (incluyendo P_Pasa)
                dl, dv, dp, d_pasa = 0, 0, "NO", loc
                if not u_preds.empty:
                    match_data = u_preds[u_preds['Partido'] == m_id]
                    if not match_data.empty:
                        dl = int(match_data.iloc[0]['P_L'])
                        dv = int(match_data.iloc[0]['P_V'])
                        dp = match_data.iloc[0]['Publica']
                        d_pasa = match_data.iloc[0].get('P_Pasa', loc) # Si no existe, por defecto Local
                
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
                
                # Si es eliminatoria, ponemos un aviso
                if es_ronda_ko:
                    st.markdown('<span class="ko-tag">PARTIDO DE ELIMINACIÓN</span>', unsafe_allow_html=True)

                c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 1, 2, 1, 1.5])
                
                with c1: # Escudo Local
                    log_l = get_logo(loc)
                    if log_l: st.image(log_l, width=50)
                
                with c2: # Marcador Local
                    st.markdown(f'<p class="team-label">{loc}</p>', unsafe_allow_html=True)
                    pl = st.number_input("G", 0, 9, dl, key=f"pl_{i}_{j_global}", disabled=lock, label_visibility="collapsed")
                
                with c3: # VS
                    st.markdown('<div class="vs-box">VS</div>', unsafe_allow_html=True)
                    if lock: st.markdown('<p style="text-align:center;">🔒</p>', unsafe_allow_html=True)
                    else:
                        try:
                            dt_p = datetime.datetime.strptime(str(hora_partido), "%Y-%m-%d %H:%M:%S")
                            st.markdown(f'<p style="text-align:center; font-size:0.65em; color:#64748b; font-weight:bold;">{dt_p.strftime("%d/%m %H:%M")}</p>', unsafe_allow_html=True)
                        except: st.markdown('<p style="text-align:center;">-</p>', unsafe_allow_html=True)

                with c4: # Marcador Visitante
                    st.markdown(f'<p class="team-label">{vis}</p>', unsafe_allow_html=True)
                    pv = st.number_input("G", 0, 9, dv, key=f"pv_{i}_{j_global}", disabled=lock, label_visibility="collapsed")
                
                with c5: # Escudo Visitante
                    log_v = get_logo(vis)
                    if log_v: st.image(log_v, width=50)
                
                with c6: # Visibilidad
                    st.markdown("<p style='font-size:0.7em; text-align:center; font-weight:bold;'>👁️ PÚBLICA</p>", unsafe_allow_html=True)
                    pub = st.checkbox("Ver", dp=="SI", key=f"pb_{i}_{j_global}", disabled=lock, label_visibility="collapsed")
                
                # --- [NUEVA FILA PARA RONDAS KO: ¿QUIÉN PASA?] ---
                pasa_res = None
                if es_ronda_ko:
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_pasa1, col_pasa2 = st.columns([2, 4])
                    with col_pasa1:
                        st.markdown("<p style='font-size:0.85em; font-weight:bold; margin-top:10px;'>🏆 ¿Quién clasifica?</p>", unsafe_allow_html=True)
                        st.caption("Solo cuenta si hay empate tras 90'.")
                    with col_pasa2:
                        # Buscamos el índice del equipo guardado para el selectbox
                        lista_equipos = [loc, vis]
                        idx_defecto = lista_equipos.index(d_pasa) if d_pasa in lista_equipos else 0
                        pasa_res = st.selectbox("Selecciona equipo", lista_equipos, index=idx_defecto, key=f"pasa_{i}_{j_global}", disabled=lock, label_visibility="collapsed")

                st.markdown('</div>', unsafe_allow_html=True)
                
                # Guardamos datos en la lista de envío
                tiene_prediccion_previa = not u_preds[u_preds['Partido'] == m_id].empty if not u_preds.empty else False
                if not lock or tiene_prediccion_previa:
                    env.append({
                        "Usuario": st.session_state.user, 
                        "Jornada": j_global, 
                        "Partido": m_id, 
                        "P_L": pl, 
                        "P_V": pv, 
                        "P_Pasa": pasa_res, # Guardamos quién pasa
                        "Publica": "SI" if pub else "NO"
                    })

            # --- BOTÓN DE GUARDADO ---
            st.markdown("---")
            if st.button("💾 GUARDAR MIS PRONÓSTICOS", use_container_width=True, type="primary"):
                # Actualizar base de datos (Predicciones)
                otras_preds = df_p_all[~((df_p_all['Usuario'] == st.session_state.user) & (df_p_all['Jornada'] == j_global))]
                df_final_p = pd.concat([otras_preds, pd.DataFrame(env)], ignore_index=True)
                conn.update(worksheet="Predicciones", data=df_final_p)
                
                # Registro en el VAR (Logs)
                log_msg = f"📝 Actualizó sus porras del Mundial ({j_global})"
                log_entry = pd.DataFrame([{"Fecha": get_now_madrid().strftime("%Y-%m-%d %H:%M:%S"), "Usuario": st.session_state.user, "Accion": log_msg}])
                df_l_existente = leer_datos("Logs")
                conn.update(worksheet="Logs", data=pd.concat([df_l_existente, log_entry], ignore_index=True))
                
                st.cache_data.clear()
                st.success("✅ ¡Porras guardadas! El VAR ha registrado tu movimiento.")
                time.sleep(1.2)
                st.rerun()

    with tabs[1]: # --- 🌳 PESTAÑA SUPER BRACKET (MUNDIAL 2026) ---
        st.header("🌳 El Súper Bracket del Mundial")
        st.caption("Define el destino del mundo. Elige quién pasa en cada ronda y tus apuestas fijas.")

        # --- 0. CONFIGURACIÓN DE SEGURIDAD Y CIERRE ---
        FECHA_INAUGURAL = datetime.datetime(2026, 6, 11, 21, 0, 0)
        mercado_abierto = get_now_madrid() < FECHA_INAUGURAL
        
        if not mercado_abierto:
            st.error(f"🔒 **MERCADO CERRADO.** El Mundial ya ha comenzado ({FECHA_INAUGURAL.strftime('%d/%m %H:%M')}). Ya no se admiten cambios.")
        else:
            st.success(f"🔓 **MERCADO ABIERTO.** Tienes hasta el 11 de junio a las 21:00 para guardar tu cuadro definitivo.")

        if es_admin:
            st.warning("🛡️ Modo Admin: Solo puedes visualizar la estructura, no participar.")
        
        # --- 1. CARGA DE DATOS PREVIOS ---
        df_b_all = leer_datos("Brackets")
        b_prev = df_b_all[df_b_all['Usuario'] == st.session_state.user]
        
        # Diccionario de Grupos que pasaste
        GRUPOS_2026 = {
            "Grupo A": ["México", "Sudáfrica", "Corea del Sur", "Chequia"],
            "Grupo B": ["Canadá", "Bosnia y Hezegovina", "Qatar", "Suiza"],
            "Grupo C": ["Brasil", "Marruecos", "Haití", "Escocia"],
            "Grupo D": ["Estados Unidos", "Paraguay", "Australia", "Turquía"],
            "Grupo E": ["Alemania", "Curazao", "Costa de Marfil", "Ecuador"],
            "Grupo F": ["Países Bajos", "Japón", "Suecia", "Túnez"],
            "Grupo G": ["Bélgica", "Egipto", "Irán", "Nueva Zelanda"],
            "Grupo H": ["España", "Cabo Verde", "Arabia Saudita", "Uruguay"],
            "Grupo I": ["Francia", "Senegal", "Irak", "Noruega"],
            "Grupo J": ["Argentina", "Argelia", "Austria", "Jordania"],
            "Grupo K": ["Portugal", "R.D. Congo", "Uzbekistán", "Colombia"],
            "Grupo L": ["Inglaterra", "Croacia", "Ghana", "Panamá"]
        }

        # --- 2. INTERFAZ: FASE DE GRUPOS ---
        st.subheader("1️⃣ Posiciones de Grupo")
        col_g1, col_g2, col_g3 = st.columns(3)
        ganadores_grupos = {}

        for idx, (nombre_g, equipos) in enumerate(GRUPOS_2026.items()):
            target_col = [col_g1, col_g2, col_g3][idx % 3]
            with target_col:
                with st.container(border=True):
                    st.markdown(f"**{nombre_g}**")
                    # Valor por defecto desde DB o primero de la lista
                    def_1 = b_prev.iloc[0][f"{nombre_g}_1"] if not b_prev.empty else equipos[0]
                    sel_1 = st.selectbox(f"1º puesto", equipos, index=equipos.index(def_1) if def_1 in equipos else 0, key=f"sel1_{nombre_g}", disabled=not mercado_abierto)
                    
                    # Filtramos el 2º para que no sea igual al 1º
                    opciones_2 = [e for e in equipos if e != sel_1]
                    def_2 = b_prev.iloc[0][f"{nombre_g}_2"] if not b_prev.empty else opciones_2[0]
                    sel_2 = st.selectbox(f"2º puesto", opciones_2, index=opciones_2.index(def_2) if def_2 in opciones_2 else 0, key=f"sel2_{nombre_g}", disabled=not mercado_abierto)
                    
                    ganadores_grupos[f"{nombre_g}_1"] = sel_1
                    ganadores_grupos[f"{nombre_g}_2"] = sel_2

        st.divider()

        # --- 3. INTERFAZ: ELIMINATORIAS (CASCADA LÓGICA) ---
        st.subheader("2️⃣ Camino a la Final")
        st.caption("Los enfrentamientos se actualizan en tiempo real según tus selecciones anteriores.")

        # Lógica de emparejamientos de Dieciseisavos (Cruces A-L)
        # Definimos 16 cruces (32 equipos en total)
        # Usamos 1º y 2º de cada grupo + 8 plazas para los "Mejores Terceros" (T3)
        cruces_base = [
            ("Grupo A_1", "Grupo C_2"), ("Grupo B_1", "T3_1"), ("Grupo E_1", "Grupo F_2"), ("Grupo F_1", "Grupo E_2"),
            ("Grupo C_1", "T3_2"), ("Grupo D_1", "T3_3"), ("Grupo G_1", "Grupo H_2"), ("Grupo H_1", "Grupo G_2"),
            ("Grupo I_1", "T3_4"), ("Grupo J_1", "T3_5"), ("Grupo K_1", "Grupo L_2"), ("Grupo L_1", "Grupo K_2"),
            ("Grupo B_2", "Grupo A_2"), ("Grupo D_2", "T3_6"), ("Grupo I_2", "T3_7"), ("Grupo J_2", "T3_8")
        ]

        # --- DIECISEISAVOS (16 partidos -> 16 ganadores) ---
        st.markdown("#### 🏟️ Dieciseisavos de Final")
        cols_16 = st.columns(4) # 4 columnas de 4 partidos cada una
        ganadores_16 = []
        for i, (t1_key, t2_key) in enumerate(cruces_base):
            with cols_16[i // 4]: # Distribuye 16 partidos en 4 columnas
                # Obtenemos el nombre del equipo (si es un T3 ponemos un placeholder)
                eq_a = ganadores_grupos.get(t1_key, "Mejor 3º (A/B/C)")
                eq_b = ganadores_grupos.get(t2_key, "Mejor 3º (D/E/F)")
                
                def_16 = b_prev.iloc[0][f"G16_{i}"] if not b_prev.empty and f"G16_{i}" in b_prev.columns else eq_a
                res_16 = st.radio(f"Cruce {i+1}", [eq_a, eq_b], 
                                  index=[eq_a, eq_b].index(def_16) if def_16 in [eq_a, eq_b] else 0, 
                                  key=f"w16_{i}", disabled=not mercado_abierto)
                ganadores_16.append(res_16)
        
        # --- OCTAVOS (16 ganadores -> 8 partidos -> 8 ganadores) ---
        st.markdown("#### 🛡️ Octavos de Final")
        cols_8 = st.columns(4)
        ganadores_8 = []
        for i in range(0, len(ganadores_16), 2):
            with cols_8[(i//2) // 2]: # Distribuye 8 partidos en 4 columnas
                e1, e2 = ganadores_16[i], ganadores_16[i+1]
                def_8 = b_prev.iloc[0][f"G8_{i//2}"] if not b_prev.empty and f"G8_{i//2}" in b_prev.columns else e1
                res_8 = st.radio(f"Octavo {(i//2)+1}", [e1, e2], 
                                 index=[e1, e2].index(def_8) if def_8 in [e1, e2] else 0, 
                                 key=f"w8_{i//2}", disabled=not mercado_abierto)
                ganadores_8.append(res_8)
        
        # --- CUARTOS (8 ganadores -> 4 partidos -> 4 ganadores) ---
        st.markdown("#### 📊 Cuartos")
        cols_4 = st.columns(2)
        ganadores_4 = []
        for i in range(0, len(ganadores_8), 2):
            with cols_4[(i//2) // 2]:
                e1, e2 = ganadores_8[i], ganadores_8[i+1]
                def_4 = b_prev.iloc[0][f"G4_{i//2}"] if not b_prev.empty and f"G4_{i//2}" in b_prev.columns else e1
                res_4 = st.radio(f"Cuarto {(i//2)+1}", [e1, e2], 
                                 index=[e1, e2].index(def_4) if def_4 in [e1, e2] else 0, 
                                 key=f"w4_{i//2}", disabled=not mercado_abierto)
                ganadores_4.append(res_4)
        
        # --- SEMIFINALES (4 ganadores -> 2 partidos -> 2 ganadores) ---
        st.markdown("#### ⚔️ Semifinales")
        c_semi_cols = st.columns(2)
        ganadores_2 = []
        for i in range(0, len(ganadores_4), 2):
            with c_semi_cols[i//2]:
                e1, e2 = ganadores_4[i], ganadores_4[i+1] # AQUÍ YA NO DARÁ ERROR
                def_2 = b_prev.iloc[0][f"G2_{i//2}"] if not b_prev.empty and f"G2_{i//2}" in b_prev.columns else e1
                res_2 = st.radio(f"Semi {(i//2)+1}", [e1, e2], 
                                 index=[e1, e2].index(def_2) if def_2 in [e1, e2] else 0, 
                                 key=f"w2_{i//2}", disabled=not mercado_abierto)
                ganadores_2.append(res_2)
        # --- LA FINAL ---
        st.divider()
        st.markdown("<h3 style='text-align:center;'>🏆 GRAN FINAL DEL MUNDIAL</h3>", unsafe_allow_html=True)
        f1, f2 = ganadores_2[0], ganadores_2[1]
        col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
        with col_f2:
            def_c = b_prev.iloc[0]["Campeon"] if not b_prev.empty else f1
            campeon_final = st.selectbox("CAMPEÓN DEL MUNDO", [f1, f2], index=[f1, f2].index(def_c) if def_c in [f1, f2] else 0, key="campeon_final", disabled=not mercado_abierto)
            st.markdown(f"<h1 style='text-align:center; color:#ffd700;'>🥇 {campeon_final}</h1>", unsafe_allow_html=True)

        # --- 4. MERCADO LARGO PLAZO ---
        st.divider()
        st.subheader("⏳ 3️⃣ Mercado de Largo Plazo (Pre-Mundial)")
        # --- 4. MERCADO LARGO PLAZO (ACTUALIZADO CON MVP) ---
        st.divider()
        st.subheader("⚽ 3️⃣ Mercado Especial (Pre-Mundial)")
        c_lp1, c_lp2, c_lp3 = st.columns(3) # Cambiamos a 3 columnas
        
        with c_lp1:
            def_p = b_prev.iloc[0]["Pichichi"] if not b_prev.empty and "Pichichi" in b_prev.columns else ""
            pichichi_sel = st.text_input("⚽ Pichichi", value=def_p, placeholder="Máximo Goleador", disabled=not mercado_abierto)
        
        with c_lp2:
            def_z = b_prev.iloc[0]["Zamora"] if not b_prev.empty and "Zamora" in b_prev.columns else ""
            zamora_sel = st.text_input("🧤 Zamora", value=def_z, placeholder="Mejor Portero", disabled=not mercado_abierto)
            
        with c_lp3:
            # AÑADIMOS EL MVP AQUÍ
            def_mvp = b_prev.iloc[0]["MVP"] if not b_prev.empty and "MVP" in b_prev.columns else ""
            mvp_sel = st.text_input("⭐ MVP del Torneo", value=def_mvp, placeholder="Mejor Jugador", disabled=not mercado_abierto)
        # --- 5. BOTÓN DE GUARDADO ---
        st.markdown("---")
        if not es_admin:
            if st.button("💾 GUARDAR APUESTA MUNDIALISTA COMPLETA", use_container_width=True, type="primary", disabled=not mercado_abierto):
                # Recopilación de datos
                datos_bracket = {"Usuario": st.session_state.user}
                datos_bracket.update(ganadores_grupos)
                for i, v in enumerate(ganadores_16): datos_bracket[f"G16_{i}"] = v
                for i, v in enumerate(ganadores_8): datos_bracket[f"G8_{i}"] = v
                for i, v in enumerate(ganadores_4): datos_bracket[f"G4_{i}"] = v
                for i, v in enumerate(ganadores_2): datos_bracket[f"G2_{i}"] = v
                datos_bracket["Campeon"] = campeon_final
                datos_bracket["Pichichi"] = pichichi_sel
                datos_bracket["Zamora"] = zamora_sel

                # Guardar en GSheets
                df_b_actualizado = df_b_all[df_b_all['Usuario'] != st.session_state.user]
                df_final_b = pd.concat([df_b_actualizado, pd.DataFrame([datos_bracket])], ignore_index=True)
                
                try:
                    conn.update(worksheet="Brackets", data=df_final_b)
                    
                    # Log en el VAR
                    log_entry = pd.DataFrame([{
                        "Fecha": get_now_madrid().strftime("%Y-%m-%d %H:%M:%S"),
                        "Usuario": st.session_state.user,
                        "Accion": f"🌳 BRACKET: Registró su cuadro completo y apuestas fijas ({campeon_final})"
                    }])
                    df_l_existente = leer_datos("Logs")
                    conn.update(worksheet="Logs", data=pd.concat([df_l_existente, log_entry], ignore_index=True))
                    
                    st.success("✅ ¡Hecho! Tus predicciones para el Mundial 2026 están a salvo en el servidor.")
                    st.balloons()
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al conectar con la base de datos: {e}")
 
    with tabs[2]: # --- 🔮 PESTAÑA OTROS (TENDENCIAS + REVELACIONES) ---
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
                            pts = calcular_puntos_wc(p['P_L'], p['P_V'], match['R_L'], match['R_V'], tipo_p) if es_final else 0.0
                            
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

    
    with tabs[2]: # --- 🔮 PESTAÑA OTROS (TENDENCIAS + REVELACIONES) ---
        st.header("👀 Qué han puesto los demás")
        ahora = get_now_madrid()
        
        # Detectamos si es ronda de eliminación (KO)
        es_ronda_ko = any(x in j_global for x in ["Dieciseisavos", "Octavos", "Cuartos", "Semis", "Final"])

        # --- [SABIDURÍA POPULAR: TENDENCIAS] ---
        st.markdown("### 🔮 Sabiduría Popular (Tendencias)")
        preds_j = df_p_all[df_p_all['Jornada'] == j_global]

        if not preds_j.empty:
            with st.expander("📊 Ver tendencias de voto del grupo", expanded=True):
                # Usamos los partidos definidos en JORNADAS para esta jornada
                for loc, vis in JORNADAS[j_global]:
                    m_id = f"{loc}-{vis}"
                    m_preds = preds_j[preds_j['Partido'] == m_id]
                    total = len(m_preds)
                    
                    if total > 0:
                        # 1. Tendencia del Marcador (90 min)
                        v_l = len(m_preds[m_preds['P_L'] > m_preds['P_V']])
                        v_x = len(m_preds[m_preds['P_L'] == m_preds['P_V']])
                        v_v = len(m_preds[m_preds['P_L'] < m_preds['P_V']])
                        p_l, p_x, p_v = (v_l/total)*100, (v_x/total)*100, (v_v/total)*100

                        st.markdown(f"**{m_id}** (Marcador 90')")
                        st.markdown(f"""
                            <div style="display: flex; height: 18px; border-radius: 4px; overflow: hidden; background: #f1f5f9; margin-bottom:10px;">
                                <div style="width: {p_l}%; background: #3b82f6; color: white; font-size: 0.7em; text-align: center; line-height: 18px;" title="Gana {loc}">{p_l:.0f}%</div>
                                <div style="width: {p_x}%; background: #94a3b8; color: white; font-size: 0.7em; text-align: center; line-height: 18px;" title="Empate">{p_x:.0f}%</div>
                                <div style="width: {p_v}%; background: #f59e0b; color: white; font-size: 0.7em; text-align: center; line-height: 18px;" title="Gana {vis}">{p_v:.0f}%</div>
                            </div>
                        """, unsafe_allow_html=True)

                        # 2. Tendencia de Clasificación (Solo en KO)
                        if es_ronda_ko:
                            v_pasa_l = len(m_preds[m_preds['P_Pasa'] == loc])
                            v_pasa_v = len(m_preds[m_preds['P_Pasa'] == vis])
                            p_p_l, p_p_v = (v_pasa_l/total)*100, (v_pasa_v/total)*100
                            
                            st.markdown(f"<small>¿Quién clasifica? (Favorito: {'**'+loc+'**' if p_p_l > p_p_v else '**'+vis+'**'})</small>", unsafe_allow_html=True)
                            st.markdown(f"""
                                <div style="display: flex; height: 8px; border-radius: 10px; overflow: hidden; background: #e2e8f0; margin-bottom: 20px;">
                                    <div style="width: {p_p_l}%; background: #ef4444;"></div>
                                    <div style="width: {p_p_v}%; background: #1e293b;"></div>
                                </div>
                            """, unsafe_allow_html=True)

        st.divider()

        # --- [REVELACIONES: PARTIDOS EMPEZADOS O FINALIZADOS] ---
        df_r_all['Hora_DT'] = pd.to_datetime(df_r_all['Hora_Inicio'], errors='coerce')
        revelados = df_r_all[(df_r_all['Jornada'] == j_global) & ((df_r_all['Finalizado'] == "SI") | (ahora > df_r_all['Hora_DT']))]
        
        if not revelados.empty:
            st.markdown("### ✅ Apuestas Reveladas")
            revelados = revelados.sort_values("Hora_DT", ascending=True)

            for _, match in revelados.iterrows():
                m_id = match['Partido']
                es_final = match['Finalizado'] == "SI"
                res_real = f"{int(match['R_L'])}-{int(match['R_V'])}"
                tipo_p = match['Tipo']
                
                # Info de prórroga para la tabla
                txt_extra = f" (Pasa: {match['R_Pasa']})" if (es_final and match['Hubo_Prorroga'] == "SI") else ""
                estado_tag = "🔴 FINALIZADO" if es_final else "⏱️ EN JUEGO"
                
                with st.expander(f"📊 {m_id} — {estado_tag} (Real: {res_real}{txt_extra})"):
                    preds_match = df_p_all[(df_p_all['Jornada'] == j_global) & (df_p_all['Partido'] == m_id)]
                    
                    if not preds_match.empty:
                        resumen_partido = []
                        for _, p in preds_match.iterrows():
                            # USAMOS LA NUEVA FUNCIÓN DE PUNTOS
                            pts = calcular_puntos_wc(
                                p['P_L'], p['P_V'], match['R_L'], match['R_V'], 
                                tipo_p, p.get('P_Pasa'), match.get('R_Pasa'), 
                                match['Hubo_Prorroga'] == "SI"
                            ) if es_final else "Pte..."
                            
                            fila = {
                                "Jugador": p['Usuario'],
                                "Apostó": f"{int(p['P_L'])}-{int(p['P_V'])}",
                                "Puntos": pts
                            }
                            # Si es KO, mostramos a quién eligió para pasar
                            if es_ronda_ko:
                                fila["Pasa?"] = p.get('P_Pasa', '-')
                            
                            resumen_partido.append(fila)
                        
                        df_resumen = pd.DataFrame(resumen_partido)
                        st.table(df_resumen.sort_values("Puntos", ascending=False) if es_final else df_resumen.sort_values("Jugador"))
        else:
            st.info("Aún no ha empezado ningún partido de esta fase. ¡Las cartas siguen ocultas!")

        # --- [PRÓXIMOS PARTIDOS: PÚBLICAS] ---
        st.divider()
        st.markdown("### 🔒 Próximos Partidos (Públicas)")
        p_futuras = df_p_all[(df_p_all['Jornada'] == j_global) & (~df_p_all['Partido'].isin(revelados['Partido'])) & (df_p_all['Publica'] == "SI")]

        if not p_futuras.empty:
            for u in p_futuras['Usuario'].unique():
                if u != st.session_state.user:
                    with st.expander(f"👤 Apuestas de {u}"):
                        cols_mostrar = ['Partido', 'P_L', 'P_V']
                        if es_ronda_ko: cols_mostrar.append('P_Pasa')
                        st.table(p_futuras[p_futuras['Usuario'] == u][cols_mostrar])

    with tabs[4]: # --- 🏅 PALMARÉS (EDICIÓN MUNDIAL 2026) ---
        st.header("🏅 El Palmarés del Mundial")
        st.caption("Gloria, poder y humillación en el torneo más grande del mundo.")
        
        # --- 1. CONFIGURACIÓN INICIAL ---
        # Vaciamos los datos antiguos para empezar la cuenta del Mundial de cero
        gan_act, perd_act, lider_act = [], [], []
        
        # Cargamos puntos base (normalmente 0 al inicio del Mundial)
        pts_acumulados = {u: safe_float(df_base[df_base['Usuario'] == u]['Puntos'].values[0]) if not df_base[df_base['Usuario'] == u].empty else 0.0 for u in u_jugadores}

        # --- 2. CÁLCULO DE MEDALLAS POR CADA FASE ---
        # Recorremos cada fase definida en tu diccionario JORNADAS (Fase de Grupos, Octavos...)
        for j_n in JORNADAS.keys():
            partidos_j = df_r_all[df_r_all['Jornada'] == j_n]
            fin_j = partidos_j[partidos_j['Finalizado'] == "SI"]
            
            if not partidos_j.empty:
                pts_esta_j = []
                for u in u_jugadores:
                    u_p = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == j_n)]
                    
                    puntos_fase = 0.0
                    for r in u_p.itertuples():
                        m_real = fin_j[fin_j['Partido'] == r.Partido]
                        if not m_real.empty:
                            # --- LLAMADA A LA NUEVA FUNCIÓN DE PUNTOS WC ---
                            puntos_fase += calcular_puntos_wc(
                                r.P_L, r.P_V, 
                                m_real.iloc[0]['R_L'], m_real.iloc[0]['R_V'], 
                                m_real.iloc[0]['Tipo'],
                                getattr(r, 'P_Pasa', None),
                                m_real.iloc[0].get('R_Pasa'),
                                m_real.iloc[0].get('Hubo_Prorroga') == "SI"
                            )
                    
                    pts_esta_j.append({"Usuario": u, "Puntos": puntos_fase})
                    pts_acumulados[u] += puntos_fase # Sumamos al total para saber quién es líder general

                # Si la fase ha empezado a dar puntos, registramos ganadores y perdedores
                if pts_esta_j and len(fin_j) > 0:
                    df_res = pd.DataFrame(pts_esta_j)
                    max_p, min_p = df_res['Puntos'].max(), df_res['Puntos'].min()
                    
                    # Identificamos Líder(es) General(es) tras esta fase
                    max_general = max(pts_acumulados.values())
                    lideres_gen = [u for u, p in pts_acumulados.items() if p == max_general]

                    # Marcamos si la fase aún no ha terminado del todo
                    tag = " (En curso ⏳)" if len(fin_j) < len(partidos_j) else ""
                    
                    gan_act.append((j_n + tag, df_res[df_res['Puntos'] == max_p]['Usuario'].tolist()))
                    perd_act.append((j_n + tag, df_res[df_res['Puntos'] == min_p]['Usuario'].tolist()))
                    lider_act.append((j_n + tag, lideres_gen))

        # --- 🥇 SECCIÓN GANADORES (MEDALLAS POR FASE) ---
        st.subheader("🥇 Héroes del Mundial (Ganadores de Fase)")
        count_g = {}
        for j, us in gan_act:
            if "En curso" not in j: # Solo medallas oficiales de fases terminadas
                for u in us: count_g[u] = count_g.get(u, 0) + 1
        
        if count_g:
            df_g = pd.DataFrame(list(count_g.items()), columns=['U', 'V']).sort_values('V', ascending=False)
            c_g = st.columns(4)
            for i, (_, r) in enumerate(df_g.iterrows()):
                with c_g[i % 4]:
                    st.markdown(f"""<div style="text-align:center; padding:10px; border-radius:10px; background:linear-gradient(135deg, #fff9c4 0%, #ffeb3b 100%); border:2px solid #ffd700; margin-bottom:10px;">
                        <b style="color:#000; font-size:0.85em;">🏆 {r['U']}</b><br><span style="font-size:1.8em; font-weight:900; color:#000;">{int(r['V'])}</span><br><small style="color:#000; font-weight:bold;">MEDALLAS</small></div>""", unsafe_allow_html=True)
        else:
            st.info("Esperando al final de la primera fase para repartir medallas.")

        st.divider()

        # --- 👑 SECCIÓN LÍDERES (TRONO DEL MUNDIAL) ---
        st.subheader("👑 El Trono del Mundial (Líderes Generales)")
        st.caption("Quién ha mandado en la clasificación acumulada en cada etapa.")
        count_l = {}
        for j, us in lider_act:
            for u in us: count_l[u] = count_l.get(u, 0) + 1
        
        if count_l:
            df_l_rank = pd.DataFrame(list(count_l.items()), columns=['U', 'V']).sort_values('V', ascending=False)
            c_l = st.columns(4)
            for i, (_, r) in enumerate(df_l_rank.iterrows()):
                with c_l[i % 4]:
                    st.markdown(f"""<div style="text-align:center; padding:10px; border-radius:10px; background:linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%); border:2px solid #0ea5e9; margin-bottom:10px;">
                        <b style="color:#0369a1; font-size:0.85em;">👑 {r['U']}</b><br><span style="font-size:1.8em; font-weight:900; color:#0369a1;">{int(r['V'])}</span><br><small style="color:#0369a1; font-weight:bold;">FASES LÍDER</small></div>""", unsafe_allow_html=True)

        st.divider()

        # --- 🦎 SECCIÓN PERDEDORES: EL LAGARTO MUNDIALISTA ---
        st.subheader("🦎 El Lagarto del Mundial")
        count_p = {}
        for j, us in perd_act:
            if "En curso" not in j:
                for u in us: count_p[u] = count_p.get(u, 0) + 1
        
        if count_p:
            df_p_rank = pd.DataFrame(list(count_p.items()), columns=['U', 'V']).sort_values('V', ascending=False)
            c_p = st.columns(4)
            for i, (_, r) in enumerate(df_p_rank.iterrows()):
                st_color = "#32cd32" if r['V'] >= 2 else "#6c757d"
                with c_p[i % 4]:
                    st.markdown(f"""<div style="text-align:center; padding:10px; border-radius:10px; background:#f0fff0; border:2px solid {st_color}; margin-bottom:10px;">
                        <b style="color:#333; font-size:0.85em;">🦎 {r['U']}</b><br><span style="font-size:1.6em; font-weight:900; color:{st_color};">{int(r['V'])}</span><br><small style="color:{st_color}; font-weight:bold;">LAGARTOS</small></div>""", unsafe_allow_html=True)

        # --- 📅 ACTA HISTÓRICA DEL MUNDIAL ---
        st.divider()
        st.subheader("📅 Acta de Guerra: Resultados por Fase")
        if gan_act:
            cronologia = []
            # Invertimos para que la fase más reciente salga arriba
            for i in range(len(gan_act)-1, -1, -1):
                jor = gan_act[i][0]
                g = gan_act[i][1]
                p = perd_act[i][1]
                l = lider_act[i][1]
                
                cronologia.append({
                    "Fase / Etapa": jor,
                    "Héroe (🏆)": " & ".join(map(str, g)),
                    "Líder General (👑)": " & ".join(map(str, l)),
                    "Lagarto (🦎)": " & ".join(map(str, p))
                })
            st.table(pd.DataFrame(cronologia))
        else:
            st.write("Aún no hay actas registradas. El Mundial está por escribir.")
    
    with tabs[5]: # --- 📈 STATS PRO (MUNDIAL EDITION) ---
        sub_tabs = st.tabs(["👤 Análisis Individual", "🌍 Mapa de Continentes", "🔥 Power Ranking", "📉 Evolución"])

        with sub_tabs[0]: # --- ANÁLISIS INDIVIDUAL ---
            u_sel = st.selectbox("Analizar jugador:", u_jugadores, key="sb_stats_pro")
            
            # Función auxiliar para ADN Pro adaptada al Mundial
            def analizar_adn_wc(usuario, df_p, df_r):
                # Unimos predicciones con resultados finalizados
                df_m = pd.merge(df_p[df_p['Usuario'] == usuario], df_r[df_r['Finalizado'] == "SI"], on=['Jornada', 'Partido'])
                if df_m.empty: return None
                
                # Calculamos puntos con la nueva lógica
                df_m['Pts'] = df_m.apply(lambda x: calcular_puntos_wc(
                    x.P_L, x.P_V, x.R_L, x.R_V, x.Tipo, 
                    getattr(x, 'P_Pasa', None), x.get('R_Pasa'), x.get('Hubo_Prorroga') == "SI"
                ), axis=1)
                
                # Estadísticas de acierto
                ex = len(df_m[df_m.apply(lambda x: x.P_L == x.R_L and x.P_V == x.R_V, axis=1)])
                sig = len(df_m[df_m['Pts'] > 0]) - ex
                
                return {
                    "exactos": ex, "signos": sig, "fallos": len(df_m)-(ex+sig),
                    "total": len(df_m)
                }

            adn = analizar_adn_wc(u_sel, df_p_all, df_r_all)
            if adn:
                c1, c2, c3 = st.columns(3)
                c1.metric("🎯 Plenos", adn['exactos'])
                c2.metric("⚖️ Signos", adn['signos'])
                pct_acierto = (adn['exactos'] + adn['signos']) / adn['total'] * 100
                c3.metric("📈 Eficiencia", f"{pct_acierto:.1f}%")
                
                st.plotly_chart(px.pie(
                    values=[adn['exactos'], adn['signos'], adn['fallos']], 
                    names=['Plenos (Resultado)', 'Signos (1X2)', 'Fallos'], 
                    color_discrete_sequence=['#2baf2b', '#ffd700', '#ff4b4b'],
                    hole=0.4, title=f"Distribución de Aciertos: {u_sel}"
                ), use_container_width=True)

            st.markdown("---")
            st.subheader(f"🎯 Tendencia de Marcadores: {u_sel}")
            u_p_stats = df_p_all[df_p_all['Usuario'] == u_sel]
            if not u_p_stats.empty:
                fig_heat = px.density_heatmap(
                    u_p_stats, x="P_L", y="P_V",
                    labels={'P_L': 'Goles Local', 'P_V': 'Goles Visitante'},
                    color_continuous_scale="Viridis", text_auto=True, nbinsx=6, nbinsy=6
                )
                st.plotly_chart(fig_heat, use_container_width=True)

        with sub_tabs[1]: # --- 🌍 EFECTIVIDAD POR CONTINENTE ---
            st.subheader("🌍 Especialista por Continente")
            st.caption("¿En qué confederación eres un experto y en cuál un 'vendehumo'?")
            
            # Diccionario de confederaciones (Ejemplo, habría que completarlo)
            confed = {
                "España": "UEFA", "Argentina": "CONMEBOL", "México": "CONCACAF", 
                "Japón": "AFC", "Marruecos": "CAF", "USA": "CONCACAF", "Brasil": "CONMEBOL"
            }
            
            # Lógica para cruzar datos
            df_m_cont = pd.merge(df_p_all[df_p_all['Usuario'] == u_sel], df_r_all[df_r_all['Finalizado'] == "SI"], on=['Jornada', 'Partido'])
            if not df_m_cont.empty:
                def asignar_confed(partido):
                    loc = partido.split('-')[0]
                    return confed.get(loc, "Otros")
                
                df_m_cont['Confed'] = df_m_cont['Partido'].apply(asignar_confed)
                df_m_cont['Acierto'] = df_m_cont.apply(lambda x: 1 if (np.sign(x.P_L - x.P_V) == np.sign(x.R_L - x.R_V)) else 0, axis=1)
                
                res_cont = df_m_cont.groupby('Confed')['Acierto'].mean().reset_index()
                res_cont['Acierto'] *= 100
                
                fig_cont = px.bar(res_cont, x='Confed', y='Acierto', color='Acierto',
                                 title=f"% de Acierto en el Signo por Confederación",
                                 labels={'Acierto': '% Acierto', 'Confed': 'Confederación'},
                                 color_continuous_scale="RdYlGn")
                st.plotly_chart(fig_cont, use_container_width=True)
            else:
                st.info("Necesitamos partidos finalizados para calcular tu mapa continental.")

        with sub_tabs[2]: # --- 🔥 POWER RANKING ---
            st.subheader("🔥 Power Ranking: Quién llega más fuerte")
            
            # Tomamos las últimas 2 fases (ej. Jornada 3 y Octavos)
            fases_finalizadas = df_r_all[df_r_all['Finalizado'] == "SI"]['Jornada'].unique().tolist()
            num_fases = st.slider("Analizar rendimiento en últimas fases:", 1, 5, 2)
            fases_sel = fases_finalizadas[-num_fases:] if fases_finalizadas else []
            
            if fases_sel:
                st.caption(f"Calculando puntos en: {', '.join(fases_sel)}")
                pwr_data = []
                for u in u_jugadores:
                    pts_periodo = 0.0
                    u_p_pwr = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'].isin(fases_sel))]
                    
                    for r in u_p_pwr.itertuples():
                        m = df_r_all[(df_r_all['Partido'] == r.Partido) & (df_r_all['Finalizado'] == "SI")]
                        if not m.empty:
                            pts_periodo += calcular_puntos_wc(
                                r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'],
                                getattr(r, 'P_Pasa', None), m.iloc[0].get('R_Pasa'), m.iloc[0].get('Hubo_Prorroga') == "SI"
                            )
                    pwr_data.append({"Usuario": u, "Puntos": pts_periodo})
                
                df_pwr = pd.DataFrame(pwr_data).sort_values("Puntos", ascending=False)
                st.plotly_chart(px.bar(df_pwr, x='Usuario', y='Puntos', color='Puntos', color_continuous_scale="Magma"), use_container_width=True)
            else:
                st.info("El Power Ranking se activará tras la primera fase.")

        with sub_tabs[3]: # --- 📉 EVOLUCIÓN ---
            st.subheader("📉 El Gráfico de la Verdad")
            metrica = st.radio("Eje Y:", ["Puntos Acumulados", "Puesto en la General"], horizontal=True, key="metrica_evol")
            
            # Reutilizamos la lógica de evolución con calcular_puntos_wc
            fases_todas = list(JORNADAS.keys())
            historia_wc = []
            pts_tracking = {u: safe_float(df_base[df_base['Usuario'] == u]['Puntos'].values[0]) if not df_base[df_base['Usuario'] == u].empty else 0.0 for u in u_jugadores}
            
            # Punto de partida
            for u, p in pts_tracking.items(): historia_wc.append({"Fase": "Inicio", "Usuario": u, "Puntos": p})
            
            for f in fases_todas:
                res_f = df_r_all[(df_r_all['Jornada'] == f) & (df_r_all['Finalizado'] == "SI")]
                if res_f.empty: continue
                
                for u in u_jugadores:
                    u_p_f = df_p_all[(df_p_all['Usuario'] == u) & (df_p_all['Jornada'] == f)]
                    ganado_f = 0.0
                    for r in u_p_f.itertuples():
                        m = res_f[res_f['Partido'] == r.Partido]
                        if not m.empty:
                            ganado_f += calcular_puntos_wc(
                                r.P_L, r.P_V, m.iloc[0]['R_L'], m.iloc[0]['R_V'], m.iloc[0]['Tipo'],
                                getattr(r, 'P_Pasa', None), m.iloc[0].get('R_Pasa'), m.iloc[0].get('Hubo_Prorroga') == "SI"
                            )
                    pts_tracking[u] += ganado_f
                    historia_wc.append({"Fase": f, "Usuario": u, "Puntos": float(pts_tracking[u])})
            
            if len(historia_wc) > len(u_jugadores):
                df_evol = pd.DataFrame(historia_wc)
                df_evol['Puesto'] = df_evol.groupby('Fase')['Puntos'].rank(ascending=False, method='min')
                
                fig_evol = px.line(df_evol, x="Fase", y="Puntos" if metrica == "Puntos Acumulados" else "Puesto", 
                                  color="Usuario", markers=True)
                if metrica == "Puesto en la General": fig_evol.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_evol, use_container_width=True)
    
    with tabs[6]: # --- 🏆 DETALLES (LA LUPA DEL VAR) ---
        st.header("🏆 Desglose de Puntos por Partido")
        st.caption(f"Análisis detallado de la fase: **{j_global}**")

        # 1. Filtramos resultados finalizados de la fase seleccionada
        df_rf = df_r_all[(df_r_all['Jornada'] == j_global) & (df_r_all['Finalizado'] == "SI")]

        if not df_rf.empty:
            # 2. Creamos una matriz vacía: Filas (Partidos) x Columnas (Usuarios)
            m_p = pd.DataFrame(index=df_rf['Partido'].unique(), columns=u_jugadores)

            for p_id in m_p.index:
                # Información real del partido (Admin)
                inf = df_rf[df_rf['Partido'] == p_id].iloc[0]
                res_real = f"{int(inf['R_L'])}-{int(inf['R_V'])}"
                if inf.get('Hubo_Prorroga') == "SI":
                    res_real += f" (Pasa: {inf.get('R_Pasa')})"

                for u in u_jugadores:
                    # Predicción del usuario
                    up = df_p_all[(df_p_all['Usuario'] == u) & 
                                  (df_p_all['Jornada'] == j_global) & 
                                  (df_p_all['Partido'] == p_id)]
                    
                    if not up.empty:
                        # --- CÁLCULO CON LÓGICA MUNDIAL ---
                        pts = calcular_puntos_wc(
                            up.iloc[0]['P_L'], 
                            up.iloc[0]['P_V'], 
                            inf['R_L'], 
                            inf['R_V'], 
                            inf['Tipo'],
                            getattr(up.iloc[0], 'P_Pasa', None), 
                            inf.get('R_Pasa'), 
                            inf.get('Hubo_Prorroga') == "SI"
                        )
                        m_p.at[p_id, u] = float(pts)
                    else:
                        m_p.at[p_id, u] = 0.0

            # 3. Formateo y Visualización Premium
            st.markdown("#### Matriz de Puntos")
            
            # Aplicamos un estilo de colores para resaltar los aciertos altos (Plenos/Esquizo)
            df_styled = m_p.astype(float).style.background_gradient(
                cmap="Greens", axis=None
            ).format("{:.2f}")

            st.dataframe(df_styled, use_container_width=True)

            # 4. Leyenda informativa para evitar dudas
            with st.expander("ℹ️ ¿Cómo se han calculado estos puntos?"):
                st.write(f"""
                - **Marcador (90'):** Se compara el resultado real con tu porra.
                - **Pase de Ronda:** Si el acta indica 'Hubo Prórroga: SI', se ha sumado el bonus (+0.5 o +1.0) si acertaste el clasificado.
                - **Tipo de partido:** Los partidos **{inf['Tipo']}** tienen multiplicadores aplicados.
                """)
        else:
            st.info(f"Todavía no hay partidos finalizados en la fase **{j_global}**. ¡Vuelve cuando pite el árbitro!")
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHp6Znd6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/fNuXfHoZY3nqE/giphy.gif", width=300)

    with tabs[7]: # --- 🔮 SIMULADOR (EL DESTINO DEL MUNDIAL) ---
        sub_tabs = st.tabs(["📉 Supercomputadora: Destino Final", "🏟️ El Mundial según mis Porros"])
        
        with sub_tabs[0]:
            st.header("📉 Supercomputadora: El Trono del Mundial")
            st.caption("""
                Predicción probabilística basada en Montecarlo (5.000 futuros posibles). 
                Calcula tus opciones de ganar la Porra basándose en tu ritmo de acierto actual, 
                los puntos del Bracket que quedan por repartir y los partidos de eliminación directa.
            """)
            
            # --- BOTÓN DE EJECUCIÓN ---
            if st.button("🚀 LANZAR SIMULACIÓN MUNDIALISTA", use_container_width=True, type="primary"):
                with st.spinner("🔮 El Oráculo está procesando 5.000 finales posibles..."):
                    # Llamamos a la función de simulación (que debe usar calcular_puntos_wc internamente)
                    # Nota: Asegúrate de que la función 'simular_temporada_completa' en tu código 
                    # haya sido actualizada para usar la lógica de puntos del Mundial.
                    df_sim = simular_temporada_completa(df_hero, df_p_all, df_r_all)
                
                st.success("✅ Simulación completada. Los dioses del fútbol han hablado.")

                # --- 1. MATRIZ DE POSICIONES ---
                st.subheader("🎯 Matriz de Posiciones Finales")
                cols_puestos = [c for c in df_sim.columns if c.startswith("P") and c != "Puesto Medio"]
                
                st.dataframe(
                    df_sim.style.format({c: "{:.1f}%" for c in cols_puestos})
                    .format({"Puesto Medio": "{:.2f}"})
                    .background_gradient(subset=cols_puestos, cmap="YlGn") 
                    .highlight_max(subset=cols_puestos, color="#1e3a8a", axis=0), 
                    use_container_width=True, hide_index=True
                )

                st.divider()

                # --- 2. DASHBOARD DE PREVISIONES ---
                c1, c2 = st.columns(2)
                with c1:
                    fav = df_sim.sort_values("P1", ascending=False).iloc[0]
                    st.markdown(f"""
                        <div style="background:#f0f7ff; padding:20px; border-radius:15px; border-left:8px solid #007bff;">
                            <small style="color:#007bff; font-weight:bold;">🏆 FAVORITO AL TÍTULO DE LA PORRA</small><br>
                            <b style="font-size:1.5em; color:#1e293b;">{fav['Usuario']}</b><br>
                            <span style="font-size:1.1em; color:#1e293b;">{fav['P1']:.1f}% de opciones de ganar.</span>
                        </div>
                    """, unsafe_allow_html=True)

                with c2:
                    col_u = f"P{len(df_sim)}" 
                    lag = df_sim.sort_values(col_u, ascending=False).iloc[0]
                    st.markdown(f"""
                        <div style="background:#fff5f5; padding:20px; border-radius:15px; border-left:8px solid #ff4b4b;">
                            <small style="color:#ff4b4b; font-weight:bold;">🦎 CANDIDATO AL LAGARTO MUNDIALISTA</small><br>
                            <b style="font-size:1.5em; color:#1e293b;">{lag['Usuario']}</b><br>
                            <span style="font-size:1.1em; color:#1e293b;">{lag[col_u]:.1f}% de acabar último.</span>
                        </div>
                    """, unsafe_allow_html=True)

                # --- 3. GRÁFICO DE CAMPEONATO ---
                st.plotly_chart(px.bar(df_sim, x="Usuario", y="P1", color="P1", 
                                      title="Probabilidades de quedar 1º en la Porra (%)",
                                      color_continuous_scale="Viridis", text_auto='.1f'), use_container_width=True)
            
            else:
                st.info("Pulsa el botón para que la Supercomputadora analice los cruces del Mundial.")

        with sub_tabs[1]:
            st.header("🏟️ El Mundial según mis Porros")
            st.write("¿Cómo quedarían los Grupos si se cumplieran todas tus predicciones?")
            
            usr_sim = st.selectbox("Generar simulación basada en:", u_jugadores, key="sb_sim_porros")
            
            if st.button("📊 Generar Clasificación de Grupos Real", use_container_width=True):
                # En el mundial no hay una tabla única, sino grupos. 
                # Esta lógica asume que en JORNADAS tienes los equipos y sus grupos.
                # Para simplificar, mostramos cómo sumaría cada selección según el usuario.
                
                sim_equipos = {} # { "España": {"PJ": 0, "Pts": 0, "GF": 0, "GC": 0} }
                
                # Filtramos solo fase de grupos para esta tabla
                preds_usr = df_p_all[(df_p_all['Usuario'] == usr_sim) & (df_p_all['Jornada'].str.contains("Grupo", case=False))]
                
                for p in preds_usr.itertuples():
                    try:
                        tl, tv = p.Partido.split('-')
                        for eq in [tl, tv]:
                            if eq not in sim_equipos:
                                sim_equipos[eq] = {"PJ": 0, "V": 0, "E": 0, "D": 0, "GF": 0, "GC": 0, "Pts": 0}
                        
                        sim_equipos[tl]["PJ"] += 1; sim_equipos[tv]["PJ"] += 1
                        sim_equipos[tl]["GF"] += p.P_L; sim_equipos[tl]["GC"] += p.P_V
                        sim_equipos[tv]["GF"] += p.P_V; sim_equipos[tv]["GC"] += p.P_L
                        
                        if p.P_L > p.P_V:
                            sim_equipos[tl]["Pts"] += 3; sim_equipos[tl]["V"] += 1; sim_equipos[tv]["D"] += 1
                        elif p.P_V > p.P_L:
                            sim_equipos[tv]["Pts"] += 3; sim_equipos[tv]["V"] += 1; sim_equipos[tl]["D"] += 1
                        else:
                            sim_equipos[tl]["Pts"] += 1; sim_equipos[tv]["Pts"] += 1; sim_equipos[tl]["E"] += 1; sim_equipos[tv]["E"] += 1
                    except: continue

                if sim_equipos:
                    df_mundial = pd.DataFrame.from_dict(sim_equipos, orient='index').sort_values(["Pts", "GF"], ascending=False)
                    st.subheader(f"Tabla General Proyectada por {usr_sim}")
                    st.table(df_mundial)
                    st.caption("Nota: Esta tabla suma todos los grupos. En el Mundial real, solo clasificarían los mejores de cada grupo.")
                else:
                    st.warning("No hay predicciones de fase de grupos registradas para este usuario.")

    with tabs[8]: # --- 🎲 ORÁCULO (EL DESTINO DE LA FASE) ---
        if usa_oraculo:
            with st.spinner("🔮 El Oráculo está analizando 5.000 futuros posibles..."):
                # Llamamos a la versión del oráculo que simula 90' + Prórrogas
                prob = simular_oraculo(u_jugadores, df_p_all, df_r_all, j_global)
            
            if prob:
                st.subheader(f"🔮 Probabilidades de Victoria: {j_global}")
                st.caption("Análisis en tiempo real de quién ganará esta fase según los partidos que quedan.")
                
                # --- DISEÑO: Gráfico Izquierda | Lista Derecha ---
                col_izq, col_der = st.columns([1.6, 1], gap="medium")

                with col_izq:
                    # --- GRÁFICO DE TENDENCIA ---
                    df_hist = leer_datos("HistoricoOraculo")
                    
                    if not df_hist.empty and 'Jornada' in df_hist.columns:
                        df_hist_j = df_hist[df_hist['Jornada'] == j_global].copy()
                        
                        if not df_hist_j.empty:
                            # Limpieza de datos para el gráfico
                            df_hist_j['Probabilidad'] = pd.to_numeric(df_hist_j['Probabilidad'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
                            df_hist_j['Fecha_DT'] = pd.to_datetime(df_hist_j['Fecha'], errors='coerce')
                            df_hist_j = df_hist_j.sort_values('Fecha_DT')

                            fig_evo = px.line(
                                df_hist_j, x="Fecha_DT", y="Probabilidad", color="Usuario",
                                markers=True, line_shape="spline",
                                color_discrete_sequence=px.colors.qualitative.Pastel
                            )
                            fig_evo.update_layout(
                                yaxis_range=[-2, 102], 
                                hovermode="x unified", 
                                xaxis_title="Evolución durante la jornada",
                                yaxis_title="Opciones de ganar la fase (%)",
                                height=450, 
                                legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5)
                            )
                            st.plotly_chart(fig_evo, use_container_width=True)
                        else:
                            st.info("⌛ Recopilando datos para el gráfico de tendencias...")
                            st.image("https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmNrNjVlaW0xZzM0MWxubDQyZGhla3V4eXVnMHU5eHcwN3NxamRtMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Jap1tdjahS0rm/giphy.gif", width=250)

                with col_der:
                    # --- LISTADO DE SUPERVIVIENTES ---
                    st.markdown("#### 🎯 Supervivientes")
                    
                    # Ordenamos de mayor a menor probabilidad
                    for u, v in sorted(prob.items(), key=lambda x: x[1], reverse=True):
                        vivo = v > 0
                        card_bg = "#f0fff4" if vivo else "#fff5f5"
                        card_border = "#2baf2b" if vivo else "#ff4b4b"
                        
                        # Cálculo del Delta (Trend)
                        delta = 0.0
                        if not df_hist.empty:
                            u_h = df_hist[(df_hist['Usuario'] == u) & (df_hist['Jornada'] == j_global)]
                            if len(u_h) > 1:
                                try:
                                    v_pre = float(str(u_h.iloc[-2]['Probabilidad']).replace(',', '.'))
                                    delta = v - v_pre
                                except: pass
                        
                        color_d = "green" if delta > 0 else "red"
                        icon_d = "▲" if delta > 0 else "▼"
                        
                        # HTML de la tarjeta de probabilidad
                        st.markdown(f"""
                            <div style="background:{card_bg}; padding:12px; border-radius:10px; border-left:5px solid {card_border}; margin-bottom:10px; opacity: {1.0 if vivo else 0.5};">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <span style="font-weight:bold; color:#31333F;">{'🟢' if vivo else '💀'} {u}</span>
                                    <span style="font-size:1.3em; font-weight:900; color:{card_border};">{v:.1f}%</span>
                                </div>
                                <div style="text-align:right; font-size:0.8em; color:{color_d if vivo else '#999'};">
                                    {f'{icon_d} {abs(delta):.1f}%' if vivo and delta != 0 else ('ELIMINADO' if not vivo else 'ESTABLE')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if vivo:
                            st.progress(min(v/100, 1.0))
                        else:
                            st.divider()

                # --- CELEBRACIÓN DE VICTORIA ---
                if any(v >= 95 for v in prob.values()):
                    virtual_ganador = max(prob, key=prob.get)
                    st.balloons()
                    st.success(f"🏆 El Oráculo ha dictado sentencia: **{virtual_ganador}** tiene pie y medio en el Olimpo.")

        else:
            # Estado cuando hay demasiados partidos o ninguno
            st.info("🔮 El Oráculo está meditando... Se activará cuando queden entre 1 y 3 partidos para cerrar la fase.")
            st.image("https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ2IycHoyZ2pxeG9pdGU0OHYxODdsdzRldzFyd25lZDVwaTkzd3ZoMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/WPtzThAErhBG5oXLeS/giphy.gif", use_container_width=True)
    
    with tabs[8]: # --- ⚙️ PANEL DE CONTROL ADMIN (MUNDIAL 2026) ---
        if st.session_state.rol == "admin":
            st.header("⚙️ Panel de Control de Administrador")
            
            # --- SUB-PESTAÑAS ---
            t_ajustes, t_fotos, t_resultados = st.tabs([
                "⚖️ Ajustes y Bonos",
                "📸 Fotos de Perfil", 
                "⚽ Resultados Oficiales"
            ])

            # --- 1. SUB-PESTAÑA: AJUSTES (Sustituye a Puntos Base) ---
            with t_ajustes:
                st.subheader("⚖️ Gestión de Puntos Extra y Sanciones")
                st.info("Usa este formulario para sumar puntos del Bracket (Campeón, Pichichi) o aplicar sanciones.")
                
                with st.form("form_ajuste_pro"):
                    c1, c2 = st.columns(2)
                    u_target = c1.selectbox("Seleccionar Jugador:", u_jugadores)
                    pts_ajuste = c2.number_input("Puntos a añadir/restar:", value=0.0, step=0.25, help="Valores negativos para sanciones.")
                    concepto = st.text_input("Concepto del ajuste:", placeholder="Ej: Bono acierto Campeón del Mundo (+5pts)")
                    
                    submit_ajuste = st.form_submit_button("⚖️ Aplicar Cambio y Registrar en VAR", use_container_width=True)

                if submit_ajuste:
                    if concepto.strip() == "" or pts_ajuste == 0:
                        st.error("❌ Indica un concepto y una cantidad distinta de 0.")
                    else:
                        # Operación en PuntosBase
                        df_b_copy = df_base.copy()
                        # Asegurar limpieza de datos (comas por puntos)
                        df_b_copy['Puntos'] = pd.to_numeric(df_b_copy['Puntos'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)

                        if u_target in df_b_copy['Usuario'].values:
                            idx = df_b_copy[df_b_copy['Usuario'] == u_target].index
                            df_b_copy.loc[idx, 'Puntos'] += float(pts_ajuste)
                            
                            try:
                                conn.update(worksheet="PuntosBase", data=df_b_copy)
                                
                                # Log de auditoría para el VAR
                                log_entry = pd.DataFrame([{
                                    "Fecha": get_now_madrid().strftime("%Y-%m-%d %H:%M:%S"),
                                    "Usuario": "🛡️ ADMIN",
                                    "Accion": f"⚖️ AJUSTE: {pts_ajuste} pts a {u_target} ({concepto})"
                                }])
                                df_l_act = leer_datos("Logs")
                                conn.update(worksheet="Logs", data=pd.concat([df_l_act, log_entry], ignore_index=True))
                                
                                st.success(f"✅ Aplicado: {u_target} ahora tiene {pts_ajuste} puntos extra.")
                                st.cache_data.clear()
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al actualizar GSheets: {e}")

            # --- 2. SUB-PESTAÑA: FOTOS DE PERFIL ---
            with t_fotos:
                st.subheader("📸 Asignación de Avatares")
                if os.path.exists(PERFILES_DIR):
                    archivos = ["Ninguna"] + sorted([f for f in os.listdir(PERFILES_DIR) if f.endswith(('.jpeg', '.jpg', '.png', '.webp'))])
                    upd_f = []
                    for u in u_jugadores:
                        path_en_db = foto_dict.get(u, "")
                        nombre_actual = os.path.basename(path_en_db) if (isinstance(path_en_db, str) and path_en_db != "") else "Ninguna"
                        
                        col_u, col_sel = st.columns([2, 1])
                        col_u.write(f"Jugador: **{u}**")
                        idx_f = archivos.index(nombre_actual) if nombre_actual in archivos else 0
                        f_sel = col_sel.selectbox(f"Foto para {u}", archivos, index=idx_f, key=f"f_adm_{u}", label_visibility="collapsed")
                        
                        upd_f.append({"Usuario": u, "ImagenPath": f"{PERFILES_DIR}{f_sel}" if f_sel != "Ninguna" else ""})
                    
                    if st.button("🖼️ Guardar Cambios de Galería", use_container_width=True):
                        conn.update(worksheet="ImagenesPerfil", data=pd.DataFrame(upd_f))
                        st.cache_data.clear()
                        st.success("✅ Galería actualizada.")
                        st.rerun()

            # --- 3. SUB-PESTAÑA: RESULTADOS (LÓGICA WC) ---
            with t_resultados:
                st.subheader(f"🏟️ Acta de la Jornada: {j_global}")
                st.caption("Gestiona goles, prórrogas y pases de ronda.")
                
                r_env = []
                h_ops = [datetime.time(h, m).strftime("%H:%M") for h in range(0, 24) for m in [0, 15, 30, 45]]
                # Detectamos si la jornada seleccionada en el sidebar es de eliminación
                es_ko = any(x in j_global for x in ["Dieciseisavos", "Octavos", "Cuartos", "Semis", "Final"])

                for i, (loc, vis) in enumerate(JORNADAS.get(j_global, [])):
                    m_id = f"{loc}-{vis}"
                    prev = df_r_all[(df_r_all['Jornada']==j_global) & (df_r_all['Partido']==m_id)]
                    
                    # Carga de valores existentes
                    rl, rv, fin, tipo = 0, 0, False, "Normal"
                    pro, pasa = "NO", loc
                    f_val, h_val = datetime.datetime(2026, 6, 11).date(), "21:00"

                    if not prev.empty:
                        rl, rv = int(prev.iloc[0]['R_L']), int(prev.iloc[0]['R_V'])
                        fin = prev.iloc[0]['Finalizado'] == "SI"
                        tipo = prev.iloc[0]['Tipo']
                        pro = prev.iloc[0].get('Hubo_Prorroga', "NO")
                        pasa = prev.iloc[0].get('R_Pasa', loc)
                        try:
                            dt = datetime.datetime.strptime(str(prev.iloc[0]['Hora_Inicio']), "%Y-%m-%d %H:%M:%S")
                            f_val, h_val = dt.date(), dt.strftime("%H:%M")
                        except: pass

                    with st.expander(f"⚽ {m_id}", expanded=not fin):
                        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
                        n_tipo = c1.selectbox("Tipo", ["Normal", "Doble", "Esquizo"], index=["Normal", "Doble", "Esquizo"].index(tipo), key=f"at_{i}")
                        n_fecha = c2.date_input("Día", value=f_val, key=f"adate_{i}")
                        n_hora = c3.selectbox("Hora", h_ops, index=h_ops.index(h_val) if h_val in h_ops else 0, key=f"ah_{i}")
                        n_fin = c4.checkbox("¿Finalizado?", value=fin, key=f"afi_{i}")

                        c5, c6, c7, c8 = st.columns([1, 1, 1.5, 1.5])
                        n_rl = c5.number_input("L", 0, 9, rl, key=f"arl_{i}")
                        n_rv = c6.number_input("V", 0, 9, rv, key=f"arv_{i}")
                        
                        n_pro, n_pasa = "NO", ""
                        if es_ko:
                            n_pro = c7.selectbox("¿Hubo Prórroga?", ["NO", "SI"], index=0 if pro == "NO" else 1, key=f"apr_{i}")
                            n_pasa = c8.selectbox("¿Quién clasificó?", [loc, vis], index=[loc, vis].index(pasa) if pasa in [loc, vis] else 0, key=f"aps_{i}")
                        
                        r_env.append({
                            "Jornada": j_global, "Partido": m_id, "Tipo": n_tipo, 
                            "R_L": n_rl, "R_V": n_rv, "Hora_Inicio": f"{n_fecha} {n_hora}:00", 
                            "Finalizado": "SI" if n_fin else "NO",
                            "Hubo_Prorroga": n_pro, "R_Pasa": n_pasa
                        })

                if st.button("🏟️ PUBLICAR RESULTADOS OFICIALES", use_container_width=True, type="primary"):
                    otros = df_r_all[df_r_all['Jornada'] != j_global]
                    df_final = pd.concat([otros, pd.DataFrame(r_env)], ignore_index=True)
                    conn.update(worksheet="Resultados", data=df_final)
                    
                    st.cache_data.clear()
                    st.success("✅ ¡Acta guardada! Los puntos se han recalculado para todos.")
                    st.rerun()
        else:
            st.error("⛔ Acceso restringido al Alto Mando.")
    
    with tabs[9]: # --- 📜 PESTAÑA VAR (EL OJO QUE TODO LO VE) ---
        st.header("🏁 El VAR de la Porra")
        
        # Imagen de cabecera para dar tensión
        st.image("https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExczF4bGVvbmQ3eTVuam44dzExbXl4MDU5cmVsY24zMGdyb2dvNnpjdiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/U4DdzRe7wJP0aPI1Pa/giphy.gif", width=300)
        st.caption("Transparencia total: aquí se registra cada movimiento clave del Mundial.")

        # Usamos tu función blindada leer_datos para traer los logs más frescos
        df_logs = leer_datos("Logs")
        
        if not df_logs.empty:
            # Aseguramos que la fecha sea operable y ordenamos (lo más nuevo arriba)
            df_logs["Fecha"] = pd.to_datetime(df_logs["Fecha"], errors='coerce')
            df_logs = df_logs.sort_values("Fecha", ascending=False)
            
            st.markdown("---")
            
            # Mostramos los últimos 40 movimientos para no saturar la App
            for _, fila in df_logs.head(40).iterrows():
                usuario_log = str(fila['Usuario'])
                accion_txt = str(fila['Accion'])
                es_admin_log = "ADMIN" in usuario_log.upper() or "🛡️" in usuario_log
                
                # --- Lógica de Iconos Dinámicos del Mundial ---
                icon = "📝" # Predicción estándar
                if "⚖️ AJUSTE" in accion_txt: icon = "⚖️"
                if "⚽ OFICIAL" in accion_txt: icon = "🏟️"
                if "🔄 Modificó" in accion_txt: icon = "🔄"
                if "🌳 BRACKET" in accion_txt: icon = "🌳"
                if "🏆" in accion_txt: icon = "🏅"
                
                with st.container():
                    # Columnas: Hora | Usuario | Acción
                    c_time, c_user, c_act = st.columns([1.2, 1.2, 3])
                    
                    # 1. Fecha y Hora (Legible)
                    if pd.notnull(fila['Fecha']):
                        fecha_fmt = fila['Fecha'].strftime("%d/%m %H:%M")
                    else:
                        fecha_fmt = "??/??"
                    c_time.caption(f"🕒 {fecha_fmt}")
                    
                    # 2. Usuario con estilo (Admin vs Jugador)
                    if es_admin_log:
                        c_user.markdown(f"<span style='color:#ff4b4b; font-weight:bold;'>{usuario_log}</span>", unsafe_allow_html=True)
                    else:
                        c_user.markdown(f"**{usuario_log}**")
                    
                    # 3. Cuadro de Acción
                    if es_admin_log:
                        # Los ajustes de puntos o resultados oficiales van en azul/amarillo
                        if "⚖️" in icon:
                            c_act.warning(f"{icon} {accion_txt.replace('⚖️ AJUSTE:', '')}")
                        else:
                            c_act.info(f"{icon} {accion_txt}")
                    else:
                        # Movimientos normales de los jugadores
                        c_act.write(f"{icon} {accion_txt}")
                    
                    st.divider()
        else:
            st.info("El historial está vacío. ¡Que empiece el baile!")
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHp6Znd6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6Z3Z6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/fNuXfHoZY3nqE/giphy.gif", width=200)





