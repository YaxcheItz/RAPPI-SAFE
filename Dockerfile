# Usa una imagen oficial de Python ligera
FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Variables de entorno para optimizar Python en Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependencias del sistema operativo (necesarias para algunos paquetes de Python)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia los requerimientos y los instala
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia el resto del código del proyecto al contenedor
COPY . /app/

# Expone el puerto que usa la aplicación
EXPOSE 8000

# Comando para iniciar la aplicación (migraciones, archivos estáticos y Daphne para WebSockets)
CMD python manage.py migrate && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p 8000 mysite.asgi:application
