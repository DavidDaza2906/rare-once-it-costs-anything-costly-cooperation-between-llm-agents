#!/usr/bin/env bash
# Secuencia post-lote: se ejecuta A MANO cuando el bloque B haya cerrado. NO se corre antes.
# Orden: verificar B → congelar → precio 0 → (opcional) 30 pasos. Cada brazo usa su propia escena
# resuelta (validada aparte) y su propia etiqueta. Puertos y archivos son los mismos, así que va EN
# SERIE, nunca en paralelo con nada.
set -euo pipefail
cd /home/daw/Sprint
source ~/.hermes/.env 2>/dev/null || true
export OPENCODE_GO_BASE_URL="https://opencode.ai/zen/go/v1"
PY=.venv-inspect/bin/python

if pgrep -f "harness/lote.py" >/dev/null; then
  echo "ABORTA: lote.py sigue corriendo. Espera a que cierre el bloque B."; exit 1
fi
if pgrep -f "harness/servicios.py" >/dev/null; then echo "servicios.py sigue arriba (ok, se reutiliza)"; fi

echo "== 1. salud final del lote (bloques A+B, sin la interrumpida) =="
$PY herramientas/salud_lote.py --desde 20260913T180000 --hash bf1b18a696a98476 --tope 10400000

echo "== 2. agregar + congelar las 80 =="
$PY harness/agregar.py
$PY herramientas/congelar.py

echo "== 3. brazo PRECIO 0 (8 corridas, misma tarea/hash_textos, precios 0) =="
# validar a la ruta real solo ahora (B ya cerró, no hay riesgo de pisar escena.resuelta.json)
$PY harness/validador.py escena-costo-cero.json escena-costo-cero.resuelta.json
$PY harness/lote.py --escena escena-costo-cero.resuelta.json --corridas 8 --tope 1400000 --etiqueta costo-cero-final

echo "== 4. (OPCIONAL, decidir según reloj y tokens) brazo 30 PASOS =="
echo "   para correrlo: $PY harness/validador.py escena-30.json escena-30.resuelta.json && \\"
echo "                  $PY harness/lote.py --escena escena-30.resuelta.json --corridas 8 --tope 1200000 --etiqueta pres30"

echo "== 5. congelar de nuevo y análisis final sobre TODO =="
$PY herramientas/congelar.py
echo "   luego: $PY analisis/estimador.py --remuestreos 10000   (primera vez que se mira el contraste)"
echo "hecho."
