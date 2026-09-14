# Panel del experimento (solo lectura) para Dokploy.
#
# El panel no tiene dependencias: solo la biblioteca estandar de Python. Resuelve sus rutas
# desde su propia ubicacion (dashboard/ -> raiz del repositorio), asi que el arbol se copia
# con su forma original: el panel, los datos de las corridas y los documentos.
#
# Arranca con --red: escucha en 0.0.0.0 y exige contrasena. La contrasena se toma de la
# variable de entorno DASHBOARD_CLAVE (se guarda su SHA-256 en memoria, nunca el texto).
# Si no se define, el panel genera una y deja su hash en dashboard/.clave.

FROM python:3.12-slim

WORKDIR /app

COPY dashboard/ ./dashboard/
COPY reportes/ ./reportes/
COPY salidas/ ./salidas/
COPY salidas-generalizacion/ ./salidas-generalizacion/
COPY docs/ ./docs/
COPY escena.resuelta.json ./escena.resuelta.json

ENV PYTHONUNBUFFERED=1
EXPOSE 8890

CMD ["python3", "dashboard/servidor.py", "8890", "--red"]
