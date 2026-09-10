//! Bitcoin script parser.
//!
//! The parsing itself lives in [`parser`] and has no Python dependency, so it
//! can be built and tested with `cargo test --no-default-features`. The
//! `python` feature (on by default) adds the `pyo3` extension module the
//! debugger imports.

pub mod parser;

pub use parser::{parse_script, OpcodeInfo, ParseError, Rule, ScriptParser};

#[cfg(feature = "python")]
// pyo3 0.22's `#[pyfunction]` expansion contains a `PyErr -> PyErr` conversion
// that clippy reports against the wrapped function's signature. There is
// nothing to fix in this module's own code.
#[allow(clippy::useless_conversion)]
mod python {
    use pyo3::exceptions::PyValueError;
    use pyo3::prelude::*;
    use pyo3::types::PyList;

    /// Parse `script_str` and return `[(opcode, byte_offset), ...]`.
    ///
    /// Raises `ValueError` on malformed script. Nothing here may panic: a
    /// panic unwinding into CPython surfaces as `pyo3_runtime.PanicException`
    /// with a Rust backtrace, which is not something a debugger user can act
    /// on.
    #[pyfunction]
    fn parse_script(py: Python<'_>, script_str: &str) -> PyResult<Py<PyList>> {
        let opcodes = crate::parser::parse_script(script_str)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;

        let list = PyList::new_bound(
            py,
            opcodes.into_iter().map(|info| (info.opcode, info.position)),
        );
        Ok(list.unbind())
    }

    #[pymodule]
    #[pyo3(name = "bitcoin_script_parser")]
    fn bitcoin_script_parser(m: &Bound<'_, PyModule>) -> PyResult<()> {
        m.add_function(wrap_pyfunction!(parse_script, m)?)?;
        Ok(())
    }
}
