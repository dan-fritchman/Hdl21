//!
//! # Hdl21 Python Bindings
//!

use pyo3::exceptions::RuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use pyo3::{PyErr, PyResult};


// Note "hdl21" must be the name of the `.so` or `.pyd` file,
// i.e. it must be the `package` and/or `lib` name in Cargo.toml

#[pymodule]
fn hdl21(_py: Python, m: &PyModule) -> PyResult<()> {
    /// "Health Check"
    #[pyfn(m, "health")]
    fn health_py(_py: Python) -> PyResult<String> {
        Ok("alive".to_string())
    }
    Ok(())
}
