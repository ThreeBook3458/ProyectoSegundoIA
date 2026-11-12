"""
Interfaz muy básica para visualizar los resultados de proyecto2.ipynb.
Ejecuta las celdas del notebook en orden y muestra su salida en Streamlit.

Uso:
    streamlit run app.py
"""

import contextlib
import io
import json
import os
import re
import time
import traceback
import warnings
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
NOTEBOOK = BASE_DIR / "proyecto2.ipynb"

# Los CSV que genera el notebook se crean en la carpeta de trabajo actual.
os.chdir(BASE_DIR)

st.set_page_config(page_title="Resultados Proyecto 2", page_icon="📦", layout="wide")


def titulo_celda(fuente: str, indice: int) -> str:
   
    # Primero las secciones marcadas como FASE (en comentarios o en prints).
    for linea in fuente.splitlines():
        m = re.search(r"FASE\s+(\d+)\s*:\s*(.+)", linea)
        if m:
            numero, resto = m.group(1), m.group(2)
            resto = re.split(r'\\n|"|`|---', resto)[0].strip(" -=\"'")
            return f"FASE {numero}: {resto}"
    # Si no hay FASE, se usa el primer comentario numerado.
    for linea in fuente.splitlines():
        limpia = linea.strip().lstrip("#").strip(" -=")
        m = re.match(r"(\d+\.\s+[A-ZÁÉÍÓÚÑ][^\n]{5,70})", limpia)
        if m:
            return m.group(1).strip(" -=")
    return f"Celda {indice + 1}"


def articulos_generados(fuente: str, error):
    """Devuelve los archivos que produce una celda (gráfica de la Fase 7,
    CSV de la Fase 8) para mostrarlos en la interfaz."""
    archivos = {}
    if error is None:
        if "graficas_resultados.png" in fuente:
            ruta = BASE_DIR / "graficas_resultados.png"
            if ruta.exists():
                archivos["imagen"] = ruta.read_bytes()
        if "datos_experimentales.csv" in fuente:
            ruta = BASE_DIR / "datos_experimentales.csv"
            if ruta.exists():
                archivos["csv"] = ruta.read_text(encoding="utf-8")
    return archivos


@st.cache_data(show_spinner=False, hash_funcs={str: lambda s: s})
def ejecutar_notebook(ruta: str, huella: float):
    """Ejecuta todas las celdas de código en un mismo espacio de nombres
    y devuelve el texto impreso por cada una."""
    # Backend sin ventana: las gráficas del notebook se guardan como PNG.
    os.environ["MPLBACKEND"] = "Agg"
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        plt = None

    nb = json.loads(Path(ruta).read_text(encoding="utf-8"))
    espacio = {}
    resultados = []
    inicio = time.perf_counter()

    for i, celda in enumerate(nb["cells"]):
        if celda["cell_type"] != "code":
            continue
        fuente = "".join(celda["source"])
        salida = io.StringIO()
        error = None
        try:
            with contextlib.redirect_stdout(salida):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    exec(compile(fuente, f"celda_{i + 1}", "exec"), espacio)
        except Exception:
            error = traceback.format_exc()
        finally:
            if plt is not None:
                plt.close("all")

        resultados.append(
            {
                "numero": i + 1,
                "titulo": titulo_celda(fuente, i),
                "codigo": fuente,
                "salida": salida.getvalue().strip(),
                "error": error,
                **articulos_generados(fuente, error),
            }
        )

    duracion = time.perf_counter() - inicio
    return resultados, duracion


if not NOTEBOOK.exists():
    st.error(f"No se encontró el notebook: {NOTEBOOK}")
    st.stop()

huella = NOTEBOOK.stat().st_mtime
try:
    celdas, duracion = ejecutar_notebook(str(NOTEBOOK), huella)
except Exception:
    st.error("No se pudo leer el notebook.")
    st.code(traceback.format_exc(), language="text")
    st.stop()

# ---------------- Barra lateral ----------------
st.sidebar.title("📦 Proyecto 2")
st.sidebar.caption(f"`{NOTEBOOK.name}` · {len(celdas)} celdas")
vista = st.sidebar.radio(
    "Ver",
    ["Todo el notebook"] + [f"Celda {c['numero']}: {c['titulo']}" for c in celdas],
)
indice_vista = (
    None
    if vista == "Todo el notebook"
    else int(vista.split(":")[0].replace("Celda", "").strip()) - 1
)
if st.sidebar.button("🔄 Volver a ejecutar", width="stretch"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.divider()
st.sidebar.caption(f"Ejecutado en {duracion:.2f} s")

# ---------------- Contenido ----------------
st.title("Resultados del notebook")
st.caption("Interfaz básica: se muestran las salidas de cada celda de proyecto2.ipynb.")

seleccionadas = celdas if indice_vista is None else [celdas[indice_vista]]

for celda in seleccionadas:
    st.subheader(f"Celda {celda['numero']} · {celda['titulo']}")
    with st.expander("Ver código de la celda", expanded=False):
        st.code(celda["codigo"], language="python")

    if celda["error"]:
        st.error("La celda terminó con un error:")
        st.code(celda["error"], language="text")
    elif celda["salida"]:
        st.code(celda["salida"], language="text")
    else:
        st.info("Esta celda no imprime resultados.")

    if celda.get("imagen"):
        st.image(
            celda["imagen"],
            caption="graficas_resultados.png (Fase 7)",
            width="stretch",
        )
        st.download_button(
            "⬇️ Descargar gráficas (.png)",
            data=celda["imagen"],
            file_name="graficas_resultados.png",
            mime="image/png",
            key=f"dl_png_{celda['numero']}",
        )

    if celda.get("csv"):
        import pandas as pd

        st.markdown("**datos_experimentales.csv** (Fase 8)")
        st.dataframe(pd.read_csv(io.StringIO(celda["csv"])), width="stretch")
        st.download_button(
            "⬇️ Descargar datos experimentales (.csv)",
            data=celda["csv"].encode("utf-8"),
            file_name="datos_experimentales.csv",
            mime="text/csv",
            key=f"dl_csv_{celda['numero']}",
        )

if indice_vista is None:
    todas = "\n\n".join(
        f"===== CELDA {c['numero']}: {c['titulo']} =====\n{c['salida'] or '(sin salida)'}"
        for c in celdas
    )
    st.download_button(
        "⬇️ Descargar todos los resultados (.txt)",
        data=todas.encode("utf-8"),
        file_name="resultados_proyecto2.txt",
        mime="text/plain",
    )
