import pytest


def test_public_names_importable():
    import beanpicker

    assert beanpicker.MobilityDatabase is not None
    assert beanpicker.Feed is not None
    assert beanpicker.Dataset is not None
    assert beanpicker.fetch is beanpicker.pipeline.fetch
    assert beanpicker.FetchResult is beanpicker.pipeline.FetchResult


def test_exceptions_hierarchy():
    import beanpicker
    from beanpicker.exceptions import (
        BeanpickerError,
        DownloadError,
        MissingTokenError,
    )

    assert issubclass(MissingTokenError, BeanpickerError)
    assert issubclass(DownloadError, BeanpickerError)
    assert beanpicker.exceptions.BeanpickerError is BeanpickerError


def test_unknown_attribute():
    import beanpicker

    with pytest.raises(AttributeError):
        beanpicker.does_not_exist


def test_version():
    pytest.importorskip("beanpicker._core")
    import beanpicker

    assert beanpicker.__version__
