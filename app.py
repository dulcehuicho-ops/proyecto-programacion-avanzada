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
    df["PERIODO"] = df["PERIODO"].astype(int)
    # Corrección: en 2023 la columna QRESIDUOS_DOM viene multiplicada por 10
    df.loc[df["PERIODO"] == 2023, "QRESIDUOS_DOM"] /= 10
    return df


df = load_data()

st.sidebar.header("Filtros de búsqueda")
periodos = sorted(df["PERIODO"].unique())
seleccion = st.sidebar.multiselect(
    "Seleccione los años:",
    periodos,
    default=periodos
)

if not seleccion:
    st.warning("Seleccione al menos un año en la barra lateral.")
    st.stop()

resumen = (
    df[df["PERIODO"].isin(seleccion)]
    .groupby("PERIODO")[["QRESIDUOS_DOM", "QRESIDUOS_NO_DOM"]]
    .sum()
)
resumen["TOTAL"] = resumen["QRESIDUOS_DOM"] + resumen["QRESIDUOS_NO_DOM"]

total_acum = resumen["TOTAL"].sum()
anio_max = resumen["TOTAL"].idxmax()
anio_min = resumen["TOTAL"].idxmin()

st.subheader("Participación de cada año en el total de residuos municipales")

c1, c2, c3 = st.columns(3)
c1.metric("Total acumulado (t)", f"{total_acum:,.0f}")
c2.metric(f"Mayor generación: {anio_max}", f"{resumen.loc[anio_max, 'TOTAL']:,.0f} t")
c3.metric(f"Menor generación: {anio_min}", f"{resumen.loc[anio_min, 'TOTAL']:,.0f} t")

st.markdown("---")

col_izq, col_centro, col_der = st.columns([1, 2, 1])

with col_centro:
    fig, ax = plt.subplots(figsize=(7, 7))
    colores = plt.cm.Greens([0.35 + 0.6 * i / max(len(resumen) - 1, 1)
                             for i in range(len(resumen))])

    wedges, texts, autotexts = ax.pie(
        resumen["TOTAL"],
        labels=[str(a) for a in resumen.index],
        colors=colores,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.8,
        wedgeprops={"width": 0.45, "edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 11}
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")
        t.set_fontsize(9)

    ax.text(0, 0, f"{total_acum:,.0f}\ntoneladas", ha="center", va="center",
            fontsize=14, fontweight="bold", color="#333333")
    ax.set_title("Residuos municipales del Perú por año",
                 fontsize=15, fontweight="bold", pad=15)
    ax.axis("equal")

    st.pyplot(fig)
    plt.close(fig)

st.markdown("---")
st.caption("Fuente: Base de datos de residuos municipales. Elaboración propia.")