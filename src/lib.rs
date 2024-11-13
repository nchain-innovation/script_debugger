use core::fmt;
use pyo3::prelude::*;
use pyo3::types::PyList;
use pest::Parser;
use pest_derive::Parser;

#[derive(Parser)]
#[grammar = "script.pest"] // Path to your grammar file
pub struct ScriptParser;

// define a struct to hold opcode information
#[derive(Debug)]
pub struct OpcodeInfo{
    opcode: String, 
    position: usize
}

impl fmt::Display for OpcodeInfo{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "OpCode: {}, Position: {}", self.opcode, self.position)
    }
}

fn parse_statements(script_pair: pest::iterators::Pair<Rule>) -> Vec<OpcodeInfo>{
    let mut opcode_positions = vec![]; 
    let mut byte_offset = 0; 

    for statement in script_pair.into_inner(){
        match statement.as_rule(){
            Rule::statement => {
                for inner_pair in statement.into_inner(){
                    match inner_pair.as_rule(){
                        Rule::opcode => {
                            let opcode = OpcodeInfo {
                                                        opcode: inner_pair.as_str().to_string(), 
                                                        position: byte_offset,//position: inner_pair.as_span().start()
                                                    } ;
                            opcode_positions.push(opcode);
                            byte_offset += 1;
                        }
                        Rule::data => {
                            if inner_pair.as_str().starts_with("0x") {
                                let hex_len = (inner_pair.as_str().len() - 2) / 2; // Length in bytes
                                byte_offset += hex_len;
                            } else {
                                // not sure about this one
                                byte_offset += inner_pair.as_str().len();
                            }
                             
                        }
                        _ => {}, // this picks up whitespace
                    }
                }
            }
            Rule::EOI => (),
            _ => unreachable!(),
        }
    }
    opcode_positions
}

/// pyo3 wrapper functions.
///
#[pyfunction]
fn parse_script(py: Python, script_str: &str) -> PyResult<Py<PyList>>{
    let parse_result = ScriptParser::parse(Rule::script, script_str);
    match parse_result {
        Ok(mut pairs)=> {
            let script_pair = pairs.next().unwrap();
            let opcodes_info = parse_statements(script_pair);
            let empty_list =  PyList::new_bound(py, opcodes_info
                                                    .into_iter()
                                                    .map(|info| (info.opcode, info.position)));
            Ok(empty_list.into())
        }
        Err(e) => {
            let err_msg = format!("Parsing error: {}", e);
            Err(pyo3::exceptions::PyValueError::new_err(err_msg))        
        }
    }
}

// Define the Python module

#[pymodule]
#[pyo3(name = "bitcoin_script_parser")]
fn bitcoin_parser(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_script, m)?)?;
    Ok(())
}
