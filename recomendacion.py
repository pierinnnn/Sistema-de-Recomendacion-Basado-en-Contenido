import streamlit as st
import pickle
import pandas as pd
import numpy as np
import gdown
import os

st.set_page_config('Encuentra tu Pelicula!', layout='wide')

similarity_path = "modelo/similarity.pkl"
similarity_id = "14Bvn23VAIY5hYvBiMBlvMbW6aXCvnulg"

if not os.path.exists(similarity_path):
    url = f"https://drive.google.com/uc?id={similarity_id}"
    os.makedirs("modelo", exist_ok=True)
    gdown.download(url, similarity_path, quiet=False)

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

if st.button("Recomendar"):
    resultados = recomendar_clustered(titulo_seleccionado, df, similarity, kmeans_model)

    if resultados:
        st.subheader(f"🎯 Películas similares a: *{titulo_seleccionado}*")
        cols = st.columns(len(resultados))
        for i, pelicula in enumerate(resultados):
            with cols[i]:
                st.image(pelicula["poster"], caption=pelicula["title"], use_container_width=True)
    else:
        st.error("❌ No se encontró la película en el dataset.")