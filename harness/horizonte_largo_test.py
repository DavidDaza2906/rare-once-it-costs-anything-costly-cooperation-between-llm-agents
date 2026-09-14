"""Prueba de horizonte largo para glm-5.3-flash.

Pregunta que responde: ¿el modelo sostiene el uso de herramientas a lo largo de
muchos turnos, o colapsa / abandona la tarea a mitad de camino?

Es la amenaza existencial del proyecto ahora que el experimento usa un solo
modelo: si no puede ejecutar acciones de forma sostenida, no hay instrumento.

La tarea exige, como mínimo, siete llamadas de herramienta en orden:
listar -> leer x3 -> escribir -> leer (verificar) -> escribir resumen.
El scorer comprueba el contenido exacto de los dos archivos producidos, así que
un acierto implica que completó la secuencia, no que la describió.
"""

from inspect_ai import Task, task
from inspect_ai.agent import as_solver, react
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, Target, accuracy, scorer, stderr
from inspect_ai.tool import ToolError, tool
from inspect_ai.solver import solver
from inspect_ai.util import store

FRAGMENTOS = {
    "datos/f1.txt": "ARRIBA-A",
    "datos/f2.txt": "MEDIO-B",
    "datos/f3.txt": "ABAJO-C",
}
ESPERADO = "ARRIBA-A\nMEDIO-B\nABAJO-C\n"
ESPERADO_RESUMEN = "3"


@solver
def sembrar():
    """Deja el sistema de archivos inicial en el store antes de que actúe el agente."""
    async def solve(state, generate):
        store().set("disco", dict(FRAGMENTOS))
        store().set("escrituras", 0)
        return state
    return solve


@tool
def listar_archivos():
    async def execute(carpeta: str = "datos") -> str:
        """Lista los archivos disponibles en una carpeta.

        Args:
            carpeta: Carpeta a listar.

        Returns:
            Los nombres de archivo, uno por línea.
        """
        disco = store().get("disco", {})
        nombres = [r for r in disco if r.startswith(carpeta)]
        return "\n".join(sorted(nombres)) if nombres else f"(no hay archivos en {carpeta})"
    return execute


@tool
def leer_archivo():
    async def execute(ruta: str) -> str:
        """Lee el contenido de un archivo.

        Args:
            ruta: Ruta del archivo a leer.

        Returns:
            El contenido del archivo.
        """
        disco = store().get("disco", {})
        if ruta not in disco:
            raise ToolError(f"no existe: {ruta}")
        return disco[ruta]
    return execute


@tool
def escribir_archivo():
    async def execute(ruta: str, contenido: str) -> str:
        """Escribe contenido en un archivo, reemplazando lo que hubiera.

        Args:
            ruta: Ruta del archivo a escribir.
            contenido: Contenido a escribir.

        Returns:
            Confirmación de la escritura.
        """
        disco = dict(store().get("disco", {}))
        disco[ruta] = contenido
        store().set("disco", disco)
        store().set("escrituras", store().get("escrituras", 0) + 1)
        return f"escrito: {ruta} ({len(contenido)} caracteres)"
    return execute


@scorer(metrics=[accuracy(), stderr()])
def archivos_correctos():
    async def score(state, target: Target) -> Score:
        disco = store().get("disco", {})
        salida = disco.get("datos/salida.txt", "")
        resumen = disco.get("datos/resumen.txt", "").strip()
        ok = salida == ESPERADO and resumen == ESPERADO_RESUMEN
        detalle = (
            f"salida={'OK' if salida == ESPERADO else repr(salida)[:80]} "
            f"resumen={'OK' if resumen == ESPERADO_RESUMEN else repr(resumen)[:40]} "
            f"escrituras={store().get('escrituras', 0)}"
        )
        return Score(value="C" if ok else "I", answer=salida, explanation=detalle)
    return score


@task
def horizonte_largo():
    instruccion = (
        "Trabajas en un sistema de archivos. Tienes tres herramientas: "
        "listar_archivos, leer_archivo y escribir_archivo.\n\n"
        "Haz esto, en este orden:\n"
        "1. Lista los archivos de la carpeta 'datos'.\n"
        "2. Lee los tres archivos f1, f2 y f3.\n"
        "3. Concatena sus contenidos, en el orden f1, f2, f3, separados por un salto de linea, "
        "y escribe el resultado en 'datos/salida.txt' (termina con un salto de linea).\n"
        "4. Vuelve a leer 'datos/salida.txt' para verificar que quedo bien.\n"
        "5. Cuenta cuantas lineas tiene 'datos/salida.txt' y escribe SOLO ese numero "
        "en 'datos/resumen.txt'.\n\n"
        "No expliques nada fuera de las herramientas: usa las herramientas hasta terminar."
    )
    return Task(
        dataset=[Sample(input=instruccion)],
        solver=[sembrar(), as_solver(react(tools=[listar_archivos(), leer_archivo(), escribir_archivo()]))],
        scorer=archivos_correctos(),
        message_limit=40,
    )
