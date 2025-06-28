import streamlit as st
import pickle
import pandas as pd
import os
import subprocess

st.set_page_config('Encuentra tu Pelicula!', layout='wide')

similarity_path = "modelo/similarity.pkl"
similarity_id = "1PByfAluVuS1GPYCnTYp_NP_DLiLhWD5C"

if not os.path.exists(similarity_path):
    os.makedirs("modelo", exist_ok=True)
    url = f"https://drive.google.com/uc?id={similarity_id}"
    subprocess.run(["gdown", url, "-O", similarity_path], check=True)

@st.cache_data
def cargar_datos():  
    df = pickle.load(open("modelo/movie_list.pkl", "rb"))
    similarity = pickle.load(open("modelo/similarity.pkl", "rb"))
    kmeans_model = pickle.load(open("modelo/kmeans_model.pkl", "rb"))
    return df, similarity, kmeans_model

df, similarity, kmeans_model = cargar_datos()

url_base_poster = "https://image.tmdb.org/t/p/w500"

def obtener_poster(poster_path):
    if pd.isna(poster_path):
        return "https://via.placeholder.com/500x750?text=No+Image"
    return url_base_poster + poster_path

def recomendar_clustered(titulo, df, similarity, kmeans_model, top_k=5):
    indices = df[df['title'].str.lower() == titulo.lower()].index

    if len(indices) == 0:
        return None

    idx = indices[0]
    cluster = df.iloc[idx]['cluster']

    # Películas del mismo cluster
    cluster_indices = df[df['cluster'] == cluster].index

    sim_scores = [(i, similarity[idx][i]) for i in cluster_indices if i != idx]
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[:top_k]

    recomendadas = []
    for i in sim_scores:
        row = df.iloc[i[0]]
        recomendadas.append({
            "title": row["title"],
            "poster": obtener_poster(row["poster_path"])
        })
    return recomendadas


#Interfaz
st.title("🎬 Recomendador de Películas")
df["title"] = df["title"].astype(str)
df["title"] = df["title"].str.replace(r"[\n\r\t]+", " ", regex=True)
df["title"] = df["title"].str.strip()
df["title"] = df["title"].apply(lambda x: x[:60] + "..." if len(x) > 60 else x)
titulo_seleccionado = st.selectbox(
    "Elige una película",
    options=df["title"].tolist()
)

#Agregar una descripción de la película seleccionada
pelicula_seleccionada = df[df["title"] == titulo_seleccionado].iloc[0]
st.subheader(f"{pelicula_seleccionada['overview']}")
# Mostrar el poster de la película seleccionada
st.image(obtener_poster(pelicula_seleccionada["poster_path"]), caption=titulo_seleccionado, width=300)
# Mostrar género de la película seleccionada
st.write(f"**Géneros:** {''.join(pelicula_seleccionada['genres'])}")
# Cluster de la película seleccionada
st.write(f"**Cluster:** {pelicula_seleccionada['cluster']}")

if st.button("Recomendar"):
    resultados = recomendar_clustered(titulo_seleccionado, df, similarity, kmeans_model)

    if resultados:
        st.subheader(f"🎯 Películas similares a: *{titulo_seleccionado}*")
        cols = st.columns(len(resultados))
        for i, pelicula in enumerate(resultados):
            with cols[i]:
                st.image(pelicula["poster"], caption=pelicula["title"], use_container_width=True)
                # Mostrar el género de la película recomendada
                genero = df[df["title"] == pelicula["title"]]["genres"].values[0]
                st.write(f"**Géneros:** {''.join(genero)}")
                # Mostrar la descripción de la película recomendada
                descripcion = df[df["title"] == pelicula["title"]]["overview"].values[0]
                st.write(f"**Descripción:** {descripcion[:150]}...")  # Mostrar solo los primeros 150 caracteres
                # Mostrar el cluster de la película recomendada
                cluster = df[df["title"] == pelicula["title"]]["cluster"].values[0]
                st.write(f"**Cluster:** {cluster}")
    else:
        st.error("❌ No se encontró la película en el dataset.")