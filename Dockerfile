# Base image with Python
FROM rust:latest AS base

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/London
ENV DEBIAN_FRONTEND="noninteractive"


    # Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    python3-setuptools \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*


# Set environment variables
ENV PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

RUN pip3 install --break-system-packages \
    maturin \
    setuptools-rust \
    setuptools \
    wheel \
    tx_engine


WORKDIR /app/src
COPY ./src/* .

WORKDIR /app/python/src
COPY ./python/src/* . 
#RUN pip3 install -r requirements.txt

WORKDIR /app
COPY ./cargo.toml Cargo.toml
COPY ./requirements.txt requirements.txt
FROM base AS release

WORKDIR /app

COPY ./examples/* ./examples/
RUN maturin build --release --out target/wheels --interpreter python3 \
    && $VIRTUAL_ENV/bin/pip install --break-system-packages --root-user-action=ignore "$(find target/wheels -name '*.whl' | head -n 1)"

# Set the default command for the container
CMD ["/bin/bash"]

