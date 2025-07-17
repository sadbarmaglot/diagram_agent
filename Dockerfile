FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    graphviz \
    libgraphviz-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -Ls https://astral.sh/uv/install.sh | bash && \
    find /root -name uv -type f -exec cp {} /usr/local/bin/uv \;

WORKDIR /app
COPY requirements.txt ./

RUN uv pip install --system --no-cache-dir -r requirements.txt

COPY . .

RUN test -d static