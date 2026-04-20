use pyo3::prelude::*;

/// Placeholder module. Sprint 2+ 會加幾何計算熱點函式（polygon ops, BVH）。
#[pymodule]
fn rust_geometry(_py: Python, _m: &Bound<'_, PyModule>) -> PyResult<()> {
    Ok(())
}
