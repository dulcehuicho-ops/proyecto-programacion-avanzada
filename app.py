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
no_dom = df_p["QRESIDUOS_NO_DOM"].sum()
total = dom + no_dom

st.header(f"Composición de los residuos municipales - {periodo}")

c1, c2, c3 = st.columns(3)
c1.metric("Total generado (t/año)", f"{total:,.0f}")
c2.metric("Domiciliarios (t/año)", f"{dom:,.0f}")
c3.metric("No domiciliarios (t/año)", f"{no_dom:,.0f}")

st.markdown("---")

col_graf, col_tabla = st.columns([1, 1])

with col_graf:
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

with col_tabla:
    st.subheader("Resumen nacional por año")
    resumen = (
        df.groupby(df["PERIODO"].astype(int))[["QRESIDUOS_DOM", "QRESIDUOS_NO_DOM"]]
        .sum()
        .rename(columns={
            "QRESIDUOS_DOM": "Domiciliarios (t)",
            "QRESIDUOS_NO_DOM": "No domiciliarios (t)"
        })
    )
    resumen["Total (t)"] = resumen.sum(axis=1)
    resumen.index.name = "Año"
    st.dataframe(resumen.style.format("{:,.0f}"), use_container_width=True)

st.markdown("---")
st.caption("Fuente: Base de datos de residuos municipales. Elaboración propia.")  