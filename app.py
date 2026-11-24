import unicodedata

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Residuos Municipales - Perú",
    layout="wide"
)


# Estilo visual: ambiental institucional (sin modificar la lógica de la aplicación)
st.markdown("""
<style>
    :root {
        --verde-profundo: #174D36;
        --verde-principal: #2E8B57;
        --verde-suave: #E8F2EC;
        --fondo-suave: #F5F8F6;
        --texto-principal: #26352D;
        --texto-secundario: #68776E;
        --borde: #DCE7DF;
    }

    .stApp {
        background: var(--fondo-suave);
        color: var(--texto-principal);
    }

    .main .block-container {
        padding-top: 2.1rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    h1, h2, h3 {
        color: var(--verde-profundo) !important;
        letter-spacing: -0.025em;
    }

    h1 {
        font-weight: 750 !important;
        padding-bottom: 0.15rem;
    }

    h2, h3 {
        font-weight: 650 !important;
    }

    p, label, .stCaption {
        color: var(--texto-secundario);
    }

    /* Introducción */
    .intro-label {
        color: var(--verde-principal);
        font-size: 0.76rem;
        font-weight: 750;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }

    /* Panel lateral */
    [data-testid="stSidebar"] {
        background: #EDF4EF;
        border-right: 1px solid var(--borde);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.7rem;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--verde-profundo) !important;
        font-size: 1.03rem;
        letter-spacing: 0;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #52645A;
    }

    /* Pestañas */
    [data-testid="stTabs"] [role="tablist"] {
        gap: 0.35rem;
        border-bottom: 1px solid var(--borde);
    }

    [data-testid="stTabs"] button[role="tab"] {
        color: #53665A;
        font-weight: 600;
        border-radius: 9px 9px 0 0;
