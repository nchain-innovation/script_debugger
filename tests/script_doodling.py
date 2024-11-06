import os 
import sys
from tx_engine import Script, Stack, opcode_index
from tx_engine.engine.op_codes import OP_16, OP_PUSHDATA1, OP_AND
from tx_engine.engine import context

sys.path.append("../src")
from debug_interface import DebuggerInterface

def main() -> None:
    print('starting')
    as_str1 = "OP_PUSHDATA1 0x02 0x01f0 OP_PUSHDATA1 0x02 0x0010 OP_AND"
    script1 = Script.parse_string(as_str1)

    print(script1)

    pass
def jpeg_to_hex(file_path: str) -> str: 
    with open(file_path, 'rb') as f:
        binary_data = f.read()
    
    return '0x' + binary_data.hex()


def load_jpeg(file_path) -> bytes:
    with open(file_path, 'rb') as f:
        binary_data = f.read()
    return binary_data

if __name__ == "__main__":
    #main()

    #hexval:str = jpeg_to_hex("/Users/j.murphy/Downloads/spaceship-launch.jpg")
    #print(hexval)
    #print(len(hexval))
    #large_num: int = 10000000000000
    #large_num_res: int = 20000000000000
    #binval: bytes = load_jpeg("/Users/j.murphy/Downloads/spaceship-launch.jpg")
    #script2 = Script.parse_string(hexval)
    #script2 += Script.parse_string("OP_DROP")
    # script2 = Script()
    #script2.add_big_integer(large_num)
    #script2 += Script.parse_string("OP_DUP OP_ADD")
    #script2.add_big_integer(large_num_res)
    #script2 += Script.parse_string("OP_EQUAL")
    #print(script2)

    #con = context.Context(script=script2)
    #if con.evaluate():
    #    print(con.get_stack())
    #    print("Success")
    #else:
    #    print("failure")


    #dbif = DebuggerInterface()
    #dbif.set_noisy(False)
    #assert(dbif.db_context.ip is None)
    ##dbif.process_input(["file", "../examples/add.bs"])

    #dbif.process_input(["s"])
        #self.assertIsNotNone(self.dbif.db_context.ip)
    #assert(dbif.db_context.get_stack() == Stack([[1]]))
    #assert(dbif.db_context.ip == 1)

    #dbif.process_input(["step"])
    #assert(dbif.db_context.get_stack() == Stack([[1], [2]]))
    #assert(dbif.db_context.ip == 2)

    #dbif.process_input(["step"])
    #assert(dbif.db_context.get_stack() ==Stack([[3]]))
    #assert(dbif.db_context.ip == 3)


    #let script = vec![OP_PUSHDATA4, 0x04, 0x00, 0x00, 0x00, 0xaa, 0xbb, 0xcc, 0xdd,OP_PUSHDATA4, 0x04, 0x00, 0x00, 0x00, 0xaa, 0xbb, 0xcc, 0xdd, OP_ADD, OP_PUSHDATA4, 0x05, 0x00, 0x00, 0x00, 0x00, 0x55, 0x77, 0x99, 0xba, OP_EQUAL];
    #assert_eq!(find_op_locations(&script), vec![0,9,18,19,29]);
    # OP_ADD OP_PUSHDATA4 0x05000000 0x00557799ba OP_EQUALVERIFY
    script_test:Script = Script.parse_string("OP_PUSHDATA4 0x04000000 0xaabbccdd OP_PUSHDATA4 0x04000000  0xaabbccdd OP_ADD  OP_PUSHDATA4 0x05000000 0x00557799ba OP_EQUAL") 
    print(script_test)
    print(opcode_index(script_test))
    #op_code_idx = opcode_index(script_test)
    #assert(op_code_idx == [0,9,18,19,29])
    #con_push_test = context.Context(script=script_test)
    #con_push_test.evaluate()
    #print(con_push_test.get_stack())

    #dbif = DebuggerInterface()
    #dbif.set_noisy(False)
    #assert(dbif.db_context.sf.instruction_count is None)
    #dbif.process_input(["file", "../examples/push_data_for_debugger.bs"])
    #dbif.process_input(["file", "../examples/integer_to_script.bs"])
    #dbif.process_input(["list"])
    #print(f'Instruction offset -> {dbif.db_context.sf.script_state.instruction_offset}')

    #print(dbif.db_context.sf.script_state.script)

    #dbif.process_input(["run"])
    #print(dbif.db_context.get_stack())

    #print('step 1')
    #dbif.process_input(["step"])
    #print(dbif.db_context.get_stack())
    #print(f'Instruction offset -> {dbif.db_context.sf.script_state.instruction_offset}')
    #input()

    #print(f'Instruction Count after 1st Step {dbif.db_context.sf.instruction_count}')
    #print(f'instruction index for next step {dbif.db_context.sf.script_state.instruction_offset[dbif.db_context.sf.instruction_count]}')

    #print('step 2')
    #dbif.process_input(["step"])
    #print(dbif.db_context.get_stack())
    #input()
    ##print(f'Instruction offset -> {dbif.db_context.sf.script_state.instruction_offset}')

    #print(f'instruction index for next step {dbif.db_context.sf.script_state.instuction_offset[dbif.db_context.sf.instruction_count]}')
    ##print(f'Instruction Count after 2nd Step {dbif.db_context.sf.instruction_count}')
    #print('step 3')
    #dbif.process_input(["step"])
    #print(f'Instruction offset -> {dbif.db_context.sf.script_state.instruction_offset}')
    ##print(dbif.db_context.get_stack())
    #input()

    #print('step 4')
    #dbif.process_input(["step"])
    #print(dbif.db_context.get_stack())
    #print(f'Instruction offset -> {dbif.db_context.sf.script_state.instruction_offset}')
    #input()

    #print('step 5')
    #dbif.process_input(["step"])
    #print(dbif.db_context.get_stack())
    #print(f'Instruction offset -> {dbif.db_context.sf.script_state.instruction_offset}')
    #input()

    script_push = Script.parse_string("0x01 OP_PUSHDATA1 0x02 0xaabb 0x02"); 
    # script_push = Script.parse_string("OP_10 OP_PUSHDATA1 0x02 0xaabb 0x02 0xaabbcc"); 
    op_code_locs = opcode_index(script_push)
    print(script_push)
    print(op_code_locs)
    #assert(op_code_locs == [0, 1]);
    con_test = context.Context(script=script_push)
    con_test.evaluate()
    print(con_test.get_stack())


    print("TESTING INTEGERS")
    script_integers = Script.parse_string("2555 2555 OP_EQUALVERIFY"); 
    # script_push = Script.parse_string("OP_10 OP_PUSHDATA1 0x02 0xaabb 0x02 0xaabbcc"); 
    op_code_locs = opcode_index(script_integers)
    print(script_integers)
    print(op_code_locs)
    #assert(op_code_locs == [0, 1]);
    con_test = context.Context(script=script_integers)
    con_test.evaluate()
    print(con_test.get_stack())

'''
    sig_string_new = "3046022100f90d26a7e1fe457a8dc24bd6ae37caa0cb9af497ce693008a6f98a67cc803915022100e7f2ed97653413ad67a67ab09f695acd06d72b589dffbd33e8c7c5bea5714eb6"
    pub_key_new = "0427cbe3affbd481f66639afbbfcc1c540c4f2db2e04b436f44b04116261a3eadca57def58934127878178d25207651d04f585cdaa938c534db8290d19ccacc3d2"
    message_new = "ab530a13e45914982b79f9b7e3fb a994cfd1f3fb22f71cea1afbf02b460c6d1d"

    # create a script
    script_exe: Script = Script()
    sig_for_script: bytes = bytes.fromhex(sig_string_new) + bytes.fromhex("41")

    script_exe.append_pushdata(sig_for_script)  
    script_exe.append_pushdata(bytes.fromhex(pub_key_new))
    script_exe = script_exe + Script.parse_string(' OP_CHECKSIG')
    context_failure = context.Context(script=script_exe)
    context_failure.z = bytes.fromhex(message_new)
    print(f'Context value -> {context}')
    ret: bool = context_failure.evaluate()
    if ret:
        print('Expected failure but got a sucess with an OP_CHECKSIG.. boo!')
    else:
        print('expected failed received for OP_CHECKSIG')


    script_test: Script = Script.parse_string("1 2 OP_ADD 4 OP_EQUAL")
    test_con = context.Context(script=script_test)
    test_ret: bool = test_con.evaluate()
    #print(f'printing the stack -> {test_con.get_stack()}')
    if test_ret:
        print('Success .. boo')
    else:
        print('Failure .. hurra')
    
    script_test_good: Script = Script.parse_string("1 2 OP_ADD 3 OP_EQUAL")
    test_con_good = context.Context(script=script_test_good)
    test_ret_good: bool = test_con_good.evaluate()
    print(test_con_good.get_stack())
    if test_ret_good:
        print('Success .. hurrah')
    #else:
        print('Failure .. boo')

    script = Script([OP_PUSHDATA1, 0x02, b"\x00\x01", OP_PUSHDATA1, 0x02, b"\x00\x03", OP_AND])
    cont = context.Context(script=script)
    #self.assertTrue(context.evaluate_core())
    print(f'{cont.get_stack()}')
    test_val = cont.evaluate_core()
    print(f'{cont.get_stack()}')
    #test_stack: Stack = Stack.single_from_array_bytes([0, 1])
    test_stack: Stack = Stack([[0,1]])
    # test_stack.push([0,1])
    print(test_stack)
    assert(test_stack == cont.get_stack())
'''
