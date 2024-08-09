import streamlit as st
import pandas as pd
import pickle

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
    
    # No se llama aquí a actualizar_tabla()

# Función para actualizar y mostrar la tabla de puntuaciones
def actualizar_tabla():
    # Crear DataFrame con las puntuaciones acumuladas
    df_puntuaciones = pd.DataFrame(st.session_state.puntuaciones, columns=jugadores)
    df_puntuaciones.index = [f"Ronda {i+1}" for i in range(10)]  # Añadir el índice de ronda
    
    # Crear columna para Apostadas / Conseguidas
    for jugador in range(num_jugadores):
        apostadas_conseguidas = ["-"] * 10  # Inicializar con "-" para todas las rondas
        for ronda in range(st.session_state.ronda_actual):
            apostadas_conseguidas[ronda] = f"{st.session_state.apuestas[ronda][jugador]} / {st.session_state.conseguidas[ronda][jugador]}"
        
        # Añadir las columnas al DataFrame
        df_puntuaciones.insert(
            2 * jugador,  # Insertar antes de la columna del jugador correspondiente
            f"{jugadores[jugador]} Apostadas / Conseguidas",
            apostadas_conseguidas
        )
    
    st.write("### Tabla de Puntuaciones Acumuladas por Ronda")
    st.dataframe(df_puntuaciones)
    
    # Mostrar la puntuación total final
    st.write("### Puntuaciones Totales Finales")
    st.dataframe(pd.DataFrame([st.session_state.acumuladas], columns=jugadores))

# Título de la aplicación
st.title("Puntuaciones de la Pocha")

# Número de jugadores
num_jugadores = st.number_input("Número de jugadores", min_value=2, max_value=10, value=4)

# Nombres de los jugadores
jugadores = []
for i in range(num_jugadores):
    jugadores.append(st.text_input(f"Nombre del jugador {i+1}", value=f"Jugador {i+1}"))

# Inicializar el estado de la aplicación
if 'ronda_actual' not in st.session_state:
    st.session_state.ronda_actual = 0  # Comienza en la ronda 0
if 'puntuaciones' not in st.session_state:
    st.session_state.puntuaciones = [[0 for _ in range(num_jugadores)] for _ in range(10)]  # 10 rondas por defecto
if 'acumuladas' not in st.session_state:
    st.session_state.acumuladas = [0 for _ in range(num_jugadores)]  # Puntuaciones acumuladas
if 'apuestas' not in st.session_state:
    st.session_state.apuestas = [[0 for _ in range(num_jugadores)] for _ in range(10)]  # Apuestas por ronda
if 'conseguidas' not in st.session_state:
    st.session_state.conseguidas = [[0 for _ in range(num_jugadores)] for _ in range(10)]  # Manos conseguidas por ronda

if st.session_state.ronda_actual < 10:  # Limitar a 10 rondas
    st.header(f"Ronda {st.session_state.ronda_actual + 1}")
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
else:
    st.write("Todas las rondas han sido completadas.")

# Mostrar la tabla de puntuaciones solo al final
actualizar_tabla()

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
