"""Chequeo estático: `self` usado fuera de un método.

Defecto que atrapa: una llamada parchada o una línea movida que queda dentro de una función de módulo
donde `self` no existe. `py_compile` NO lo detecta (es un NameError, falla en tiempo de ejecución) y una
prueba que ejecute solo la función invocada tampoco: el punto de llamada es el que corre. Paso el 13 sep
con `limpiar_estado_de_puertos([ag], self.salida)` dentro de `correr()`, y costó un lote de corridas
rotas que solo se vieron al mirar por qué faltaba el archivo de puertos.

Se recorre el AST de cada módulo del arnés. Un `self` cargado es legal si alguna función que lo encierra
lo recibe como parámetro; si no, es un error.

Uso:  python3 harness/prueba_estatica.py
"""
import ast
import glob
import os

BASE = os.path.dirname(os.path.abspath(__file__))
fallos = []


def tiene_self(nodo: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return bool(nodo.args.args) and nodo.args.args[0].arg in ("self", "cls")


def revisar(nodos, en_metodo: bool, archivo: str, hallazgos: list) -> None:
    for nodo in nodos:
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            revisar(nodo.body, en_metodo or tiene_self(nodo), archivo, hallazgos)
            continue
        if isinstance(nodo, ast.Name) and isinstance(nodo.ctx, ast.Load) and nodo.id == "self" and not en_metodo:
            hallazgos.append((archivo, nodo.lineno))
        for hijo in ast.iter_child_nodes(nodo):
            revisar([hijo], en_metodo, archivo, hallazgos)


def main() -> None:
    for ruta in sorted(glob.glob(os.path.join(BASE, "*.py"))):
        nombre = os.path.basename(ruta)
        try:
            arbol = ast.parse(open(ruta, encoding="utf-8").read(), filename=ruta)
        except SyntaxError as e:
            print(f"  FALLA {nombre}: no parsea ({e})")
            fallos.append(nombre)
            continue
        hallazgos = []
        revisar(arbol.body, False, nombre, hallazgos)
        if hallazgos:
            for archivo, linea in hallazgos:
                print(f"  FALLA {archivo}:{linea}: 'self' fuera de un metodo")
            fallos.append(nombre)
    print()
    if fallos:
        print(f"  {len(fallos)} modulo(s) con 'self' fuera de metodo")
        raise SystemExit(1)
    print("  sin 'self' fuera de metodo en el arnes: APTO")


if __name__ == "__main__":
    main()
