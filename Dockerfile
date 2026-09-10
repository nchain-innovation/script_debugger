# Build image for the bitcoin script debugger.
#
# rust:1-trixie ships Debian trixie, whose python3 is 3.13 — the newest
# CPython pyo3 0.22 supports. Pinning matters: on a newer interpreter the pyo3
# build script refuses to run.
FROM rust:1-trixie AS base

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/London
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    python3-setuptools \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages --no-cache-dir \
    maturin \
    setuptools-rust \
    setuptools \
    wheel \
    tx_engine

WORKDIR /app
COPY ./Cargo.toml ./Cargo.toml
COPY ./requirements.txt ./requirements.txt
COPY ./src/ ./src/
COPY ./python/src/ ./python/src/

FROM base AS release

WORKDIR /app
COPY ./examples/ ./examples/

# There is no virtualenv in this image, so install into the system interpreter.
# The previous version invoked "$VIRTUAL_ENV/bin/pip", which expanded to
# /bin/pip because VIRTUAL_ENV was never set, and failed.
RUN maturin build --release --out target/wheels --interpreter python3 \
    && pip3 install --break-system-packages --no-cache-dir --root-user-action=ignore \
       "$(find target/wheels -name '*.whl' | head -n 1)"

CMD ["/bin/bash"]
