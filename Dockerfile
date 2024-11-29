# Base image with Python
FROM rust:latest as base

ENV PYTHONUNBUFFERED 1
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

# Install Rust
#RUN curl https://sh.rustup.rs -sSf | sh -s -- -y \
#    && echo 'source $HOME/.cargo/env' >> ~/.bashrc

# Set environment variables
ENV VIRTUAL_ENV=/venv
ENV PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python3 -m venv $VIRTUAL_ENV \
    && $VIRTUAL_ENV/bin/pip install --upgrade pip \
    && $VIRTUAL_ENV/bin/pip install maturin

# Clone the GitHub repository
WORKDIR /app
RUN git clone https://github.com/nchain-innovation/chain-gang.git
    
WORKDIR /app/chain-gang 
RUN maturin build --release --out target/wheels \
    && $VIRTUAL_ENV/bin/pip install --root-user-action=ignore "$(find target/wheels -name '*.whl' | head -n 1)" 


WORKDIR /app/src
COPY ./src/* .

WORKDIR /app/python/src
COPY ./python/src/* . 
# RUN pip3 install -r requirements.txt

WORKDIR /app
COPY ./cargo.toml Cargo.toml
COPY ./requirements.txt requirements.txt
FROM base as release

WORKDIR /app

COPY ./examples/* ./examples/
RUN maturin build --release --out target/wheels \
    && $VIRTUAL_ENV/bin/pip install --root-user-action=ignore "$(find target/wheels -name '*.whl' | head -n 1)"

# Set the default command for the container
CMD ["/bin/bash"]

