# script_debugger

This project provides nChain with a gdb-style debugger for bitcoin script.

* `dbg` — Bitcoin script debugger. It provides a GDB-style interface to run,
  step through, and set breakpoints in Metascript and canonical script
  programs.

These tools are built around a BSV bitcoin script engine written in Rust.

## Running the debugger

The tools can be run from Docker, or from Python on the command line as long
as the dependencies are met. The debugger includes a script parser written
with a combination of Rust (the [pest](https://pest.rs) crate, for the parsing
expression grammar) and Python.

To build it you need Rust and [maturin](https://www.maturin.rs) installed, and
an activated Python virtual environment (`python3 -m venv`, `pyenv`, or
similar).

```bash
maturin build
pip3 install --force-reinstall "$(find target/wheels -name '*.whl' | head -n 1)"
pip3 install -r requirements.txt
```

Note: pyo3 0.22 supports CPython up to 3.13. On a newer interpreter the build
fails unless you set `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1`, or upgrade pyo3.

### To run from the command line

```bash
python3 python/src/dbg.py -file ./examples/large_data_push_integer_test.bs
```

Bitcoin script files must have a `.bs` extension.

## Using Docker

To build the container:

```bash
./build.sh
```

To run the debugger in the container:

```bash
./run_dbg.sh ./examples/large_integer_test.bs
```

## Development

Run the Python and Rust linters:

```bash
./lint.sh
```

Run the tests. The Rust parser tests need no Python interpreter; the debugger
tests need the `bitcoin_script_parser` wheel installed (see above):

```bash
cargo test --no-default-features
python3 -m pytest tests
```
