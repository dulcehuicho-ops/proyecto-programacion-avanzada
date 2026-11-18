import math
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

resumen = df.groupby("PERIODO")[["QRESIDUOS_DOM", "QRESIDUOS_NO_DOM"]].sum()
resumen["TOTAL"] = resumen["QRESIDUOS_DOM"] + resumen["QRESIDUOS_NO_DOM"]

st.subheader("Composición de los residuos municipales por año")

n = len(resumen)
columnas = 4
filas = math.ceil(n / columnas)
colores = ["#2E8B57", "#F4A261"]

fig, axes = plt.subplots(filas, columnas, figsize=(16, 4.8 * filas))
axes = axes.flatten()

for ax, (anio, fila) in zip(axes, resumen.iterrows()):
    wedges, texts, autotexts = ax.pie(
        [fila["QRESIDUOS_DOM"], fila["QRESIDUOS_NO_DOM"]],
        colors=colores,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.8,
        wedgeprops={"width": 0.4, "edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 11}
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")

    ax.text(0, 0, f"Total\n{fila['TOTAL']:,.0f} t", ha="center", va="center",
            fontsize=10, fontweight="bold", color="#333333")
    ax.set_title(str(anio), fontsize=14, fontweight="bold", pad=8)
    ax.set_xlabel(
        f"Domiciliarios: {fila['QRESIDUOS_DOM']:,.0f} t\n"
        f"No domiciliarios: {fila['QRESIDUOS_NO_DOM']:,.0f} t",
        fontsize=10
    )
    ax.axis("equal")

for ax in axes[n:]:
    ax.axis("off")

fig.legend(
    wedges,
    ["Domiciliarios", "No domiciliarios"],
    loc="lower center",
    ncol=2,
    fontsize=12,
    frameon=False
)
fig.tight_layout(rect=[0, 0.04, 1, 1])

st.pyplot(fig, use_container_width=True)
plt.close(fig)

st.markdown("---")
st.caption("Fuente: Base de datos de residuos municipales. Elaboración propia.")