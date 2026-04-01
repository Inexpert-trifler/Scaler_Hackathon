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
RUN mkdir -p logs agent
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=7860
ENV LLM_MODE=mock
ENV USE_TORCH_SCORER=false
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1
CMD ["python", "start.py"]
