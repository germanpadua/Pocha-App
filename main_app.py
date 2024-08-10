import streamlit as st
import pandas as pd
import pickle
import plotly.graph_objects as go

# Función para calcular el número de rondas
def calcular_rondas(num_cartas, num_jugadores):
    rondas_por_jugador = num_cartas // num_jugadores
    
    rondas_totales = 2 * (rondas_por_jugador - 1)  # Sumamos +1 para la ronda con el máximo número de cartas
    rondas_totales += 2 * num_jugadores
    return rondas_totales, rondas_por_jugador

# Función para generar los nombres de las rondas
def generar_nombres_rondas(num_jugadores, rondas_por_jugador):
    nombres_rondas = []
    contador_rondas = 1
    
    # Fase ascendente
    for i in range(1, rondas_por_jugador): 
        nombres_rondas.append(f"{contador_rondas}. {i} cartas")
        contador_rondas += 1
        
    # Fase con el número máximo de cartas
    for i in range(num_jugadores):
        nombres_rondas.append(f"{contador_rondas}. {rondas_por_jugador} cartas")
        contador_rondas += 1
    
    # Fase descendente
    for i in range(rondas_por_jugador - 1, 0, -1):
        nombres_rondas.append(f"{contador_rondas}. {i} cartas")
        contador_rondas += 1
    
    for i in range(num_jugadores):
        nombres_rondas.append(f"{contador_rondas}. {rondas_por_jugador} cartas")
        contador_rondas += 1
    
    return nombres_rondas

# Función para pasar de ronda y actualizar puntuaciones
def pasar_ronda(): 
    for jugador in range(num_jugadores):
        apostadas = st.session_state.apuestas[st.session_state.ronda_actual][jugador]
        conseguidas = manos_conseguidas[jugador]
        if apostadas == conseguidas:
            puntos = 10 + (5 * apostadas)
        else:
            diferencia = abs(apostadas - conseguidas)
            puntos = -5 * diferencia
        
        # Sumar los puntos obtenidos a las puntuaciones acumuladas
        st.session_state.acumuladas[jugador] += puntos
        st.session_state.puntuaciones[st.session_state.ronda_actual][jugador] = st.session_state.acumuladas[jugador]
    
    st.session_state.ronda_actual += 1

# Función para actualizar y mostrar la tabla de puntuaciones
def actualizar_tabla(num_rondas, nombres_rondas):
    # Crear DataFrame con las puntuaciones combinadas
    df_puntuaciones = pd.DataFrame()

    for jugador in range(num_jugadores):
        combinadas = [f"{st.session_state.apuestas[ronda][jugador]} / {st.session_state.conseguidas[ronda][jugador]} / {st.session_state.puntuaciones[ronda][jugador]}" if ronda < st.session_state.ronda_actual else "- / - / -" for ronda in range(num_rondas)]
        
        # Añadir la columna combinada al DataFrame
        df_puntuaciones[f"{jugadores[jugador]} Ap / Co / Pts"] = combinadas
    
    # Verificación para asegurarse de que las longitudes coincidan
    if len(nombres_rondas) == len(df_puntuaciones):
        df_puntuaciones.index = nombres_rondas  # Usar nombres personalizados de las rondas
    else:
        st.error("Error: El número de rondas no coincide con los nombres de las rondas.")
    
    # Mostrar la tabla utilizando st.dataframe con configuración de columna
    st.write("### Tabla de Puntuaciones Acumuladas por Ronda")
    st.dataframe(
        df_puntuaciones,
        column_config={
            df_puntuaciones.index.name: st.column_config.Column(
                "Rondas", width="small"  # Ajustar la anchura de la columna de las rondas
            )
        },
        hide_index=False,  # Mostrar el índice que tiene los nombres de las rondas
    )

    # Mostrar la puntuación total final
    st.write("### Puntuaciones Totales Finales")
    st.dataframe(pd.DataFrame([st.session_state.acumuladas], columns=jugadores))

# Función para mostrar gráfico de la evolución de las puntuaciones
def mostrar_grafico_evolucion(num_rondas, nombres_rondas):
    fig = go.Figure()
    rondas = ["Inicio"] + nombres_rondas  # Incluir "Inicio" en lugar de "Ronda 0"
    
    for jugador in range(num_jugadores):
        puntuaciones = [0]  # Empezar con 0 en la "Inicio"
        puntuaciones += [st.session_state.puntuaciones[ronda][jugador] for ronda in range(num_rondas)]
        fig.add_trace(go.Scatter(x=rondas, y=puntuaciones, mode='lines+markers', name=f"{jugadores[jugador]}"))

    fig.update_layout(
        title="Evolución de las Puntuaciones",
        xaxis_title="Ronda",
        yaxis_title="Puntuación",
        xaxis=dict(tickmode='linear'),
        yaxis=dict(tickformat=".0f"),
        height=400
    )
    
    st.plotly_chart(fig)

# Título de la aplicación
st.title("Puntuaciones de la Pocha")

# Número de jugadores
num_jugadores = st.number_input("Número de jugadores", min_value=2, max_value=10, value=4)

# Nombres de los jugadores
jugadores = []
for i in range(num_jugadores):
    jugadores.append(st.text_input(f"Nombre del jugador {i+1}", value=f"Jugador {i+1}"))

num_cartas = st.number_input("Número de cartas", min_value=36, max_value=50, value=48)

# Calcular el número de rondas basado en las reglas proporcionadas
num_rondas, rondas_por_jugador = calcular_rondas(num_cartas, num_jugadores)

st.write(f"Se jugarán {num_rondas} rondas en total.")

nombres_rondas = generar_nombres_rondas(num_jugadores, rondas_por_jugador)

# Inicializar el estado de la aplicación
if 'ronda_actual' not in st.session_state:
    st.session_state.ronda_actual = 0  # Comienza en la ronda 0
if 'puntuaciones' not in st.session_state:
    st.session_state.puntuaciones = [[0 for _ in range(num_jugadores)] for _ in range(num_rondas)]  # Inicializar según el número de rondas calculadas
if 'acumuladas' not in st.session_state:
    st.session_state.acumuladas = [0 for _ in range(num_jugadores)]  # Puntuaciones acumuladas
if 'apuestas' not in st.session_state:
    st.session_state.apuestas = [[0 for _ in range(num_jugadores)] for _ in range(num_rondas)]  # Apuestas por ronda
if 'conseguidas' not in st.session_state:
    st.session_state.conseguidas = [[0 for _ in range(num_jugadores)] for _ in range(num_rondas)]  # Manos conseguidas por ronda

if st.session_state.ronda_actual < num_rondas:  # Limitar a las rondas calculadas
    st.header(f"{nombres_rondas[st.session_state.ronda_actual]}")
    # Crear columnas para "Apuestas de manos" y "Manos conseguidas"
    col1, col2 = st.columns(2)
    
    # Solicitar apuestas de manos
    with col1:
        st.write("### Apuestas de manos")
        
    with col2:
        st.write("### Manos conseguidas")
        
    manos_conseguidas = []
    for jugador in range(num_jugadores):
        with col1:
            st.session_state.apuestas[st.session_state.ronda_actual][jugador] = st.number_input(
                f"Manos apostadas por {jugadores[jugador]}",
                key=f"apuesta_ronda{st.session_state.ronda_actual}_jugador{jugador}",
                min_value=0
            )
        
        with col2:
            manos = st.number_input(
                f"Manos conseguidas por {jugadores[jugador]}",
                key=f"conseguidas_ronda{st.session_state.ronda_actual}_jugador{jugador}",
                min_value=0
            )
            manos_conseguidas.append(manos)
            st.session_state.conseguidas[st.session_state.ronda_actual][jugador] = manos

    # Botón para pasar de ronda y actualizar la tabla
    st.button(label="Guardar y pasar a la siguiente ronda", on_click=pasar_ronda)
    actualizar_tabla(num_rondas, nombres_rondas)
else:
    st.write("Todas las rondas han sido completadas.")
    actualizar_tabla(num_rondas, nombres_rondas)
    mostrar_grafico_evolucion(num_rondas, nombres_rondas)

# Guardar puntuaciones
if st.button("Guardar puntuaciones"):
    with open("puntuaciones.pkl", "wb") as f:
        pickle.dump(st.session_state.puntuaciones, f)
    st.write("Puntuaciones guardadas.")

# Cargar puntuaciones
if st.button("Cargar puntuaciones"):
    try:
        with open("puntuaciones.pkl", "rb") as f:
            st.session_state.puntuaciones = pickle.load(f)
        st.write("Puntuaciones cargadas.")
    except FileNotFoundError:
        st.write("No se encontraron puntuaciones guardadas.")
