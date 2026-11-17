import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Dashboard de Residuos Municipales - Perú",
    page_icon="♻️",
    layout="wide"
)

st.title("📊 Dashboard de Residuos Municipales generados anualmente en el Perú")

st.markdown(
    "Aplicación interactiva desarrollada para el curso de "
    "Programación Avanzada - UPCH."
)

st.markdown(
    "El presente proyecto tiene como finalidad analizar la "
    "generación de residuos municipales en el Perú, mediante "
    "la visualización de datos estadísticos a nivel nacional."
)

st.markdown("---")

@st.cache_data
def load_data():
    df = pd.read_csv(
        "1 DataSet Residuos municipales generados anualmente.csv",
        sep=";",
        encoding="latin1"
    )
    return df

df = load_data()

st.sidebar.header("Filtros de búsqueda")

periodos = sorted(df["PERIODO"].dropna().unique())

periodo_seleccionado = st.sidebar.selectbox(
    "Seleccione el periodo (Año):",
    periodos,
    index=len(periodos) - 1
)

df_periodo = df[
    df["PERIODO"] == periodo_seleccionado
]

st.header("♻️ Composición de los residuos municipales")

st.subheader(
    f"Distribución de residuos municipales en el Perú ({periodo_seleccionado})"
)

residuos_domiciliarios = df_periodo["QRESIDUOS_DOM"].sum()

residuos_no_domiciliarios = df_periodo["QRESIDUOS_NO_DOM"].sum()

valores = [
    residuos_domiciliarios,
    residuos_no_domiciliarios
]

etiquetas = [
    "Residuos domiciliarios",
    "Residuos no domiciliarios"
]

fig, ax = plt.subplots(figsize=(8, 5))

ax.pie(
    valores,
    labels=etiquetas,
    autopct="%1.1f%%",
    startangle=90,
    shadow=False,
    explode=(0.03, 0),
    wedgeprops={
        "edgecolor": "white",
        "linewidth": 2
    }
)

ax.set_title(
    "Composición de los residuos municipales",
    fontsize=14,
    fontweight="bold"
)

ax.axis("equal")

st.pyplot(fig)

plt.close(fig)

st.markdown("---")

st.caption(
    "Fuente: Base de datos de residuos municipales. "
    "Elaboración propia."
)