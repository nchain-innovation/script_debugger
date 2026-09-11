# Examples

This directory contains example bitcoin script files for the debugger. Some of
them are used by the unit tests in `tests/test_debugger.py`.

| File | Description |
|---|---|
| `add.bs` | Put 1 and 2 on the stack and add them together. |
| `divide_by_two.bs` | Divide 7 by 2. |
| `swap.bs` | Put three values on the stack and swap the top two over. |
| `integer_to_script.bs` | Various integer operations. |
| `longer_op_codes.bs` | `integer_to_script.bs` followed by `OP_1ADD` / `OP_1SUB`. |
| `long_opcodes_test.bs` | The opcodes whose mnemonics contain a digit. |
| `verify_op_code_tests.bs` | `OP_NUMEQUALVERIFY` on its own. |
| `large_integer_test.bs` | Large integer operations using raw hex pushes. |
| `large_data_push_integer_test.bs` | A large `OP_PUSHDATA4` push followed by integer operations. |
| `push_data.bs` | A single large raw data push. |
| `push_data_for_debugger.bs` | `OP_PUSHDATA4` pushes, added and compared. |
| `pushdata_tests.bs` | `OP_PUSHDATA1`, `OP_PUSHDATA2` and `OP_PUSHDATA4`. |
| `single_opif.bs` | An empty conditional: `OP_IF OP_ENDIF`. |
| `not_nested_if.bs` | Two sequential, non-nested conditionals. |
| `nested_ifs.bs` | A conditional nested inside another conditional. |
