"""The one-call pipeline: AOI + date -> OSM extract + validated feeds."""

from beanpicker.pipeline._fetch import FetchResult, fetch

__all__ = ["FetchResult", "fetch"]
