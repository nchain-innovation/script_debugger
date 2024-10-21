import os
from tx_engine import Script
from tx_engine.engine.op_codes import OP_16
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
    #script2 = Script()
    script2.add_big_integer(large_num)
    script2 += Script.parse_string("OP_DUP OP_ADD")
    script2.add_big_integer(large_num_res)
    script2 += Script.parse_string("OP_EQUAL")
    print(script2)

    con = context.Context(script=script2)
    if con.evaluate():
        print("Success")
    else:
        print("failure")

    #script3 = Script.parse_string("1 2 16 -2 -2456 2678 OP_1 OP_16")
    #print(script3)

    #script4 = Script()
    #script4.append_data(1)
    #script4.append_data(2)
    #script4.append_data(16)
    #script4 += Script(OP_16)
    #print(script4)

    #num: int = 5
    #number_script: Script = Script()
    #number_script.append_byte(num)
    #print(number_script)
    #big_num: int = 1000000000
    #number_script.append_data(big_num)
    #print(number_script)


    #large_num: int = 10000000000000
    #large_num_res: int = 20000000000000
    #number_script.add_big_integer(large_num)
    #print(number_script)
    #number_script += Script.parse_string("OP_DUP OP_ADD")
    #number_script.add_big_integer(large_num_res)
    #number_script += Script.parse_string("OP_EQUALVERIFY")
    #print(number_script)


    
'''
Would this work:

OP_PUSHDATA1 MOP_SIZE1 <DATA> (user would write this either in a file or in the constructor of the script)
-> AFTER the OP_PUSHDATA1 the chain_gang interpreter will check for MOP_SIZE1
-> This will then take the next value (which will be the data) 
-> Push the size in 1 byte (checking to ensure it fits into 1 byte)
-> Push the <DATA> so the real script will result in 
OP_PUSHDATA1 <1 Byte indicating the size of the DATA> <DATA>


OR

<DATA> 
-> Either the script constructor or the parse_string class method should return

OP_PUSHDATA_X <SIZE> <DATA> 

'''