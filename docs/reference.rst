.. _reference:

API reference
=============

:func:`~beanpicker.fetch` is the main entry point: it runs the whole
acquisition pipeline for an area of interest and returns a
:class:`~beanpicker.FetchResult`. Every stage is also available on its own —
the catalog client, the OSM fetcher, and the validate/repair/crop functions.

The pipeline
------------

.. currentmodule:: beanpicker

.. autosummary::
   :toctree: api/

   fetch
   FetchResult
   FetchResult.to_cafein
   FetchResult.to_pyrosm

The feed catalog
----------------

.. autosummary::
   :toctree: api/

   MobilityDatabase
   MobilityDatabase.search_feeds
   MobilityDatabase.feed
   MobilityDatabase.datasets
   MobilityDatabase.dataset_for
   MobilityDatabase.download
   MobilityDatabase.download_latest
   MobilityDatabase.validation_report
   MobilityDatabase.close
   Feed
   Dataset

OSM extracts
------------

.. autosummary::
   :toctree: api/

   fetch_pbf

Validation, repair and cropping
-------------------------------

.. autosummary::
   :toctree: api/

   validate_feed
   repair_feed
   crop_feed

Reporting
---------

.. currentmodule:: beanpicker.report

.. autosummary::
   :toctree: api/

   build_report
   parity_summary
   render_markdown
   render_html

Exceptions
----------

.. currentmodule:: beanpicker.exceptions

.. autosummary::
   :toctree: api/

   BeanpickerError
   MissingTokenError
   DownloadError
   ExtractNotFoundError
