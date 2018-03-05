import pytest
from re import escape as esc
from wavy.detail import *
from wavy import *


class MockEmptyClass(object):
    """
    Test file is opened when string is passed.
    """
    pass


def test_get_file_from_arg_with_string(mocker):
    """
    Test file is opened when string is passed.
    """
    open_fct = mocker.patch('builtins.open', return_value=MockEmptyClass())
    res = get_stream_from_file('foo', 'rb', MockEmptyClass)
    assert isinstance(res, MockEmptyClass)
    open_fct.assert_called_with('foo', 'rb')


def test_get_file_from_arg_with_object():
    """
    Test object is returned if it's of the expected type.
    """
    res = get_stream_from_file(MockEmptyClass(), 'rb', MockEmptyClass)
    assert isinstance(res, MockEmptyClass)


def test_get_file_from_arg_with_wrong_type():
    """
    Test exception is raise when object is not of expected types.
    """
    with pytest.raises(WaveFileNotSupported, match=esc(
            "'file' argument must be a string or <MockEmptyClass> instance, "
            "<class 'int'> given instead.")):
        get_stream_from_file(10, 'rb', MockEmptyClass)
