import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Residuos Municipales - Perú",
    layout="wide"
)

st.title("Residuos Municipales en el Perú")
st.markdown(
    "Aplicación interactiva desarrollada para el curso de "
    "Programación Avanzada - UPCH. Analiza la generación anual de "
    "residuos municipales a nivel nacional."
)

st.header("Análisis Estadístico a Nivel Nacional")
st.markdown("---")


def a_numero(serie):
    s = serie.astype(str).str.strip()
    con_ambos = s.str.contains(r"\.") & s.str.contains(",")
    s = s.where(~con_ambos, s.str.replace(".", "", regex=False))
    s = s.str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


@st.cache_data
def load_data():
    df = pd.read_csv(
        "1 DataSet Residuos municipales generados anualmente.csv",
        sep=";",
        encoding="latin1"
    )
    for col in ["QRESIDUOS_DOM", "QRESIDUOS_NO_DOM", "QRESIDUOS_MUN"]:
        df[col] = a_numero(df[col])
    df["PERIODO"] = pd.to_numeric(df["PERIODO"], errors="coerce")
    df = df.dropna(subset=["PERIODO"])
    # Corrección: en 2023 la columna QRESIDUOS_DOM viene multiplicada por 10
    df["QRESIDUOS_DOM"] = df["QRESIDUOS_MUN"] - df["QRESIDUOS_NO_DOM"]
    return df


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
no_dom = df_p["QRESIDUOS_NO_DOM"].sum()
total = dom + no_dom

st.subheader(f"Composición de los residuos municipales - {periodo}")

c1, c2, c3 = st.columns(3)
c1.metric("Total generado (t/año)", f"{total:,.0f}")
c2.metric("Domiciliarios (t/año)", f"{dom:,.0f}")
c3.metric("No domiciliarios (t/año)", f"{no_dom:,.0f}")

st.markdown("---")

col_izq, col_centro, col_der = st.columns([1, 2, 1])

with col_centro:
    fig, ax = plt.subplots(figsize=(6, 6))
    colores = ["#2E8B57", "#F4A261"]

    wedges, texts, autotexts = ax.pie(
        [dom, no_dom],
        labels=["Domiciliarios", "No domiciliarios"],
        colors=colores,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.8,
        wedgeprops={"width": 0.4, "edgecolor": "white", "linewidth": 3},
        textprops={"fontsize": 12}
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")

    ax.text(0, 0, f"{total:,.0f}\ntoneladas", ha="center", va="center",
            fontsize=14, fontweight="bold", color="#333333")
    ax.set_title(f"Residuos municipales del Perú ({periodo})",
                 fontsize=15, fontweight="bold", pad=15)
    ax.axis("equal")

    st.pyplot(fig)
    plt.close(fig)

st.markdown("---")
st.caption("Fuente: Base de datos de residuos municipales. Elaboración propia.")