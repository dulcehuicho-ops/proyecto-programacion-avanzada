import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Dashboard de Residuos Municipales - Perú",
    layout="wide"
)

st.title("Dashboard de Residuos Municipales en el Perú")
st.markdown(
    "Aplicación interactiva desarrollada para el curso de "
    "Programación Avanzada - UPCH. Analiza la generación anual de "
    "residuos municipales a nivel nacional."
)
st.markdown("---")


@st.cache_data
def load_data():
    df = pd.read_csv(
        "1 DataSet Residuos municipales generados anualmente.csv",
        sep=";",
        encoding="latin1"
    )
    for col in ["QRESIDUOS_DOM", "QRESIDUOS_NO_DOM", "QRESIDUOS_MUN"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.strip().str.replace(",", ".", regex=False),
            errors="coerce"
        )
    df["PERIODO"] = pd.to_numeric(df["PERIODO"], errors="coerce")
    return df.dropna(subset=["PERIODO"])


df = load_data()

st.sidebar.header("Filtros de búsqueda")
periodos = sorted(df["PERIODO"].astype(int).unique())
periodo = st.sidebar.selectbox(
    "Seleccione el periodo (Año):",
    periodos,
    index=len(periodos) - 1
)

df_p = df[df["PERIODO"] == periodo]

dom = df_p["QRESIDUOS_DOM"].sum()
no_dom =