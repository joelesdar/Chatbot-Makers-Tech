import streamlit as st
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=API_KEY)

st.title("Makers Tech")
st.subheader("Asistente para compras")
messages = [("system", "Eres un asistente para una empresa de comercio eléctronico de tecnología y tu labor es dar respuesta a los usuarios sobre los distintos productos")]

# Iniciar el historial del chat
if "messages" not in st.session_state:
  st.session_state.messages = []

# Mostrar mensajes de chat del historial al recargar la app
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# Reaccionar a la entrada del usuario
if prompt := st.chat_input("Escribe tu mensaje"):
  # Mostrar mensaje del usuario
  st.chat_message("user").markdown(prompt)
  # Agregar mensaje del usuario en el contenedor de mensajes del chat
  st.session_state.messages.append({"role": "user", "content": prompt})
  messages.append(["human", prompt])

  response = llm.invoke(messages).content
  # Mostrar respuesta del asistente
  with st.chat_message("assistant"):
      st.markdown(response)
  # Agregar respuesta del asistente al historial del chat
  st.session_state.messages.append({"role": "assistant", "content": response})

  