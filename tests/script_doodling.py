import os
from tx_engine import Script, Stack
from tx_engine.engine.op_codes import OP_16, OP_PUSHDATA1, OP_AND
from tx_engine.engine import context

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

    hexval:str = jpeg_to_hex("/Users/j.murphy/Downloads/spaceship-launch.jpg")
    #print(hexval)
    #print(len(hexval))
    large_num: int = 10000000000000
    large_num_res: int = 20000000000000
    #binval: bytes = load_jpeg("/Users/j.murphy/Downloads/spaceship-launch.jpg")
    script2 = Script.parse_string(hexval)
    script2 += Script.parse_string("OP_DROP")
    # script2 = Script()
    script2.add_big_integer(large_num)
    script2 += Script.parse_string("OP_DUP OP_ADD")
    script2.add_big_integer(large_num_res)
    script2 += Script.parse_string("OP_EQUAL")
    print(script2)

    con = context.Context(script=script2)
    if con.evaluate():
        print(con.get_stack())
        print("Success")
    else:
        print("failure")

'''
    sig_string_new = "3046022100f90d26a7e1fe457a8dc24bd6ae37caa0cb9af497ce693008a6f98a67cc803915022100e7f2ed97653413ad67a67ab09f695acd06d72b589dffbd33e8c7c5bea5714eb6"
    pub_key_new = "0427cbe3affbd481f66639afbbfcc1c540c4f2db2e04b436f44b04116261a3eadca57def58934127878178d25207651d04f585cdaa938c534db8290d19ccacc3d2"
    message_new = "ab530a13e45914982b79f9b7e3fba994cfd1f3fb22f71cea1afbf02b460c6d1d"

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
