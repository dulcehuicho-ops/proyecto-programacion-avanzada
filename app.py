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
# INICIO DEL CÓDIGO PARA EL GRÁFICO DE DISPERSIÓN (BARRA LATERAL)
# =====================================================================
st.sidebar.markdown("---")
st.sidebar.header("Dispersión por distrito")

depto_disp = st.sidebar.selectbox(
    "Departamento para dispersión distrital:",
    departamentos,
    index=departamentos.index("LIMA") if "LIMA" in departamentos else 0,
    key="depto_dispersion"
)

variable_y_disp = st.sidebar.selectbox(
    "Variable en el eje Y (residuos):",
    ["Total (Domiciliarios + No domiciliarios)", "Domiciliarios", "No domiciliarios"],
    index=0,
    key="var_y_dispersion"
)
# =====================================================================
# FIN DEL CÓDIGO PARA EL GRÁFICO DE DISPERSIÓN (BARRA LATERAL)
# =====================================================================

# =====================================================================
# PESTAÑAS
# =====================================================================
tab_comp, tab_rank, tab_evo, tab_disp = st.tabs([
    "Composición por año",
    "Ranking de departamentos",
    "Evolución por departamento",
    "Dispersión por distrito"
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

# ---------------- 2. Ranking por departamento ----------------
with tab_rank:
    st.subheader(f"Departamentos con más residuos municipales - {periodo}")

    if mostrar == "Todos":
        datos_rank = ranking
    elif mostrar == "Elegir departamentos":
        datos_rank = ranking[ranking["DEPARTAMENTO"].isin(elegidos_rank)]
    else:
        datos_rank = ranking.head(int(mostrar.split()[1]))

    if datos_rank.empty:
        st.info("Elija al menos un departamento en la barra lateral.")
    else:
        st.caption(
            f"Los {len(datos_rank)} departamentos mostrados concentran "
            f"{datos_rank['PORCENTAJE'].sum():.1f}% del total nacional."
        )

        fig_rank = px.bar(
            datos_rank,
            x="TOTAL",
            y="DEPARTAMENTO",
            orientation="h",
            color="GRUPO",
            text="ETIQUETA",
            color_discrete_map={"Top 10": "#2E8B57",
                                "Otros departamentos": "#A8D5BA"},
            category_orders={
                "DEPARTAMENTO": datos_rank["DEPARTAMENTO"].tolist()
            },
            hover_data={"GRUPO": False, "ETIQUETA": False, "TOTAL": ":,.0f",
                        "PUESTO": True},
            labels={"TOTAL": "Residuos (toneladas)", "DEPARTAMENTO": "",
                    "GRUPO": "", "PUESTO": "Puesto"}
        )
        fig_rank.update_traces(textposition="outside", cliponaxis=False)
        fig_rank.update_xaxes(tickformat=",",
                              range=[0, datos_rank["TOTAL"].max() * 1.3])
        fig_rank.update_layout(
            template="plotly_white",
            height=max(350, 30 * len(datos_rank) + 120),
            showlegend=datos_rank["GRUPO"].nunique() > 1,
            legend_title_text=""
        )

        st.plotly_chart(fig_rank, use_container_width=True)

# ---------------- 3. Evolución por departamento ----------------
with tab_evo:
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

# =====================================================================
# INICIO DEL CÓDIGO PARA EL GRÁFICO DE DISPERSIÓN (PESTAÑA)
# =====================================================================
with tab_disp:
    st.subheader(f"Gráfico de dispersión por distrito ({depto_disp}) - {periodo}")

    df_disp = df_p[df_p["DEPARTAMENTO"] == depto_disp].copy()
    df_disp["POB_TOTAL_NUM"] = a_numero(df_disp["POB_TOTAL"])
    df_disp["TOTAL_DIST"] = df_disp["QRESIDUOS_DOM"] + df_disp["QRESIDUOS_NO_DOM"]

    if variable_y_disp == "Domiciliarios":
        col_y = "QRESIDUOS_DOM"
        etiqueta_y = "Residuos domiciliarios (toneladas)"
    elif variable_y_disp == "No domiciliarios":
        col_y = "QRESIDUOS_NO_DOM"
        etiqueta_y = "Residuos no domiciliarios (toneladas)"
    else:
        col_y = "TOTAL_DIST"
        etiqueta_y = "Residuos totales (toneladas)"

    df_disp = df_disp.dropna(subset=["POB_TOTAL_NUM", col_y])

    if df_disp.empty:
        st.info("No hay datos distritales disponibles para el filtro seleccionado.")
    else:
        fig_disp = px.scatter(
            df_disp,
            x="POB_TOTAL_NUM",
            y=col_y,
            color="PROVINCIA" if "PROVINCIA" in df_disp.columns else None,
            hover_name="DISTRITO" if "DISTRITO" in df_disp.columns else None,
            hover_data={
                "POB_TOTAL_NUM": ":,.0f",
                col_y: ":,.1f",
                "QRESIDUOS_DOM": ":,.1f",
                "QRESIDUOS_NO_DOM": ":,.1f",
                "TOTAL_DIST": ":,.1f"
            },
            labels={
                "POB_TOTAL_NUM": "Población total (habitantes)",
                col_y: etiqueta_y,
                "PROVINCIA": "Provincia",
                "QRESIDUOS_DOM": "Domiciliarios (t)",
                "QRESIDUOS_NO_DOM": "No domiciliarios (t)",
                "TOTAL_DIST": "Total residuos (t)"
            },
            title=f"Relación entre población y residuos por distrito ({depto_disp}, {periodo})"
        )
        fig_disp.update_traces(marker=dict(size=9, opacity=0.8, line=dict(width=1, color="white")))
        fig_disp.update_xaxes(tickformat=",", hoverformat=",.0f")
        fig_disp.update_yaxes(tickformat=",", hoverformat=",.1f")
        fig_disp.update_layout(
            template="plotly_white",
            height=550
        )

        st.plotly_chart(fig_disp, use_container_width=True)
# =====================================================================
# FIN DEL CÓDIGO PARA EL GRÁFICO DE DISPERSIÓN (PESTAÑA)
# =====================================================================

st.markdown("---")
st.caption("Fuente: Base de datos de residuos municipales. Elaboración propia.")