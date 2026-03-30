FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY models.py .
COPY client.py .
COPY openenv.yaml .
COPY inference.py .
COPY start.py .
COPY app ./app
COPY server ./server
COPY scorer ./scorer
COPY agent ./agent
RUN mkdir -p logs
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV LLM_MODE=mock
ENV USE_TORCH_SCORER=false
EXPOSE 8000
CMD ["python", "start.py"]
