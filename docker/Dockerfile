# OpenCog Medical Demo — Docker Image
# Based on Ubuntu 20.04 with OpenCog dependencies

FROM ubuntu:20.04

LABEL maintainer="opencog-medical-demo"
LABEL description="OpenCog AtomSpace + PLN Medical Reasoning Demo"
LABEL version="1.0"

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ─── System Dependencies ──────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    libboost-all-dev \
    libssl-dev \
    python3 \
    python3-pip \
    python3-dev \
    cython3 \
    guile-3.0 \
    guile-3.0-dev \
    libgtest-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Make python3 the default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10

# ─── Build CogUtil (OpenCog utility library) ──────────────────────────────────
WORKDIR /opt/opencog

RUN git clone https://github.com/opencog/cogutil.git && \
    cd cogutil && \
    mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install && \
    ldconfig

# ─── Build AtomSpace ──────────────────────────────────────────────────────────
RUN git clone https://github.com/opencog/atomspace.git && \
    cd atomspace && \
    mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install && \
    ldconfig

# ─── Build URE (Unified Rule Engine / PLN) ────────────────────────────────────
RUN git clone https://github.com/opencog/ure.git && \
    cd ure && \
    mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install && \
    ldconfig

# ─── Python Dependencies ──────────────────────────────────────────────────────
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Copy Project Files ───────────────────────────────────────────────────────
COPY . .

# Install the project in editable mode
RUN pip install -e . 2>/dev/null || true

# ─── Expose Jupyter Port ──────────────────────────────────────────────────────
EXPOSE 8888

# ─── Entry Point ─────────────────────────────────────────────────────────────
CMD ["python", "-m", "src.demo.run_demo"]
