import streamlit as st
import pickle
import pandas as pd
import numpy as np

st.set_page_config('Encuentra tu Pelicula!', layout='wide')

@st.cache_data
def cargar_datos():
    df = pickle.load(open("modelo/movie_list.pkl", "rb"))
    similarity = pickle.load(open("modelo/similarity.pkl", "rb"))
    return df, similarity

df, similarity = cargar_datos()

url_base_poster = "https://image.tmdb.org/t/p/w500"

def obtener_poster(poster_path):
    if pd.isna(poster_path):
        return "https://via.placeholder.com/500x750?text=No+Image"
    return url_base_poster + poster_path

def recomendar(titulo, df, similarity, top_k=5):
    indices = df[df['title'].str.lower() == titulo.lower()].index

    if len(indices) == 0:
        return None

    idx = indices[0]
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_k+1]  # ignorar la peli original

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
df = df.drop_duplicates(subset="title")
df["title"] = df["title"].apply(lambda x: x[:60] + "..." if len(x) > 60 else x)
titulo_seleccionado = st.selectbox(
    "Elige una película",
    options=df["title"].tolist()
)

if st.button("Recomendar"):
    resultados = recomendar(titulo_seleccionado, df, similarity)

    if resultados:
        st.subheader(f"🎯 Películas similares a: *{titulo_seleccionado}*")
        cols = st.columns(len(resultados))
        for i, pelicula in enumerate(resultados):
            with cols[i]:
                st.image(pelicula["poster"], caption=pelicula["title"], use_container_width=True)
    else:
        st.error("❌ No se encontró la película en el dataset.")