import math
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

# ---------------- Barra lateral ----------------
st.sidebar.header("Filtros de búsqueda")
periodos = sorted(df["PERIODO"].unique())
periodo = st.sidebar.selectbox(
    "Seleccione el periodo (Año):",
    periodos,
    index=len(periodos) - 1
)

st.sidebar.markdown("---")
st.sidebar.header("Evolución por departamento")

departamentos = sorted(df["DEPARTAMENTO"].unique())

todos = st.sidebar.checkbox("Seleccionar todos los departamentos", value=True)
if todos:
    seleccion = departamentos
else:
    seleccion = st.sidebar.multiselect(
        "Elija los departamentos:",
        departamentos,
        default=["LIMA"] if "LIMA" in departamentos else departamentos[:1]
    )

vista = st.sidebar.radio(
    "Tipo de vista:",
    ["Un gráfico por departamento", "Todos en un solo gráfico"]
)

escala_log = True
if vista == "Todos en un solo gráfico":
    escala_log = st.sidebar.checkbox(
        "Escala logarítmica (para ver los departamentos pequeños)",
        value=True
    )

# ---------------- Composición del año elegido ----------------
df_p = df[df["PERIODO"] == periodo]

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

# ---------------- Evolución por departamento ----------------
st.markdown("---")
st.subheader("Evolución histórica por departamento")

if not seleccion:
    st.info("Seleccione al menos un departamento en la barra lateral.")
else:
    df_dep = df.assign(TOTAL=df["QRESIDUOS_DOM"] + df["QRESIDUOS_NO_DOM"])
    evolucion = (
        df_dep[df_dep["DEPARTAMENTO"].isin(seleccion)]
        .groupby(["PERIODO", "DEPARTAMENTO"])["TOTAL"]
        .sum()
        .reset_index()
    )
    etiquetas = {
        "PERIODO": "Año",
        "TOTAL": "Residuos (toneladas)",
        "DEPARTAMENTO": "Departamento"
    }

    # Indicadores cuando se elige un solo departamento
    if len(seleccion) == 1:
        serie = evolucion.sort_values("PERIODO")
        primero, ultimo = serie.iloc[0], serie.iloc[-1]
        variacion = (ultimo["TOTAL"] / primero["TOTAL"] - 1) * 100

        k1, k2, k3 = st.columns(3)
        k1.metric(f"Residuos {int(primero['PERIODO'])} (t)",
                  f"{primero['TOTAL']:,.0f}")
        k2.metric(f"Residuos {int(ultimo['PERIODO'])} (t)",
                  f"{ultimo['TOTAL']:,.0f}")
        k3.metric("Variación en el periodo", f"{variacion:+.1f}%")

    if vista == "Un gráfico por departamento":
        filas = math.ceil(len(seleccion) / 5)
        fig_ev = px.line(
            evolucion,
            x="PERIODO",
            y="TOTAL",
            facet_col="DEPARTAMENTO",
            facet_col_wrap=5,
            markers=True,
            labels=etiquetas,
            color_discrete_sequence=["#2E8B57"],
            category_orders={"DEPARTAMENTO": sorted(seleccion)}
        )
        fig_ev.update_traces(line=dict(width=2.5), marker=dict(size=5))
        fig_ev.update_xaxes(showticklabels=True, dtick=5, title=None)
        fig_ev.update_yaxes(matches=None, showticklabels=True, tickformat="~s",
                            hoverformat=",.0f", title=None)
        fig_ev.for_each_annotation(
            lambda a: a.update(text=a.text.split("=")[-1])
        )
        fig_ev.update_layout(
            template="plotly_white",
            height=230 * filas + 80,
            showlegend=False
        )
    else:
        fig_ev = px.line(
            evolucion,
            x="PERIODO",
            y="TOTAL",
            color="DEPARTAMENTO",
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Alphabet,
            labels=etiquetas
        )
        fig_ev.update_traces(line=dict(width=2), marker=dict(size=6))
        fig_ev.update_xaxes(dtick=1)
        if escala_log:
            fig_ev.update_yaxes(
                type="log",
                tickvals=[20000, 50000, 100000, 200000, 500000,
                          1000000, 2000000, 5000000],
                tickformat=",",
                hoverformat=",.0f"
            )
        else:
            fig_ev.update_yaxes(tickformat=",", hoverformat=",.0f",
                                rangemode="tozero")
        fig_ev.update_layout(
            template="plotly_white",
            hovermode="x unified" if len(seleccion) <= 6 else "closest",
            legend_title_text="Departamento",
            height=600
        )

    st.plotly_chart(fig_ev, use_container_width=True)

st.markdown("---")
st.caption("Fuente: Base de datos de residuos municipales. Elaboración propia.")