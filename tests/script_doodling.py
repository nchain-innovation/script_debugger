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


