# script_debugger
This project provides nChain with a gdb style debugger for bitcoin script. 


* `dbg` - Bitcoin Script debugger, this provides a GDB style interface to run, step through and set breakpoints in Metascript and canonical script programs.



These tools are built around a BSV bitcoin script engine written in Rust. 


# Running the debuuger 
The project tools can be run from Docker or Python on the commandline as long as the associated dependencies are met. To debugger includes a script parser that is written using a combination of Rust (Pest crate) for Parser Expression Grammer and python. To build please follow the steps below. Pleae note Rust and Maturin must be installed. And you must have a python virtual environment such as penv set up correctly.

### 
```bash
maturin build
pip3 install --force-reinstall "$(find target/wheels -name '*.whl' | head -n 1)"
```

## To run from the commandline
```bash
python3 python/src/dbg.py -file ./examples/large_data_push_integer_test.bs
```


# Using Docker

The debugger in this project can be run in a Docker instance. The build the container:
```bash
./build.sh
```

To run the debugger in the docker container.
```bash
./run_dbg.sh ./examples/large_integer_test.bs
```

Please note that Bitcoin Script files must have a '.bs' file extension.



