"""AOI-driven OSM and GTFS acquisition, validation and repair."""

__all__ = ["Dataset", "Feed", "MobilityDatabase", "exceptions", "__version__"]


def __getattr__(name):
    if name in ("Dataset", "Feed", "MobilityDatabase"):
        from beanpicker import catalog

        return getattr(catalog, name)
    if name == "exceptions":
        from beanpicker import exceptions

        return exceptions
    if name == "__version__":
        from beanpicker._core import __version__

        return __version__
    raise AttributeError(f"module 'beanpicker' has no attribute {name!r}")
