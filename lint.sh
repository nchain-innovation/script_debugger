#!/bin/bash
# Lint everything. Any failure fails the script.
set -e

flake8 --ignore=E501,E131,E402,E722 python/src tests

mypy --check-untyped-defs --ignore-missing-imports python/src

cargo fmt --check
cargo clippy --no-default-features --all-targets -- -D warnings
