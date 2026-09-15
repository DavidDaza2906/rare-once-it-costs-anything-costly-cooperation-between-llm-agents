# Panel del experimento (solo lectura) para Dokploy.
#
# El panel no tiene dependencias: solo la biblioteca estandar de Python. Resuelve sus rutas
# desde su propia ubicacion (dashboard/ -> raiz del repositorio), asi que el arbol se copia
# con su forma original: el panel, los datos de las corridas y los documentos.
#
# Arranca con --red: escucha en 0.0.0.0. Va con --clave anular, o sea SIN contrasena: el panel
# sirve los datos a quien llegue a la URL. Es una decision del equipo (los datos ya son publicos
# en el repositorio de entrega); para volver a exigir contrasena basta quitar ese argumento y
# definir DASHBOARD_CLAVE, o dejar que el panel genere una.

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

CMD ["python3", "dashboard/servidor.py", "8890", "--red", "--clave", "anular"]
