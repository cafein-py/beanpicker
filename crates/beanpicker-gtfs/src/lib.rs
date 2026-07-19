//! GTFS ingest and validation core: parses a feed zip into raw tables while
//! collecting notices under the canonical gtfs-validator code convention,
//! instead of failing hard on the first defect.

pub mod notice;
pub mod scan;
pub mod schema;

pub use notice::{Notice, Severity};
pub use scan::{
    scan, scan_reader, scan_reader_with, scan_with, ScanOptions, ScanResult, Table,
    DEFAULT_MAX_COLUMNS, DEFAULT_MAX_ENTRY_BYTES, DEFAULT_MAX_ROWS, DEFAULT_MAX_TOTAL_BYTES,
};
