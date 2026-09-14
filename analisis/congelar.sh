#!/usr/bin/env bash
# Congelamiento: la secuencia completa, en orden, en un solo comando.
#
#   bash analisis/congelar.sh
#
# Se corre UNA vez, cuando el ultimo lote haya cerrado. Hace, en este orden:
#   1. trae salidas/ del arbol 2 al arbol 1, para que todo quede en un solo lugar
#   2. el analisis confirmatorio (la mirada, con las tres declaradas)
#   3. el analisis del 2x2 de abstencion
#   4. el analisis de la familia del incidente
#   5. la auditoria de integridad sobre todas las familias
#   6. las figuras vectoriales
#   7. la tabla de numeros congelados y los hashes de los archivos que la sostienen
#
# No calcula nada por su cuenta: solo encadena los guiones ya probados y deja el rastro de hashes.
#
# Orden obligatorio antes de correrlo: el ultimo lote del factorial cerrado, la corrida de reemplazo
# por la contaminacion de la suite ya corrida (si falta, el N queda uno corto), y ningun lote vivo
# (lo comprueba el paso 0).
#
# set -e es deliberado: si un paso falla, el congelamiento se detiene en vez de dejar un archivo de
# numeros a medias que se lea como si estuviera congelado. Un fallo aqui es preferible a un numero falso.

set -eu
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
ARBOL2="$(dirname "$RAIZ")/Sprint-2"
PY="$RAIZ/.venv-inspect/bin/python"
PYFIG="/tmp/venv-figuras/bin/python"
cd "$RAIZ" || exit 1

echo "=== 0. comprobacion: no hay lotes vivos ==="
if pgrep -f "[l]ote.py" >/dev/null; then
  echo "  HAY LOTES CORRIENDO: se detiene. El congelamiento espera a que cierren."
  pgrep -af "[l]ote.py" | sed 's/^/    /'
  exit 1
fi
echo "  ninguno: se puede congelar"

echo
echo "=== 1. traer los datos del arbol 2 ==="
traidas=0
if [ -d "$ARBOL2/salidas" ]; then
  for d in "$ARBOL2"/salidas/2026*/; do
    [ -d "$d" ] || continue
    nombre="$(basename "$d")"
    if [ ! -d "$RAIZ/salidas/$nombre" ]; then
      cp -r "$d" "$RAIZ/salidas/$nombre" && traidas=$((traidas+1))
    fi
  done
fi
echo "  corridas traidas del arbol 2: $traidas (las ya presentes no se tocan)"

echo
echo "=== 2. analisis confirmatorio (la mirada) ==="
touch /tmp/.marca-congelamiento
"$PY" analisis/confirmatorio.py
# Compuerta: la mirada tiene que haber ocurrido AHORA. Un archivo viejo significa que el paso no corrio
# como se cree, y entonces el congelamiento se detiene en vez de congelar numeros que no son de hoy.
if [ reportes/confirmatorio.json -ot /tmp/.marca-congelamiento ]; then
  echo "  FALLA: reportes/confirmatorio.json es anterior al arranque del congelamiento."
  echo "         El paso 2 no produjo un archivo nuevo: se detiene y se revisa."
  exit 1
fi
echo "  compuerta: la mirada quedo escrita ahora"

echo
echo "=== 3. abstencion: 2x2 ==="
"$PY" analisis/abstencion.py

echo
echo "=== 4. familia del incidente ==="
"$PY" analisis/incidente.py

echo
echo "=== 5. auditoria de integridad ==="
"$PY" analisis/auditoria_aislamiento.py 2>&1 | tail -12

echo
echo "=== 6. figuras ==="
if [ -x "$PYFIG" ]; then
  "$PYFIG" analisis/figuras.py
else
  echo "  falta el entorno de figuras ($PYFIG): se omiten. Recrearlo con:"
  echo "    python3 -m venv /tmp/venv-figuras && /tmp/venv-figuras/bin/python -m pip install matplotlib"
fi

echo
echo "=== 7. tabla de numeros y hashes del congelamiento ==="
mkdir -p docs
"$PY" analisis/tabla-numeros.py > docs/NUMEROS-CONGELADOS.md
echo "  escrito docs/NUMEROS-CONGELADOS.md"
echo
echo "  hashes de los archivos que sostienen los numeros:"
for f in reportes/confirmatorio.json reportes/abstencion-2x2.json reportes/incidente.json; do
  if [ -f "$f" ]; then
    printf "    %-34s %s\n" "$f" "$(sha256sum "$f" | cut -c1-16)"
  fi
done
echo
echo "  figuras:"
ls -1 figuras/*.pdf 2>/dev/null | sed 's/^/    /'
echo
echo "CONGELADO. Los numeros estan en docs/NUMEROS-CONGELADOS.md y sus hashes arriba."
