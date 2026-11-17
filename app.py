RESIDUOS MUNICIPALES GENERADOS EN EL PERÚ

import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Residuos Municipales del Perú",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

ARCHIVO = (
    Path(__file__).parent
    / "1 DataSet Residuos municipales generados anualmente.csv"
)

st.markdown("""
<style>
    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #176B45;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 16px;
        color: #64748b;
        margin-bottom: 20px;
    }

    [data-testid="stMetric"] {
        background-color: #F0F7F3;
        border: 1px solid #D5E8DB;
        padding: 16px;
        border-radius: 12px;
    }

    [data-testid="stSidebar"] {
        background-color: #F4F8F5;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">'
    '♻️ DASHBOARD DE RESIDUOS MUNICIPALES GENERADOS EN EL PERÚ'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Análisis de la generación de residuos sólidos municipales '
    'a nivel nacional, departamental, provincial y distrital.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


@st.cache_data(show_spinner="Cargando base de datos...")
def load_data():

    if not ARCHIVO.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo {ARCHIVO.name}"
        )

    df = pd.read_csv(
        ARCHIVO,
        sep=";",
        encoding="latin1"
    )

    df.columns = df.columns.str.strip()

    columnas = [
        "FECHA_CORTE",
        "N_SEC",
        "UBIGEO",
        "REG_NAT",
        "DEPARTAMENTO",
        "PROVINCIA",
        "DISTRITO",
        "POB_TOTAL",
        "POB_URBANA",
        "POB_RURAL",
        "GPC_DOM",
        "QRESIDUOS_DOM",
        "QRESIDUOS_NO_DOM",
        "QRESIDUOS_MUN",
        "PERIODO"
    ]

    faltantes = [
        columna for columna in columnas
        if columna not in df.columns
    ]

    if faltantes:
        raise ValueError(
            "Faltan columnas en el archivo: "
            + ", ".join(faltantes)
        )

    df = df[columnas].copy()

    columnas_texto = [
        "REG_NAT",
        "DEPARTAMENTO",
        "PROVINCIA",
        "DISTRITO"
    ]

    for columna in columnas_texto:
        df[columna] = (
            df[columna]
            .astype("string")
            .str.strip()
        )

    columnas_numericas = [
        "FECHA_CORTE",
        "N_SEC",
        "POB_TOTAL",
        "POB_URBANA",
        "POB_RURAL",
        "GPC_DOM",
        "QRESIDUOS_DOM",
        "QRESIDUOS_NO_DOM",
        "QRESIDUOS_MUN",
        "PERIODO"
    ]

    for columna in columnas_numericas:
        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        )

    df = df.dropna(
        subset=[
            "PERIODO",
            "DEPARTAMENTO",
            "PROVINCIA",
            "DISTRITO",
            "POB_TOTAL",
            "QRESIDUOS_MUN"
        ]
    )

    for columna in columnas_texto:
        df = df[
            df[columna].notna()
            & (df[columna] != "")
        ]

    df["PERIODO"] = df["PERIODO"].astype(int)

    df["UBIGEO"] = (
        df["UBIGEO"]
        .astype("Int64")
        .astype("string")
        .str.zfill(6)
    )

    return df


try:
    df = load_data()

except Exception as error:
    st.error(f"Error al cargar la base de datos: {error}")
    st.info(
        "Verifica que el archivo CSV esté en la misma carpeta "
        "que el archivo app.py."
    )
    st.stop()

if df.empty:
    st.warning("La base de datos no contiene registros.")
    st.stop()


st.sidebar.title("🔎 Panel de búsqueda")

st.sidebar.markdown(
    "Selecciona los criterios para explorar la información."
)

periodos = sorted(df["PERIODO"].unique())

periodo_seleccionado = st.sidebar.selectbox(
    "📅 Seleccione el año:",
    periodos,
    index=len(periodos) - 1
)

df_periodo = df[
    df["PERIODO"] == periodo_seleccionado
].copy()

departamentos = sorted(
    df_periodo["DEPARTAMENTO"].unique()
)

dep_seleccionado = st.sidebar.selectbox(
    "🗺️ Seleccione el departamento:",
    departamentos
)

df_dep = df_periodo[
    df_periodo["DEPARTAMENTO"] == dep_seleccionado
].copy()

provincias = sorted(
    df_dep["PROVINCIA"].unique()
)

prov_seleccionada = st.sidebar.selectbox(
    "📍 Seleccione la provincia:",
    provincias
)

df_prov = df_dep[
    df_dep["PROVINCIA"] == prov_seleccionada
].copy()

st.sidebar.divider()

st.sidebar.caption(
    "Desarrollado con Python, Pandas y Streamlit."
)


st.header("📌 Indicadores principales")

total_residuos = df_periodo["QRESIDUOS_MUN"].sum()
total_domiciliarios = df_periodo["QRESIDUOS_DOM"].sum()
total_no_domiciliarios = df_periodo["QRESIDUOS_NO_DOM"].sum()
total_poblacion = df_periodo["POB_TOTAL"].sum()

total_departamentos = df_periodo["DEPARTAMENTO"].nunique()
total_distritos = df_periodo["UBIGEO"].nunique()

gpc_promedio = df_periodo["GPC_DOM"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Residuos municipales", f"{total_residuos:,.2f}")
col2.metric("Residuos domiciliarios", f"{total_domiciliarios:,.2f}")
col3.metric("Residuos no domiciliarios", f"{total_no_domiciliarios:,.2f}")
col4.metric("Población registrada", f"{total_poblacion:,.0f}")

col5, col6, col7 = st.columns(3)

col5.metric("Departamentos", f"{total_departamentos}")
col6.metric("Distritos registrados", f"{total_distritos:,}")
col7.metric("GPC domiciliaria promedio", f"{gpc_promedio:.2f}")

st.caption(
    f"Información correspondiente al año {periodo_seleccionado}. "
    "La GPC corresponde al promedio simple de los registros "
    "distritales del periodo."
)

st.divider()


st.header("🇵🇪 Análisis de residuos municipales a nivel nacional")

st.markdown(
    "Evolución histórica de la generación de residuos "
    "municipales en el Perú."
)

df_nacional = (
    df.groupby("PERIODO")["QRESIDUOS_MUN"]
    .sum()
    .reset_index()
    .sort_values("PERIODO")
)

st.subheader("Evolución anual de residuos municipales")

st.line_chart(
    df_nacional.set_index("PERIODO"),
    y="QRESIDUOS_MUN",
    x_label="Año",
    y_label="Cantidad de residuos municipales"
)

st.subheader("Composición de los residuos municipales")

df_composicion = (
    df_periodo[
        ["QRESIDUOS_DOM", "QRESIDUOS_NO_DOM"]
    ]
    .sum()
    .rename({
        "QRESIDUOS_DOM": "Domiciliarios",
        "QRESIDUOS_NO_DOM": "No domiciliarios"
    })
)

st.bar_chart(
    df_composicion,
    horizontal=True
)

st.divider()


st.header("🗺️ Análisis por departamento")

st.markdown(
    f"Departamento seleccionado: **{dep_seleccionado}**"
)

df_prov_resumen = (
    df_dep.groupby("PROVINCIA")["QRESIDUOS_MUN"]
    .sum()
    .reset_index()
    .sort_values("QRESIDUOS_MUN", ascending=False)
)

st.subheader(
    f"Generación de residuos por provincia ({periodo_seleccionado})"
)

st.bar_chart(
    df_prov_resumen.set_index("PROVINCIA"),
    x_label="Provincia",
    y_label="Cantidad de residuos municipales"
)

if not df_prov_resumen.empty:
    mayor_provincia = df_prov_resumen.iloc[0]

    st.info(
        f"La provincia con mayor generación registrada es "
        f"**{mayor_provincia['PROVINCIA']}**, con "
        f"**{mayor_provincia['QRESIDUOS_MUN']:,.2f}**."
    )

st.divider()


st.header("📍 Análisis por provincia y distrito")

st.markdown(
    f"Provincia seleccionada: **{prov_seleccionada}**"
)

df_dist_resumen = (
    df_prov.groupby("DISTRITO")["QRESIDUOS_MUN"]
    .sum()
    .reset_index()
    .sort_values("QRESIDUOS_MUN", ascending=False)
)

st.subheader(
    f"Generación de residuos por distrito ({periodo_seleccionado})"
)

df_top_distritos = df_dist_resumen.head(15)

st.bar_chart(
    df_top_distritos.set_index("DISTRITO"),
    x_label="Distrito",
    y_label="Cantidad de residuos municipales"
)

if not df_dist_resumen.empty:
    mayor_distrito = df_dist_resumen.iloc[0]

    st.info(
        f"El distrito con mayor generación registrada es "
        f"**{mayor_distrito['DISTRITO']}**, con "
        f"**{mayor_distrito['QRESIDUOS_MUN']:,.2f}**."
    )

st.divider()


st.header("👥 Análisis poblacional")

st.markdown(
    "Distribución de la población urbana y rural "
    "en el departamento seleccionado."
)

df_poblacion = (
    df_dep[
        ["POB_URBANA", "POB_RURAL"]
    ]
    .sum()
    .rename({
        "POB_URBANA": "Población urbana",
        "POB_RURAL": "Población rural"
    })
)

st.bar_chart(
    df_poblacion,
    horizontal=True
)

st.divider()


st.header("🌎 Análisis por región natural")

st.markdown(
    "Comparación de la generación de residuos municipales "
    "según la región natural."
)

df_region = (
    df_periodo.groupby("REG_NAT")["QRESIDUOS_MUN"]
    .sum()
    .reset_index()
    .sort_values("QRESIDUOS_MUN", ascending=False)
)

st.bar_chart(
    df_region.set_index("REG_NAT"),
    x_label="Región natural",
    y_label="Cantidad de residuos municipales"
)

st.divider()


st.header("📋 Tabla detallada de datos")

st.markdown(
    "Consulta los registros correspondientes a los filtros "
    "seleccionados."
)

columnas_tabla = [
    "FECHA_CORTE",
    "UBIGEO",
    "REG_NAT",
    "DEPARTAMENTO",
    "PROVINCIA",
    "DISTRITO",
    "POB_TOTAL",
    "POB_URBANA",
    "POB_RURAL",
    "GPC_DOM",
    "QRESIDUOS_DOM",
    "QRESIDUOS_NO_DOM",
    "QRESIDUOS_MUN",
    "PERIODO"
]

df_tabla = df_prov[columnas_tabla].copy()

with st.expander(
    "📂 Ver tabla de datos detallada",
    expanded=True
):

    st.dataframe(
        df_tabla,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"Total de registros encontrados: {len(df_tabla)}"
    )

    archivo_csv = df_tabla.to_csv(
        index=False,
        sep=";"
    ).encode("utf-8-sig")

    st.download_button(
        label="⬇️ Descargar datos filtrados",
        data=archivo_csv,
        file_name=(
            f"residuos_{periodo_seleccionado}_"
            f"{dep_seleccionado}_"
            f"{prov_seleccionada}.csv"
        ),
        mime="text/csv"
    )


st.header("📊 Información de la base de datos")

col1, col2, col3 = st.columns(3)

col1.metric("Total de registros", f"{len(df):,}")
col2.metric("Año inicial", f"{df['PERIODO'].min()}")
col3.metric("Año final", f"{df['PERIODO'].max()}")


st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#64748b; padding:15px;">

        <h4 style="color:#176B45;">
            ♻️ Dashboard de Residuos Municipales del Perú
        </h4>

        Aplicación desarrollada con Python, Pandas y Streamlit.

        <br>

        Curso de Programación Avanzada - UPCH

        <br><br>

        Análisis de datos ambientales y generación de residuos municipales.

    </div>
    """,
    unsafe_allow_html=True
)
