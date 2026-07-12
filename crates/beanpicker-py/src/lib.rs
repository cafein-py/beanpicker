use pyo3::prelude::*;

/// Native core of beanpicker: GTFS parsing, validation, repair and cropping
/// arrive here in Phase 2; for now the crate only pins the package version.
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
