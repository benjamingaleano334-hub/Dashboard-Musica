# Un siglo de música en Spotify

Dashboard interactivo hecho con **Streamlit** que explora cómo cambió el sonido de las canciones entre 1921 y 2020 y qué se relaciona con su popularidad.

**Demo en vivo:** https://dashboard-musica-1950-2020.streamlit.app

## Pregunta central

> ¿Cómo cambió el sonido de las canciones a lo largo de las décadas y qué hace que una sea más popular que otra?

El dashboard se organiza en cuatro pestañas. Cada una parte de una pregunta y termina con un recuadro que resume lo que muestran los datos (se recalcula con el filtro de años):

| Pestaña | Pregunta |
|---|---|
| **Evolución** | ¿Cómo cambió el sonido de las canciones? |
| **Popularidad** | ¿Qué hace que una canción sea más popular? |
| **Géneros** | ¿En qué se diferencian los géneros? |
| **Artistas** | ¿Quiénes lideran y cómo se comparan? |

## Datos

Se usa el dataset **Spotify Dataset 1921-2020** de Kaggle, compuesto por dos archivos:

- `data.csv`: una fila por canción, con año, popularidad y características de audio calculadas por Spotify (energía, acústica, bailabilidad, positividad, volumen, tempo, duración).
- `data_w_genres.csv`: una fila por artista, con la lista de sus géneros.

Los archivos originales no están incluidos en este repositorio. El dashboard usa la tabla ya limpia, en `data/clean/spotify_limpio.csv`.

## Tratamiento de los datos

| Paso | Decisión | Motivo |
|---|---|---|
| Audiolibros | Se eliminaron las pistas con `speechiness` ≥ 0,66 | Son capítulos de libros leídos en voz alta, no música |
| Duración | Se pasó a minutos y se eliminaron las pistas de más de 20 minutos | Ruidos y sonidos para dormir; efecto mínimo (0,16% de las pistas) |
| Popularidad 0 | Se conservan y se marcan con `pop_cero` | La popularidad es la **actual** y no la de la época de lanzamiento. Se excluyen solo al analizar popularidad |
| Artista principal | Se usa el primer artista de cada canción | Permite cruzar con los géneros y armar rankings |
| Géneros | Se agruparon 2.972 géneros en 12 familias por palabras clave | Imposibles de graficar sin agrupar |
| Sin género | Se conservan con la etiqueta "Sin género" | No se pierden canciones en las otras secciones |

La tabla final tiene unas 165.000 canciones y 14 columnas.

## Cómo ejecutarlo localmente

Requiere Python 3.9 o superior.

```bash
# 1. Clonar el repositorio
git clone https://github.com/benjamingaleano334-hub/Dashboard-Musica.git
cd Dashboard-Musica

# 2. Crear y activar un entorno virtual
python -m venv venv
venv\Scripts\activate          # en Windows
# source venv/bin/activate     # en Mac o Linux

# 3. Instalar las dependencias
pip install -r requirements.txt

# 4. Correr el dashboard
streamlit run app.py
```

Se abre automáticamente en `http://localhost:8501`.

## Estructura del proyecto

```
├── app.streamlit/
│   └── config.toml          # tema visual
├── data/
│       └── spotify_limpio.csv
├── app.py                   # el dashboard
├── requirements.txt
└── README.md
```

## Tecnologías

- Python
- Streamlit
- Pandas
- Plotly

## Limitaciones

- La popularidad es la actual, no la que tuvo cada canción en su época.
- El año 2020 está incompleto y los años 20 y 30 tienen pocas canciones, por eso el filtro inicial va de 1950 a 2019.
- Es un catálogo de Spotify, no un registro de lo que la gente escuchaba en cada época.
- Las familias de género son una agrupación propia y aproximada, asignada por artista.
- Las canciones sin género se concentran antes de 1950 y en artistas no anglosajones.
- La correlación entre popularidad y características de audio no implica causalidad.

## Autor

Benjamin Galeano · Analisis y exploracion de datos / Instituto tecnologico Beltran · 2026
