#!/usr/bin/env bash
# Copia de seguridad de solo lectura del lote: salidas, escenas, instrumento, preregistro.
set -euo pipefail
cd /home/daw/Sprint
marca=$(date -u +%Y%m%dT%H%M)
tar --exclude='__pycache__' -czf "respaldos/lote_${marca}.tar.gz" \
    salidas escena*.json harness/instrumento.json PREREGISTRO.md ESTADO.md todo*.md 2>/dev/null
echo "$(date -u +%H:%M) UTC respaldo respaldos/lote_${marca}.tar.gz $(du -h "respaldos/lote_${marca}.tar.gz" | cut -f1)"
