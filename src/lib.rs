use core::fmt;
use pest::Parser;
use pest_derive::Parser;
use pyo3::prelude::*;
use pyo3::types::PyList;

#[derive(Parser)]
#[grammar = "script.pest"] // Path to your grammar file
pub struct ScriptParser;

// define a struct to hold opcode information
#[derive(Debug)]
pub struct OpcodeInfo {
    opcode: String,
    position: usize,
}

impl fmt::Display for OpcodeInfo {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "OpCode: {}, Position: {}", self.opcode, self.position)
    }
}

fn parse_statement(pair: pest::iterators::Pair<Rule>, byte_offset: &mut usize) -> Vec<OpcodeInfo> {
    let mut opcodes = Vec::new();
    match pair.as_rule() {
        Rule::statement => {
            let inner = pair.into_inner();
            for subpair in inner {
                // Recursive descent
                opcodes.extend(parse_statement(subpair, byte_offset)); // Collect results from recursion
            }
        }
        Rule::opcode => {
            opcodes.push(OpcodeInfo {
                opcode: pair.as_str().to_string(),
                position: *byte_offset, 
            });
            *byte_offset += 1; 
        }
        Rule::data => {
            if pair.as_str().starts_with("0x") {
                let hex_len = (pair.as_str().len() - 2) / 2;
                *byte_offset += hex_len;
            } else {
                *byte_offset += pair.as_str().len();
            }
        }
        // For if_statement, process each inner pair.
        Rule::if_statement => {
            for inner_pair in pair.into_inner() {
                let text = inner_pair.as_str().trim(); 
                if inner_pair.as_rule() == Rule::if_token ||
                    inner_pair.as_rule() == Rule::else_token ||
                    inner_pair.as_rule() == Rule::endif_token{
                        opcodes.push(OpcodeInfo {
                            opcode: text.to_string(),
                            position: *byte_offset
                        });
                        *byte_offset += 1; 
                } else {
                    opcodes.extend(parse_statement(inner_pair, byte_offset));
                }
            }
        }
        Rule::EOI => {
            println!("End of Input reached");
        }
        _ => {
            panic!("Unexpected rule in parse_statement: {:?}", pair.as_rule());
        }
    }
    opcodes
}
/// pyo3 wrapper functions.
///
#[pyfunction]
fn parse_script(py: Python, script_str: &str) -> PyResult<Py<PyList>> {
    let parse_result = ScriptParser::parse(Rule::script, script_str).expect("Failed to parse nested if script");
    let script_pair = parse_result.into_iter().next().expect("Expected a script rule");
    let mut opcodes = Vec::new(); 
    let mut byte_offset = 0; 
    for pair in script_pair.into_inner(){ // unwrapping script
        //parsed_statements.push(parse_statement(pair));
        opcodes.extend(parse_statement(pair, &mut byte_offset)); 
    }

    let empty_list = PyList::new_bound(
        py,
        opcodes
            .into_iter()
            .map(|info| (info.opcode, info.position)),
    );
    Ok(empty_list.into())
}

// Define the Python module

#[pymodule]
#[pyo3(name = "bitcoin_script_parser")]
fn bitcoin_parser(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_script, m)?)?;
    Ok(())
}
