# Installation

beanpicker requires Python >= 3.10.

## From PyPI

*(coming with the first release)*

```
pip install beanpicker
```

Binary wheels ship for Linux, macOS and Windows, so no Rust toolchain is
needed.

## From source

A source build compiles the Rust core, so a [Rust
toolchain](https://rustup.rs/) must be installed:

```
git clone https://github.com/cafein-py/beanpicker.git
cd beanpicker
pip install .
```

## Optional pieces

- **Mobility Database API token** — a free
  [Mobility Database](https://mobilitydatabase.org/) refresh token unlocks
  historical dataset selection, checksum-verified versioned downloads and the
  hosted canonical-validator reports. Pass it as `refresh_token=` or set the
  `MOBILITY_API_REFRESH_TOKEN` environment variable. Without one, beanpicker
  transparently falls back to the public CSV catalogue and the latest hosted
  feed zips (unverified moving targets).
- **cafein** — needed only for `FetchResult.to_cafein()`.

## Verifying the installation

```python
import beanpicker

print(beanpicker.__version__)
```
