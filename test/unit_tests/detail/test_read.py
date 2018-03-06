import chunk
import numpy
import pytest
from re import escape as esc
from wavy import *
from wavy.detail import *


def test_check_head_chunk(mocker):
    """
    Test head chunk is read correctly
    """
    # mock Chunk methods
    mocker.patch.object(chunk.Chunk, '__init__', return_value=None)
    mocker.patch.object(chunk.Chunk, 'getname', return_value=b'RIFF')
    # mock stream methods
    stream = mocker.MagicMock()
    stream.read.return_value = b'WAVE'

    check_head_chunk(stream)
    # check all called as expected
    chunk.Chunk.__init__.assert_called_with(stream, bigendian=False)
    chunk.Chunk.getname.assert_called_with()
    stream.read.assert_called_with(4)


def test_check_head_chunk_wrong_tag(mocker):
    """
    Test exception is raised when head tag has unknown type.
    """
    # mock Chunk methods
    mocker.patch.object(chunk.Chunk, '__init__', return_value=None)
    mocker.patch.object(chunk.Chunk, 'getname', return_value=b'FOOL')
    with pytest.raises(WaveFileNotSupported,
                       match=esc('File does not start with RIFF ID.')):
        check_head_chunk(None)


def test_check_head_chunk_wrong_type(mocker):
    """
    Test exception is raised when wave type tag has unknown type.
    """
    # mock Chunk methods
    mocker.patch.object(chunk.Chunk, '__init__', return_value=None)
    mocker.patch.object(chunk.Chunk, 'getname', return_value=b'RIFF')
    # mock stream methods
    stream = mocker.MagicMock()
    stream.read.return_value = b'BARB'
    with pytest.raises(WaveFileNotSupported,
                       match=esc('File does not appear to be a WAVE file.')):
        check_head_chunk(stream)


@pytest.mark.parametrize('fmt_names, chunk_size, format_tag, sub_format_tag', [
    # WAVE_FORMAT_PCM with allowed chunk sizes
    ([b'fmt ', ], 16, WAVE_FORMAT_PCM, 0),
    ([b'fmt ', ], 18, WAVE_FORMAT_PCM, 0),
    ([b'fmt ', ], 40, WAVE_FORMAT_PCM, 0),
    # make sure it finds chunk after others
    ([b'fmt ', b'bar', b'RIFF', b'foo'], 16, WAVE_FORMAT_PCM, 0),
    # cover WAVE_FORMAT_EXTENSIBLE for 24b PCM
    ([b'fmt ', ], 40, WAVE_FORMAT_EXTENSIBLE, WAVE_FORMAT_PCM)
])
def test_get_fmt_chunk(fmt_names, chunk_size, format_tag,
                       sub_format_tag, mocker):
    """
    Test head chunk is read correctly
    """
    read_list = [struct.pack('<H', sub_format_tag),
                 struct.pack('<HHLLHH', format_tag, 1, 2, 3, 4, 5)]
    # mock Chunk methods
    mocker.patch.object(chunk.Chunk, '__init__', return_value=None)
    mocker.patch.object(chunk.Chunk, 'getname',
                        side_effect=lambda: fmt_names.pop())
    mocker.patch.object(chunk.Chunk, 'getsize', return_value=chunk_size)
    mocker.patch.object(chunk.Chunk, 'read',
                        side_effect=lambda _: read_list[-1])
    mocker.patch.object(chunk.Chunk, 'seek',
                        side_effect=lambda _: read_list.pop())
    mocker.patch.object(chunk.Chunk, 'skip')

    assert get_fmt_chunk(None) == FormatInfo(WAVE_FORMAT_PCM, 1, 2, 3, 4, 5)
    # check all called as expected
    chunk.Chunk.__init__.assert_called_with(None, bigendian=False)
    chunk.Chunk.getname.assert_called_with()
    chunk.Chunk.getsize.assert_called_with()
    if format_tag == WAVE_FORMAT_PCM:
        chunk.Chunk.read.assert_called_with(16)
    else:
        chunk.Chunk.read.assert_has_calls([mocker.call(16),
                                           mocker.call(2)])
        chunk.Chunk.seek.assert_called_with(24)
        chunk.Chunk.seek.skip()


test_get_fmt_chunk_fail_args = 'fmt_names, chunk_size, format_tag, ' \
                               'sub_format_tag, exception_type, error_msg'


@pytest.mark.parametrize(test_get_fmt_chunk_fail_args, [
    # data before fmt
    ([b'fmt ', b'data'], 16, WAVE_FORMAT_PCM, 0,
     WaveFileIsCorrupted, 'Found data chunk before fmt chunk.'),
    # unsupported chunk size
    ([b'fmt ', ], 25, WAVE_FORMAT_PCM, 0,
     WaveFileIsCorrupted, 'Format chunk is of unexpected size: 25.'),
    # unsupported wFormatTag = WAVE_FORMAT_IEEE_FLOAT
    ([b'fmt ', ], 40, 0x0003, 0,
     WaveFileNotSupported, 'The wave format is not of supported type.'),
    # WAVE_FORMAT_EXTENSIBLE should have chunksize of 40
    ([b'fmt ', ], 18, WAVE_FORMAT_EXTENSIBLE, 0,
     WaveFileNotSupported, 'The wave format is not of supported type.'),
    # unsupported subFormatTag = WAVE_FORMAT_IEEE_FLOAT
    ([b'fmt ', ], 40, WAVE_FORMAT_EXTENSIBLE, 0x0003,
     WaveFileNotSupported, 'The wave format is not of supported type.'),
])
def test_get_fmt_chunk_fail(fmt_names, chunk_size, format_tag,
                            sub_format_tag, exception_type, error_msg, mocker):
    """
    Test head chunk is read correctly
    """
    read_list = [struct.pack('<H', sub_format_tag),
                 struct.pack('<HHLLHH', format_tag, 1, 2, 3, 4, 5)]
    # mock Chunk methods
    mocker.patch.object(chunk.Chunk, '__init__', return_value=None)
    mocker.patch.object(chunk.Chunk, 'getname',
                        side_effect=lambda: fmt_names.pop())
    mocker.patch.object(chunk.Chunk, 'getsize', return_value=chunk_size)
    mocker.patch.object(chunk.Chunk, 'read',
                        side_effect=lambda _: read_list[-1])
    mocker.patch.object(chunk.Chunk, 'seek',
                        side_effect=lambda _: read_list.pop())

    with pytest.raises(exception_type, match=esc(error_msg)):
        get_fmt_chunk(None)


def test_check_format_info_pass():
    check_format_info(FormatInfo(0, 0, 1, 2, 2, 8))


@pytest.mark.parametrize('info, expected_msg', [
    (FormatInfo(0, 0, 0, 0, 2, 4), "Block align is incorrect for 4 bits. "
                                   "Expected: 1, Actual: 2."),
    (FormatInfo(0, 0, 1, 3, 2, 8), "Avg. bytes per sec. is incorrect. "
                                   "Expected: 2, Actual: 3.")
])
def test_check_format_info_fail(info, expected_msg):
    with pytest.raises(WaveFileIsCorrupted, match=esc(expected_msg)):
        check_format_info(info)


@pytest.mark.parametrize('chunk_names', [
    # test that it accept both cases (fact chunk is optional)
    [b'data', ],
    [b'data', b'fact'],
    [b'data', b'foo ', b'fact']
])
def test_get_data_chunk(chunk_names, mocker):
    """
    Test data chunk is read correctly
    """
    # mock Chunk methods
    mocker.patch.object(chunk.Chunk, '__init__', return_value=None)
    mocker.patch.object(chunk.Chunk, 'getname',
                        side_effect=lambda: chunk_names.pop())
    mocker.patch.object(chunk.Chunk, 'skip')

    assert isinstance(get_data_chunk(None), chunk.Chunk)
    # check all called as expected
    chunk.Chunk.__init__.assert_called_with(None, bigendian=False)
    chunk.Chunk.getname.assert_called_with()


@pytest.mark.parametrize('format, dtype', [
    # single channel (mono)
    (FormatInfo(wFormatTag=1, nChannels=1, nSamplesPerSec=1,
                nAvgBytesPerSec=2, nBlockAlign=2, wBitsPerSample=8), '<u1'),
    (FormatInfo(wFormatTag=1, nChannels=1, nSamplesPerSec=1,
                nAvgBytesPerSec=4, nBlockAlign=4, wBitsPerSample=16), '<i2'),
    (FormatInfo(wFormatTag=1, nChannels=1, nSamplesPerSec=1,
                nAvgBytesPerSec=8, nBlockAlign=8, wBitsPerSample=32), '<i4'),
    # multi-channel (stereo)
    (FormatInfo(wFormatTag=1, nChannels=2, nSamplesPerSec=1,
                nAvgBytesPerSec=2, nBlockAlign=2, wBitsPerSample=8), '<u1'),
    (FormatInfo(wFormatTag=1, nChannels=2, nSamplesPerSec=1,
                nAvgBytesPerSec=4, nBlockAlign=4, wBitsPerSample=16), '<i2'),
    (FormatInfo(wFormatTag=1, nChannels=2, nSamplesPerSec=1,
                nAvgBytesPerSec=8, nBlockAlign=8, wBitsPerSample=32), '<i4')
])
def test_get_data_from_chunk(format, dtype, mocker):
    """
    Test data is read correctly from chunk
    """
    # mock Chunk methods
    chunk = mocker.MagicMock()
    chunk.getsize.return_value = format.nBlockAlign
    chunk.read.return_value = 'bytes'

    data = mocker.MagicMock()
    data.reshape.return_value = data

    fromstring = mocker.patch.object(numpy, 'fromstring',
                                     return_value=data)

    assert get_data_from_chunk(chunk, format) is data
    # check all called as expected
    chunk.getsize.assert_called_with()
    chunk.read.assert_called_with(format.nBlockAlign)
    fromstring.assert_called_with('bytes', dtype=dtype)
    if format.nChannels > 1:
        data.reshape.assert_called_with(-1, format.nChannels)


@pytest.mark.parametrize('format', [
    # single channel (mono)
    FormatInfo(wFormatTag=1, nChannels=1, nSamplesPerSec=1,
                nAvgBytesPerSec=6, nBlockAlign=6, wBitsPerSample=24),
    # multi-channel (stereo)
    FormatInfo(wFormatTag=1, nChannels=2, nSamplesPerSec=1,
               nAvgBytesPerSec=6, nBlockAlign=6, wBitsPerSample=24)
])
def test_get_data_from_chunk_24_bit(format, mocker):
    """
    Test data is read correctly from chunk for 24 bit
    """
    # mock Chunk methods
    chunk = mocker.MagicMock()
    chunk.getsize.return_value = format.nBlockAlign
    chunk.read.return_value = b'\n\x00\x00' # 10 in int 24

    data = mocker.MagicMock()
    data.reshape.return_value = data

    unpack = mocker.patch.object(struct, 'unpack', return_value=[10])
    array = mocker.patch.object(numpy, 'array',
                                     return_value=data)

    assert get_data_from_chunk(chunk, format) is data
    # check all called as expected
    chunk.getsize.assert_called_with()
    chunk.read.assert_called_with(3)
    unpack.assert_called_with('<I', b'\n\x00\x00\x00')
    array.assert_called_with([10, 10])
    if format.nChannels > 1:
        data.reshape.assert_called_with(-1, format.nChannels)


@pytest.mark.parametrize('format', [
    # single channel (mono)
    FormatInfo(wFormatTag=1, nChannels=1, nSamplesPerSec=1,
                nAvgBytesPerSec=6, nBlockAlign=6, wBitsPerSample=24),
    # multi-channel (stereo)
    FormatInfo(wFormatTag=1, nChannels=2, nSamplesPerSec=1,
               nAvgBytesPerSec=6, nBlockAlign=6, wBitsPerSample=24)
])
def test_get_data_from_chunk_raises_error_if_corrupt(format, mocker):
    """
    Test data is read correctly from chunk for 24 bit
    """
    # mock Chunk methods
    chunk = mocker.MagicMock()
    chunk.getsize.return_value = 1

    format = FormatInfo(wFormatTag=1, nChannels=2, nSamplesPerSec=1,
               nAvgBytesPerSec=6, nBlockAlign=6, wBitsPerSample=24)

    with pytest.raises(WaveFileIsCorrupted,
                       match=esc('Data size does not match frame '
                                 'size of 24 bits')):
        get_data_from_chunk(chunk, format)

