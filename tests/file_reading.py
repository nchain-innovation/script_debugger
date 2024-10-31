import sys
import tx_engine
sys.path.append("../src")
from debug_interface import DebuggerInterface

def main(file_name: str):
    print('starting')
    dbif = DebuggerInterface()
    dbif.load_script_file(file_name)
    
    print(dbif.db_context.sf.script_state.script)
    #print(type(dbif.db_context.sf.script_state.script))

    #script_test: tx_engine.Script = tx_engine.Script.parse_string("0x00a0724e1809 OP_DUP OP_ADD 0x0040e59c3012 OP_EQUALVERIFY")
    #print(script_test)

    dbif.db_context.list()
    #dbif.db_context.reset()
    # len(self.context.cmds)
    #dbif.db_context.run()
    #print(dbif.db_context.get_stack())
    if dbif.db_context.sf.ip is None:
        dbif.db_context.sf.ip = 0
    while (dbif.db_context.can_run()):
        dbif.db_context.step()
    print(dbif.db_context.get_stack())
if __name__ == "__main__":
    file_name: str = "/Users/j.murphy/nchain/github-innovation/script_debugger/examples/large_data_push_integer_test.bs"
    main(file_name)
