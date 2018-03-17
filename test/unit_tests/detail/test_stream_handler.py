import numpy
import pytest
import struct
from wavy.detail import *


@pytest.mark.parametrize('le, prefix', [
    (False, '>'), (True, '<')
])
def test_stream_handler(le, prefix):
    """
    Test that StreamHandler is build correctly
    """
    handler = StreamHandler(le)
    assert handler.little_endian == le
    assert handler.endian_prefix == prefix


@pytest.mark.parametrize('le, prefix', [
    (False, '>'), (True, '<')
])
def test_stream_handler_read(le, prefix, mocker):
    """
    Test that StreamHandler is build correctly
    """
    unpack = mocker.patch('struct.unpack_from', return_value='data')
    handler = StreamHandler(le)
    assert handler.read('LLL', 'stream', 10) == 'data'
    unpack.assert_called_with(prefix + 'LLL', 'stream', 10)
    assert handler.read('LLL', 'stream') == 'data'
    unpack.assert_called_with(prefix + 'LLL', 'stream', 0)


@pytest.mark.parametrize('n_bytes, expected_dtype', [
    (1, 'u1'),
    (2, 'i2'),
    (4, 'i4'),
    (8, 'i8')
])
def test_stream_handler_read_data_simple_type(n_bytes, expected_dtype, mocker):
    """
    Test that StreamHandler reads data correctly for 8, 16, 32, and 64 bit
    """
    # set up mocks
    fromstring = mocker.patch('numpy.fromstring', return_value='data')
    stream = mocker.MagicMock()
    stream.read.return_value = 'raw_data'

    for le in [True, False]:
        handler = StreamHandler(le)
        assert handler.read_data(stream, 10, n_bytes) == 'data'

        prefix = '<' if le else '>'
        fromstring.assert_called_with('raw_data', dtype=prefix + expected_dtype)
        stream.read.assert_called_with(10)


@pytest.mark.parametrize('le, n_bytes', [
    (True, 3), (False, 3),
    (True, 6), (False, 6)
])
def test_stream_handler_read_data_complex_type(le, n_bytes, mocker):
    """
    Test that StreamHandler reads data correctly for 24 and 48 bit
    """
    # set up mocks
    array = mocker.patch('numpy.array', return_value='data')
    stream = mocker.MagicMock()
    # 10 in int 24
    padding = (n_bytes - 1) * b'\x00'
    stream.read.return_value = b'\n' + padding if le else padding + b'\n'

    handler = StreamHandler(le)
    assert handler.read_data(stream, 2 * n_bytes, n_bytes) == 'data'

    array.assert_called_with([10, 10])
    stream.read.assert_has_calls([mocker.call(n_bytes),
                                  mocker.call(n_bytes)])
