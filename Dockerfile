FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "openenv-core>=0.2.0" || \
    pip install --no-cache-dir "openenv>=0.2.0" || true

# Copy all files
COPY . .

EXPOSE 7860

CMD ["python", "-m", "server.app"]
