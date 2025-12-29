FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgomp1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to /app/gymmando_graph/ to match import structure
# (imports use 'from gymmando_graph.modules...')
COPY . /app/gymmando_graph/

# Set PYTHONPATH so the gymmando_graph module is discoverable
ENV PYTHONPATH=/app
# Suppress the ONNX warning
ENV ORT_LOGGING_LEVEL=3

# Pre-download VAD models to avoid runtime download issues
RUN python -m livekit.agents download-files

CMD ["python", "-u", "-m", "gymmando_graph.livekit_agent", "start"]