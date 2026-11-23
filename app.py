import unicodedata

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st

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


def sin_tildes(texto):
    t = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in t if not unicodedata.combining(c)).strip().upper()


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

    df.loc[df["PERIODO"] == 2023, "QRESIDUOS_DOM"] /= 10

    df["DEPARTAMENTO"] = df["DEPARTAMENTO"].map(sin_tildes)
    return df


df = load_data()
departamentos = sorted(df["DEPARTAMENTO"].unique())

# =====================================================================
# BARRA LATERAL (mismo orden que las pestañas)
# =====================================================================
st.sidebar.header("Filtros de búsqueda")
periodos = sorted(df["PERIODO"].unique())
periodo = st.sidebar.selectbox(
    "Seleccione el periodo (Año):",
    periodos,
    index=len(periodos) - 1
)

# Datos del año elegido (se usan en la composición y en el ranking)
df_p = df[df["PERIODO"] == periodo]

ranking = (
    df_p.assign(TOTAL=df_p["QRESIDUOS_DOM"] + df_p["QRESIDUOS_NO_DOM"])
    .groupby("DEPARTAMENTO")["TOTAL"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
ranking["PUESTO"] = range(1, len(ranking) + 1)
ranking["PORCENTAJE"] = ranking["TOTAL"] / ranking["TOTAL"].sum() * 100
ranking["GRUPO"] = ranking["PUESTO"].apply(
    lambda p: "Top 10" if p <= 10 else "Otros departamentos"
)
ranking["ETIQUETA"] = ranking.apply(
    lambda r: f"{r['TOTAL']:,.0f} t ({r['PORCENTAJE']:.1f}%)", axis=1
)

st.sidebar.markdown("---")
st.sidebar.header("Ranking por departamento")

mostrar = st.sidebar.radio(
    "Departamentos a mostrar:",
    ["Top 5", "Todos", "Elegir departamentos"],
    index=0
)

elegidos_rank = []
if mostrar == "Elegir departamentos":
    elegidos_rank = st.sidebar.multiselect(
        "Elija los departamentos del ranking:",
        departamentos,
        default=sorted(ranking.head(10)["DEPARTAMENTO"].tolist()),
        key="deptos_ranking"
    )

st.sidebar.markdown("---")
st.sidebar.header("Evolución por departamento")

todos = st.sidebar.checkbox("Seleccionar todos los departamentos", value=True)
if todos:
    seleccion = departamentos
else:
    seleccion = st.sidebar.multiselect(
        "Elija los departamentos:",
        departamentos,
        default=["LIMA"] if "LIMA" in departamentos else departamentos[:1],
        key="deptos_evolucion"
    )

escala_log = st.sidebar.checkbox(
    "Escala logarítmica (para ver los departamentos pequeños)",
    value=True
)

# =====================================================================
# PESTAÑAS
# =====================================================================
tab_comp, tab_rank, tab_evo = st.tabs([
    "Composición por año",
    "Ranking de departamentos",
    "Evolución por departamento"
])

# ---------------- 1. Composición del año elegido ----------------
with tab_comp:
    dom = df_p["QRESIDUOS_DOM"].sum()
    no_dom = df_p["QRESIDUOS_NO_DOM"].sum()
    total = dom + no_dom

    pct_dom = dom / total * 100
    pct_no_dom = no_dom / total * 100

    st.subheader(f"Composición de los residuos municipales - {periodo}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total generado (t/año)", f"{total:,.0f}",
              delta="100% del total", delta_color="off")
    c2.metric("Domiciliarios (t/año)", f"{dom:,.0f}",
              delta=f"{pct_dom:.1f}% del total", delta_color="off")
    c3.metric("No domiciliarios (t/año)", f"{no_dom:,.0f}",
              delta=f"{pct_no_dom:.1f}% del total", delta_color="off")

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

#