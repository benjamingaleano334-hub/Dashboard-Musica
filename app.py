import html

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Un siglo de música en Spotify",
    page_icon="🎧",
    layout="wide",
)

# ---------- Estilo ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=Manrope:wght@400;500;600&display=swap');

    .stApp {
        background-color: #0B1426;
        color: #E6EEFF;
        font-family: 'Manrope', sans-serif;
    }
    [data-testid="stSidebar"] { background-color: #121E38; }
    [data-testid="stHeader"] { background: transparent; }

    .stApp h1, .stApp h2, .stApp h3,
    [data-testid="stMetricValue"] { font-family: 'Chakra Petch', sans-serif; }

    .block-container { padding-top: 2rem; max-width: 1280px; }

    [data-testid="stMetric"] {
        background: #121E38;
        border: 1px solid #23365E;
        border-radius: 14px;
        padding: 16px 20px;
    }
    [data-testid="stMetricLabel"] { color: #8FA3C8; }
    [data-testid="stMetricValue"] { font-size: 2rem; }

    .stTabs [data-baseweb="tab"] { font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #22D3EE; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #22D3EE; }

    .hallazgo {
        background: #121E38;
        border-left: 3px solid #22D3EE;
        border-radius: 0 10px 10px 0;
        padding: 14px 18px;
        margin: 8px 0 20px 0;
        line-height: 1.6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Datos ----------
@st.cache_data
def cargar_datos():
    return pd.read_csv("data/spotify_limpio.csv")


df_total = cargar_datos()


# ---------- Funciones de apoyo ----------
def formato(n):
    """Número entero con punto de miles: 137376 -> 137.376"""
    return f"{n:,}".replace(",", ".")


def dec(x, cifras=2):
    """Número con coma decimal: 0.5 -> 0,50"""
    return f"{x:.{cifras}f}".replace(".", ",")


def hallazgo(texto):
    """Recuadro con lo que muestran los datos en cada sección."""
    st.markdown(
        f'<div class="hallazgo">{html.escape(texto)}</div>',
        unsafe_allow_html=True,
    )


# Del cian (décadas viejas) al magenta (décadas recientes)
ESPECTRO = [
    "#22D3EE", "#3DC5F0", "#57B6F3", "#72A8F5", "#8C99F8", "#A78BFA",
    "#B686EC", "#C681DF", "#D57CD1", "#E577C4", "#F472B6",
]


def color_de(decada):
    return ESPECTRO[(decada - 1920) // 10]


def estilo(fig, altura=380):
    fig.update_layout(
        template="plotly_dark",
        height=altura,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Manrope, sans-serif", color="#E6EEFF"),
        title_font=dict(family="Chakra Petch, sans-serif", size=18),
        margin=dict(l=10, r=10, t=50, b=10),
        showlegend=False,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#23365E", zeroline=False)
    return fig


CARACTERISTICAS = {
    "Energía": "energy",
    "Acústica": "acousticness",
    "Bailabilidad": "danceability",
    "Positividad": "valence",
    "Volumen (dB)": "loudness",
    "Tempo (BPM)": "tempo",
    "Duración (minutos)": "duracion_min",
}
NOMBRES = {columna: nombre for nombre, columna in CARACTERISTICAS.items()}

# ---------- Barra lateral ----------
st.sidebar.header("Filtros")

anio_min = int(df_total["year"].min())
anio_max = int(df_total["year"].max())

desde, hasta = st.sidebar.slider(
    "Rango de años",
    min_value=anio_min,
    max_value=anio_max,
    value=(1950, 2019),
)

st.sidebar.caption(
    "El año 2020 está incompleto y los años 20 y 30 tienen pocas canciones. "
    "Por eso el rango empieza en 1950 y termina en 2019."
)

df = df_total[df_total["year"].between(desde, hasta)]

if df.empty:
    st.warning("No hay canciones en ese rango de años. Probá con otro.")
    st.stop()

con_pop = df[~df["pop_cero"]]

# ---------- Encabezado ----------
st.title("Un siglo de música en Spotify")
st.write(
    "¿Cómo cambió el sonido de las canciones a lo largo de las décadas "
    "y qué hace que una sea más popular que otra? Cada pestaña parte de una "
    "pregunta y termina con lo que muestran los datos."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Canciones", formato(len(df)))
c2.metric("Artistas", formato(df["artista_principal"].nunique()))
c3.metric("Años", f"{desde} a {hasta}")
c4.metric("Popularidad mediana", f"{con_pop['popularity'].median():.0f}")

# ---------- Secciones ----------
tab_evolucion, tab_popularidad, tab_generos, tab_artistas = st.tabs(
    ["Evolución", "Popularidad", "Géneros", "Artistas"]
)

# ======================================================================
# 1. EVOLUCIÓN
# ======================================================================
with tab_evolucion:
    st.subheader("¿Cómo cambió el sonido de las canciones?")

    PRINCIPALES = {
        "Energía": "#22D3EE",
        "Acústica": "#A78BFA",
        "Bailabilidad": "#FBBF24",
        "Positividad": "#34D399",
    }

    medianas = (
        df.groupby("decada")[[CARACTERISTICAS[n] for n in PRINCIPALES]]
        .median()
        .rename(columns=NOMBRES)
    )

    fig = px.line(
        medianas,
        markers=True,
        color_discrete_map=PRINCIPALES,
        title="Cuatro características del sonido, por década",
    )
    fig = estilo(fig, 400)
    fig.update_layout(
        showlegend=True,
        legend_title_text="",
        legend=dict(orientation="h", y=-0.12),
        margin=dict(l=10, r=10, t=50, b=50),
    )
    fig.update_xaxes(title=None, dtick=10)
    fig.update_yaxes(title=None)
    st.plotly_chart(fig, theme=None)

    primera, ultima = medianas.index.min(), medianas.index.max()
    if primera != ultima:
        hallazgo(
            f"Entre la década de {primera} y la de {ultima}, la energía mediana "
            f"pasó de {dec(medianas.loc[primera, 'Energía'])} a "
            f"{dec(medianas.loc[ultima, 'Energía'])} y la acústica de "
            f"{dec(medianas.loc[primera, 'Acústica'])} a "
            f"{dec(medianas.loc[ultima, 'Acústica'])}. La positividad pasó de "
            f"{dec(medianas.loc[primera, 'Positividad'])} a "
            f"{dec(medianas.loc[ultima, 'Positividad'])}. "
            "Estos valores describen las canciones del catálogo de cada época, "
            "no lo que la gente escuchaba."
        )

    st.markdown("**Una característica en detalle**")
    nombre = st.selectbox("Característica", list(CARACTERISTICAS.keys()))
    columna = CARACTERISTICAS[nombre]

    por_decada = df.groupby("decada")[columna].median().reset_index()
    cantidad = df.groupby("decada").size().reset_index(name="canciones")

    izq, der = st.columns([3, 2])

    with izq:
        fig = px.bar(por_decada, x="decada", y=columna,
                     title=f"{nombre}: valor mediano por década")
        fig.update_traces(marker_color=[color_de(d) for d in por_decada["decada"]])
        fig.update_xaxes(type="category", title=None)
        fig.update_yaxes(title=None)
        st.plotly_chart(estilo(fig), theme=None)

    with der:
        fig = px.bar(cantidad, x="decada", y="canciones",
                     title="Canciones por década")
        fig.update_traces(marker_color=[color_de(d) for d in cantidad["decada"]])
        fig.update_xaxes(type="category", title=None)
        fig.update_yaxes(title=None)
        st.plotly_chart(estilo(fig), theme=None)

    st.caption(
        "Se usa la mediana de cada década. Las décadas con menos canciones "
        "(gráfico de la derecha) son menos confiables."
    )

# ======================================================================
# 2. POPULARIDAD
# ======================================================================
with tab_popularidad:
    st.subheader("¿Qué hace que una canción sea más popular?")
    st.write(
        "La popularidad que informa Spotify es la **actual**, así que favorece a la "
        "música reciente. Acá se excluyen las canciones con popularidad 0."
    )

    pop_decada = con_pop.groupby("decada")["popularity"].median().reset_index()
    columnas_sonido = list(CARACTERISTICAS.values())

    opciones = ["Todas las décadas juntas"] + sorted(con_pop["decada"].unique().tolist())
    eleccion = st.selectbox("Medir la relación dentro de", opciones)

    if eleccion == "Todas las décadas juntas":
        base = con_pop
    else:
        base = con_pop[con_pop["decada"] == eleccion]

    corr = (
        base[columnas_sonido + ["popularity"]]
        .corr()["popularity"]
        .drop("popularity")
        .rename(index=NOMBRES)
        .reset_index()
    )
    corr.columns = ["caracteristica", "correlacion"]

    izq, der = st.columns(2)

    with izq:
        fig = px.bar(pop_decada, x="decada", y="popularity",
                     title="Popularidad mediana por década")
        fig.update_traces(marker_color=[color_de(d) for d in pop_decada["decada"]])
        fig.update_xaxes(type="category", title=None)
        fig.update_yaxes(title=None)
        st.plotly_chart(estilo(fig), theme=None)

    with der:
        fig = px.bar(corr.sort_values("correlacion"), x="correlacion", y="caracteristica",
                     orientation="h", title="Relación con la popularidad")
        fig.update_traces(marker_color="#22D3EE")
        fig.update_xaxes(range=[-1, 1], title=None)
        fig.update_yaxes(title=None)
        st.plotly_chart(estilo(fig), theme=None)

    st.caption(
        "La escala va de -1 a 1; cerca de 0 significa poca relación. "
        "Compará 'todas las décadas juntas' con una sola década."
    )

    # Hallazgo: relación global frente a relación dentro de cada década
    if len(con_pop) > 100:
        global_corr = (
            con_pop[columnas_sonido + ["popularity"]]
            .corr()["popularity"]
            .drop("popularity")
        )
        mejor = global_corr.abs().idxmax()

        maximos = []
        for _, grupo in con_pop.groupby("decada"):
            if len(grupo) > 100:
                c = grupo[columnas_sonido + ["popularity"]].corr()["popularity"].drop("popularity")
                maximos.append(c.abs().max())

        if maximos and con_pop["decada"].nunique() >= 2:
            dentro = pd.Series(maximos).median()
            hallazgo(
                f"Con todas las décadas juntas, la característica más ligada a la "
                f"popularidad es {NOMBRES[mejor]} (correlación "
                f"{dec(global_corr[mejor])}). Dentro de una misma década, la relación "
                f"más fuerte baja a {dec(dentro)} en la mediana de las décadas. "
                "Gran parte del vínculo entre sonido y popularidad se debe a la época: "
                "las canciones recientes son a la vez más enérgicas y más escuchadas. "
                "La correlación no demuestra que una cosa cause la otra."
            )
        elif maximos:
            hallazgo(
                f"En este rango la característica más ligada a la popularidad es "
                f"{NOMBRES[mejor]} (correlación {dec(global_corr[mejor])}). "
                "Ampliá el rango de años para comparar épocas distintas. "
                "La correlación no demuestra que una cosa cause la otra."
            )

# ======================================================================
# 3. GÉNEROS
# ======================================================================
with tab_generos:
    st.subheader("¿En qué se diferencian los géneros?")

    con_genero = df[~df["familia"].isin(["Sin género", "Otros"])]
    sin_clasificar = len(df) - len(con_genero)

    if con_genero.empty:
        st.info("No hay canciones con género en este rango de años.")
    else:
        izq, der = st.columns(2)

        with izq:
            cant = con_genero["familia"].value_counts().sort_values().reset_index()
            cant.columns = ["familia", "canciones"]
            fig = px.bar(cant, x="canciones", y="familia", orientation="h",
                         title="Canciones por familia")
            fig.update_traces(marker_color="#22D3EE")
            fig.update_xaxes(title=None)
            fig.update_yaxes(title=None)
            st.plotly_chart(estilo(fig, 460), theme=None)

        with der:
            perfil = (
                con_genero.groupby("familia")[["energy", "danceability", "valence", "acousticness"]]
                .median()
                .rename(columns=NOMBRES)
            )
            fig = px.imshow(
                perfil, text_auto=".2f", aspect="auto",
                color_continuous_scale=[[0, "#121E38"], [1, "#22D3EE"]],
                title="Perfil sonoro por familia",
            )
            fig.update_coloraxes(showscale=False)
            fig.update_xaxes(title=None)
            fig.update_yaxes(title=None)
            st.plotly_chart(estilo(fig, 460), theme=None)

        recientes = df_total[
            (~df_total["pop_cero"])
            & (df_total["year"] >= 1990)
            & (~df_total["familia"].isin(["Sin género", "Otros"]))
        ]
        pop_familia = (
            recientes.groupby("familia")["popularity"].median().sort_values().reset_index()
        )

        fig = px.bar(pop_familia, x="popularity", y="familia", orientation="h",
                     title="Popularidad mediana por familia (canciones desde 1990)")
        fig.update_traces(marker_color="#22D3EE")
        fig.update_xaxes(title=None)
        fig.update_yaxes(title=None)
        st.plotly_chart(estilo(fig, 420), theme=None)

        mayor = cant.iloc[-1]
        porcentaje = mayor["canciones"] / len(con_genero) * 100
        mas_energica = perfil["Energía"].idxmax()
        mas_acustica = perfil["Acústica"].idxmax()
        texto = (
            f"{mayor['familia']} es la familia con más canciones "
            f"({dec(porcentaje, 0)}% de las clasificadas). "
            f"{mas_energica} es la más enérgica y {mas_acustica} la más acústica. "
        )
        if not pop_familia.empty:
            texto += (
                f"Entre las canciones desde 1990, la más popular en la mediana es "
                f"{pop_familia.iloc[-1]['familia']}, aunque las diferencias entre "
                "familias son moderadas."
            )
        hallazgo(texto)

        st.caption(
            f"Se excluyen {formato(sin_clasificar)} canciones sin género o de la categoría "
            "'Otros', que se concentran antes de 1950 y en artistas no anglosajones. "
            "La popularidad se compara solo desde 1990 para no mezclar épocas muy distintas."
        )

# ======================================================================
# 4. ARTISTAS
# ======================================================================
with tab_artistas:
    st.subheader("¿Quiénes lideran y cómo se comparan?")

    criterio = st.radio(
        "Ordenar el ranking por",
        ["Cantidad de canciones", "Popularidad mediana"],
        horizontal=True,
    )

    por_artista = (
        con_pop.groupby("artista_principal")
        .agg(canciones=("popularity", "size"), valor=("popularity", "median"))
        .reset_index()
        .rename(columns={"artista_principal": "artista"})
    )

    if criterio == "Cantidad de canciones":
        ranking = df["artista_principal"].value_counts().head(15).sort_values().reset_index()
        ranking.columns = ["artista", "valor"]
        titulo = "Artistas con más canciones"
    else:
        minimo = st.slider("Mínimo de canciones por artista", 10, 100, 30)
        ranking = (
            por_artista[por_artista["canciones"] >= minimo]
            .sort_values("valor", ascending=False)
            .head(15)
            .sort_values("valor")
        )
        titulo = f"Artistas más populares (con {minimo} canciones o más)"

    if ranking.empty:
        st.info("Ningún artista cumple ese mínimo en el rango de años elegido. Probá con un mínimo menor.")
    else:
        fig = px.bar(ranking, x="valor", y="artista", orientation="h", title=titulo)
        fig.update_traces(marker_color="#22D3EE")
        fig.update_xaxes(title=None)
        fig.update_yaxes(title=None)
        st.plotly_chart(estilo(fig, 460), theme=None)

    cuentas = df["artista_principal"].value_counts()
    frecuentes = por_artista[por_artista["canciones"] >= 30].sort_values("valor", ascending=False)

    texto = (
        f"{cuentas.index[0]} es el artista con más canciones en este rango "
        f"({formato(int(cuentas.iloc[0]))}). "
    )
    if not frecuentes.empty:
        lider = frecuentes.iloc[0]
        texto += (
            f"Entre quienes tienen 30 canciones o más, el más popular es "
            f"{lider['artista']} (popularidad mediana {dec(lider['valor'], 0)}). "
        )
    texto += (
        "Medir cantidad o popularidad da rankings distintos: el primero refleja "
        "cómo está armado el catálogo y el segundo, qué se escucha hoy."
    )
    hallazgo(texto)

    st.subheader("Comparar artistas")

    lista_artistas = sorted(df["artista_principal"].unique())
    por_defecto = [a for a in ["Queen", "The Beatles"] if a in lista_artistas]

    elegidos = st.multiselect(
        "Elegí hasta dos artistas (podés escribir para buscar)",
        lista_artistas,
        default=por_defecto,
        max_selections=2,
    )

    if elegidos:
        comp = (
            df[df["artista_principal"].isin(elegidos)]
            .groupby("artista_principal")[["energy", "danceability", "valence", "acousticness"]]
            .median()
            .rename(columns=NOMBRES)
            .reset_index()
        )
        largo = comp.melt(
            id_vars="artista_principal", var_name="caracteristica", value_name="valor"
        )

        fig = px.bar(largo, x="caracteristica", y="valor", color="artista_principal",
                     barmode="group", color_discrete_sequence=["#22D3EE", "#FBBF24"],
                     title="Perfil sonoro")
        fig = estilo(fig)
        fig.update_layout(showlegend=True, legend_title_text="")
        fig.update_xaxes(title=None)
        fig.update_yaxes(title=None)
        st.plotly_chart(fig, theme=None)

# ======================================================================
# NOTAS SOBRE LOS DATOS
# ======================================================================
with st.expander("Cómo se prepararon los datos"):
    st.markdown(
        """
- **Fuente:** Spotify Dataset 1921-2020 (Kaggle): un archivo de canciones y otro de géneros por artista.
- **Audiolibros:** se eliminaron las pistas con `speechiness` de 0,66 o más (casi todas son capítulos de audiolibros).
- **Popularidad 0:** se conservan, pero se excluyen al analizar popularidad. Es la popularidad **actual**, por eso muchas canciones antiguas tienen 0.
- **Duración:** se pasó a minutos y se eliminaron las pistas de más de 20 minutos (ruidos y sonidos para dormir, y algo de música muy larga).
- **Artista principal:** se usa el primer artista de cada canción.
- **Géneros:** se agruparon en 12 familias por palabras clave. Las canciones sin género y las de la categoría 'Otros' no entran en la pestaña de géneros.
- **Limitaciones:** el año 2020 está incompleto, el catálogo no es lo que la gente escuchaba en cada época y la correlación no implica causalidad.
        """
    )