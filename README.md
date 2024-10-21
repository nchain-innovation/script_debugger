# script_debugger
This project provides nChain with a gdb style debugger for bitcoin script. 


* `Debugger` - Metascript debugger, this provides a GDB style interface to run, step through and set breakpoints in Metascript and canonical script programs.



These tools are built around a BSV bitcoin script engine written in Python. The script engine is derived from source code found in the book: "Programming Bitcoin by Jimmy Song (O'Reilly). Copyright 2019 Jimmy Song, 978-1-492-03149-4". 

It is included via a submodule.


# Syntax Highlighting
Microsoft Visual Studio Code TDL, SDL and Metascript syntax highlighting is provided by the `vscode-sdl` project.

This can be found in the [SDL VS Code project](https://bitbucket.stressedsharks.com/projects/SDL/repos/vscode-sdl/browse)

# Running the debuuger 
The project tools can be run from Docker or Python as long as the associated dependencies are met. 


# Using Docker

The tools in this project can be run in a Docker instance.



# Pulling the git submodule tx_engine
Please note that whenever you are cloning a git repository that has a submodule, there is an extra command to execute in order for the submodules to be pulled.  Once the project directory has been cloned, please execute 

git submodule update --init --recursive
