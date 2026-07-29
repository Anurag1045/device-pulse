# Stage 1: builder — installs dependencies into a separate prefix
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: runtime — lean final image with no build tools
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy only installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app/ ./app/

EXPOSE 8000

ENV FLASK_APP=app.main

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]
