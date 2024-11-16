import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Cargar archivo del inventario
path = "inventario_makers_tech.csv"
df = pd.read_csv(path)

# Cargar API key
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Configurar modelo
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=API_KEY)

# Función para generar recomendaciones personalizadas
def generar_recomendaciones_personalizadas(intereses, rango_precios, caracteristicas):
    min_precio, max_precio = rango_precios
    recomendaciones = df.copy()

    # Filtrar por categoría
    if intereses:
        recomendaciones = recomendaciones[recomendaciones["Categoria"].str.contains(intereses, case=False, na=False)]

    # Filtrar por rango de precios
    recomendaciones = recomendaciones[
        (recomendaciones['Precio'] >= min_precio) & (recomendaciones['Precio'] <= max_precio)
    ]

    # Filtrar por características (si existen)
    if caracteristicas:
        recomendaciones['Match'] = recomendaciones['Descripcion'].str.contains(caracteristicas, case=False, na=False)
        recomendaciones['Match Score'] = np.where(recomendaciones['Match'], 1, 0)
    else:
        recomendaciones['Match Score'] = 0

    # Crear recomendaciones basadas en un score
    recomendaciones['Recomendación'] = pd.cut(
        recomendaciones['Match Score'],
        bins=[-1, 0.5, 0.8, 1.1],
        labels=["No Recomendado", "Recomendado", "Altamente Recomendado"]
    )

    return recomendaciones

# Interfaz Streamlit
st.title("Makers Tech")
st.subheader("Bienvenido al sistema de la tienda")

# Login simulado
if "user_id" not in st.session_state:
    st.session_state.user_id = None
    st.session_state.role = None

if st.session_state.user_id is None:
    username = st.text_input("Inicia sesión con tu nombre de usuario (obligatorio):")
    role = st.radio("¿Eres administrador o cliente?", ["Cliente", "Administrador"])

    if role == "Administrador":
        password = st.text_input("Ingresa tu contraseña:", type="password")

    if st.button("Ingresar"):
        if not username.strip():
            st.error("El nombre de usuario es obligatorio.")
        elif role == "Administrador" and password != "1234":
            st.error("Contraseña incorrecta. Intenta nuevamente.")
        else:
            st.session_state.user_id = username.strip()
            st.session_state.role = role
            st.success(f"Bienvenido, {username} como {role.lower()}!")

else:
    # Menú lateral con botón de cerrar sesión
    st.sidebar.title(f"Menú de {st.session_state.user_id} ({st.session_state.role})")
    opciones = ["Asesoría de productos", "Recomendaciones"]
    if st.session_state.role == "Administrador":
        opciones.append("Panel de Administrador")

    opcion = st.sidebar.radio("Selecciona una opción:", opciones)

    if st.sidebar.button("Cerrar sesión", key="logout"):
        st.session_state.user_id = None
        st.session_state.role = None
        st.experimental_rerun()

    # Opción 1: Asesoría de productos
    if opcion == "Asesoría de productos":
        st.subheader("Chat Asesor Virtual")
        st.write("Haz preguntas sobre los productos disponibles en la tienda.")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        system_instruction = (
            "Eres un asistente virtual y un experto en aparatos eléctricos que ayuda a los usuarios con preguntas sobre los productos disponibles."
        )

        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt := st.chat_input("Escribe tu pregunta:"):
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            inventario_contexto = df.to_dict(orient="records")
            prompt_con_contexto = (
                f"Datos del inventario: {inventario_contexto}\n\nPregunta: {prompt}"
            )
            response = llm.invoke([
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt_con_contexto}
            ]).content

            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Opción 2: Recomendaciones
    elif opcion == "Recomendaciones":
        st.subheader("Productos Recomendados")
        intereses = st.text_input("¿Qué categoría de producto te interesa? (Ejemplo: Laptop, PC, Tablet)")
        rango_precios = st.slider("Selecciona tu rango de precios (USD):", 0, 5000, (100, 4900))
        caracteristicas = st.text_input("¿Qué características buscas? (Opcional, ejemplo: 'pantalla táctil', '8GB RAM')")

        if st.button("Generar Recomendaciones"):
            recomendaciones = generar_recomendaciones_personalizadas(intereses, rango_precios, caracteristicas)

            for categoria in ["Altamente Recomendado", "Recomendado", "No Recomendado"]:
                st.write(f"### {categoria}")
                st.dataframe(recomendaciones[recomendaciones['Recomendación'] == categoria], use_container_width=True)

    # Opción 3: Panel de Administrador (solo para administradores)
    elif opcion == "Panel de Administrador" and st.session_state.role == "Administrador":
        st.subheader("Métricas del Inventario")

        # Ejemplo de métricas: productos por categoría
        st.write("### Productos por categoría")
        productos_por_categoria = df['Categoria'].value_counts()

        # Gráfico con Matplotlib
        fig, ax = plt.subplots()
        productos_por_categoria.plot(kind='bar', ax=ax, color='skyblue')
        ax.set_title("Productos por Categoría")
        ax.set_xlabel("Categoría")
        ax.set_ylabel("Cantidad")
        st.pyplot(fig)

        # Mostrar tabla de productos con baja cantidad
        st.write("### Productos con bajo stock (menos de 5 unidades):")
        bajo_stock = df[df['Cantidad'] < 5]
        st.dataframe(bajo_stock, use_container_width=True)

        # Mostrar promedio de precios por categoría
        st.write("### Promedio de precios por categoría")
        precios_por_categoria = df.groupby('Categoria')['Precio'].mean()

        # Gráfico con Matplotlib
        fig, ax = plt.subplots()
        precios_por_categoria.plot(kind='bar', ax=ax, color='lightgreen')
        ax.set_title("Promedio de Precios por Categoría")
        ax.set_xlabel("Categoría")
        ax.set_ylabel("Precio Promedio (USD)")
        st.pyplot(fig)

        # Resumen estadístico del inventario
        st.write("### Resumen estadístico del inventario:")
        st.dataframe(df.describe())
