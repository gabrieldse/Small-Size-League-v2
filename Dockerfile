FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Update system and install base dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    curl \
    wget \
    python3 \
    python3-pip \
    python3-venv \
    # grSim dependencies
    qtbase5-dev \
    libqt5opengl5-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libprotobuf-dev \
    protobuf-compiler \
    libode-dev \
    && rm -rf /var/lib/apt/lists/*

# Install grSim
RUN git clone https://github.com/RoboCup-SSL/grSim.git /opt/grSim-src && \
    mkdir -p /opt/grSim-src/build && \
    cd /opt/grSim-src/build && \
    cmake .. && \
    make -j$(nproc) && \
    make install

# Setup Python Virtual Environment
RUN python3 -m venv /opt/venv

# Make sure we use the venv by default
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Install Rust for documentation
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN cargo install mdbook

WORKDIR /workspace

CMD ["bash"]
