import streamlit as st
import openai
import re

# Configuración de la API de OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Función de limpieza de chat
def limpiar_chat(contenido):
    patron = r"^.*? - "
    lineas_limpiadas = [re.sub(patron, "", linea).strip() for linea in contenido.splitlines()]
    return "\n".join(lineas_limpiadas)

# Función para dividir el archivo en fragmentos de palabras
def fragmentar_texto(texto, max_palabras):
    palabras = texto.split()
    fragmentos = []
    for i in range(0, len(palabras), max_palabras):
        fragmento = " ".join(palabras[i:i + max_palabras])
        fragmentos.append(fragmento)
    return fragmentos

# Función para analizar preguntas frecuentes en cada fragmento
def analizar_preguntas_frecuentes(fragmento, preguntas_existentes):
    respuesta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente que identifica preguntas frecuentes en chats de soporte técnico."},
            {"role": "user", "content": f"Analiza el siguiente contenido y extrae solo las preguntas frecuentes:\n\n{fragmento}"}
        ]
    )
    nuevas_preguntas = respuesta.choices[0].message['content'].split("\n")
    
    # Consolidar preguntas sin duplicados
    for pregunta in nuevas_preguntas:
        preguntas_existentes.add(pregunta.strip())
    return preguntas_existentes

# Interfaz de Streamlit
st.title("Analizador de Preguntas Frecuentes en Chats de WhatsApp")

# Input 1: Cantidad de palabras por fragmento
cantidad_palabras = st.number_input("Cantidad de palabras por fragmento", min_value=1, step=1)

# Input 2: Cargar archivo original del chat
archivo_subido = st.file_uploader("Sube el archivo original del chat (.txt)", type="txt")

if archivo_subido and cantidad_palabras:
    # Paso 1: Limpiar el archivo
    contenido = archivo_subido.read().decode("utf-8")
    chat_limpio = limpiar_chat(contenido)
    
    # Paso 2: Fragmentar el archivo limpio
    fragmentos = fragmentar_texto(chat_limpio, cantidad_palabras)
    
    # Paso 3: Análisis de preguntas frecuentes en fragmentos
    preguntas_frecuentes_consolidadas = set()
    for idx, fragmento in enumerate(fragmentos):
        with st.spinner(f"Analizando fragmento #{idx+1}..."):
            preguntas_frecuentes_consolidadas = analizar_preguntas_frecuentes(fragmento, preguntas_frecuentes_consolidadas)
    
    # Paso 4: Output final - consolidar preguntas frecuentes y permitir descarga
    resultado_final = "\n".join(preguntas_frecuentes_consolidadas)
    st.download_button(
        label="Descargar Preguntas Frecuentes",
        data=resultado_final,
        file_name="preguntas_frecuentes.txt",
        mime="text/plain"
    )
