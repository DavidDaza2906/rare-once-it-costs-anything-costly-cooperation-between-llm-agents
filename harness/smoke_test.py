"""Prueba mínima de integración Inspect AI <-> gateway openai-compatible.

Objetivo: comprobar dos cosas que el experimento necesita y que un gateway
agregador puede no soportar:
  1. que una llamada de chat completions funciona;
  2. que el modelo EMITE tool calls con el formato de OpenAI y que Inspect las
     ejecuta (los agentes del sandbox dependen de eso para usar bash()).

El scorer exige la cadena "42", que solo está disponible dentro del resultado
de la herramienta: si la respuesta llega a 42, el ciclo de tool calling
funcionó de punta a punta.
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
from inspect_ai.solver import generate, use_tools
from inspect_ai.tool import tool
from inspect_ai.util import store


@tool
def leer_nota():
    async def execute(ruta: str) -> str:
        """Lee una nota del registro compartido.

        Args:
            ruta: Ruta de la nota dentro del registro.

        Returns:
            El contenido de la nota.
        """
        store().set("llamada_herramienta", True)
        return "NOTA-INFO: el scorer acepta como respuesta valida el numero 42."
    return execute


@task
def smoke_gateway():
    return Task(
        dataset=[
            Sample(
                input=(
                    "Debes leer la nota que esta en 'registro/nota.txt' usando la "
                    "herramienta disponible y responder unicamente con el numero "
                    "que la nota indica como valido."
                ),
                target="42",
            )
        ],
        solver=[use_tools(leer_nota()), generate()],
        scorer=match(),
    )
