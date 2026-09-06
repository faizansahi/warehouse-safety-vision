FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml .
COPY src src
RUN pip install --no-cache-dir .
CMD ["uvicorn","warehouse_vision.main:app","--host","0.0.0.0","--port","8000"]
