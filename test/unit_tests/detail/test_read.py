import chunk
import numpy
import pytest
from re import escape as esc
from wavy import *
from wavy.detail import *


def test_get_chunk_eof(mocker):
    mocker.patch.object(chunk.Chunk, '__init__', side_effect=EOFError)
    with pytest.raises(wavy.WaveFileIsCorrupted,
                       match=esc('Reached end of file prematurely.')):
        get_chunk(None)


@pytest.mark.parametrize('content, le', [
    ([b'WAVE', 0, b'RIFF'], True),
    ([b'WAVE', 0, b'RIFX'], False)
])
def test_get_stream_handler(content, le, mocker):
    """
    Test head chunk is read correctly
    """
    # mock stream methods
    stream = mocker.MagicMock()
    stream.read.side_effect = lambda x: content.pop()

    handler = get_stream_handler(stream)
    # check all called as expected
    stream.read.assert_has_calls([mocker.call(4),
                                  mocker.call(4),
                                  mocker.call(4)])

    assert isinstance(handler, StreamHandler)
    assert handler.little_endian == le


def test_check_head_chunk_wrong_tag(mocker):
    """
    Test exception is raised when head tag has unknown type.
    """
    # mock stream methods
    stream = mocker.MagicMock()
    stream.read.return_value = b'XFIR'

    with pytest.raises(WaveFileNotSupported,
                       match=esc("Unsupported header for "
                                 "file 'XFIR'.")):
        get_stream_handler(stream)


def test_check_head_chunk_wrong_type(mocker):
    """
    Test exception is raised when wave type tag has unknown type.
    """
    content = [b'BARB', 0, b'RIFF']
    # mock stream methods
    stream = mocker.MagicMock()
    stream.read.side_effect = lambda x: content.pop()

    with pytest.raises(WaveFileNotSupported,
                       match=esc('File does not appear to be a WAVE file.')):
        get_stream_handler(stream)


@pytest.mark.parametrize('fmt_names, chunk_size, format_tag, sub_format_tag', [
    # WAVE_FORMAT_PCM with allowed chunk sizes
    ([b'fmt ', ], 16, WAVE_FORMAT_PCM, 0),
    ([b'fmt ', ], 18, WAVE_FORMAT_PCM, 0),
    ([b'fmt ', ], 40, WAVE_FORMAT_PCM, 0),
    ([b'fmt ', ], 16, WAVE_FORMAT_IEEE_FLOAT, 0),
    ([b'fmt ', ], 18, WAVE_FORMAT_IEEE_FLOAT, 0),
    ([b'fmt ', ], 40, WAVE_FORMAT_IEEE_FLOAT, 0),
    # make sure it finds chunk after others
    ([b'fmt ', b'bar', b'RIFF', b'foo'], 16, WAVE_FORMAT_PCM, 0),
    # cover WAVE_FORMAT_EXTENSIBLE for PCM
    ([b'fmt ', ], 40, WAVE_FORMAT_EXTENSIBLE, WAVE_FORMAT_PCM),
    ([b'fmt ', ], 40, WAVE_FORMAT_IEEE_FLOAT, WAVE_FORMAT_PCM)
])
def test_get_fmt_chunk(fmt_names, chunk_size, format_tag,
                       sub_format_tag, mocker):
    """
    Test head chunk is read correctly
    """
    read_list = [struct.pack('<H', sub_format_tag),
                 struct.pack('<HHLLHH', format_tag, 1, 2, 3, 4, 32)]
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

    expected_format = sub_format_tag if format_tag == WAVE_FORMAT_EXTENSIBLE else format_tag
    assert get_fmt_chunk(None, StreamHandler(True)) == FormatInfo(expected_format, 1, 2, 3, 4, 32)
    # check all called as expected
    chunk.Chunk.__init__.assert_called_with(None, bigendian=False)
    chunk.Chunk.getname.assert_called_with()
    chunk.Chunk.getsize.assert_called_with()
    if format_tag in SUPPORTED_WAVE_FORMATS:
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
    # unsupported wFormatTag = WAVE_FORMAT_ALAW
    ([b'fmt ', ], 40, 0x0006, 0,
     WaveFileNotSupported, 'The wave format is not of supported type.'),
    # WAVE_FORMAT_EXTENSIBLE should have chunksize of 40
    ([b'fmt ', ], 18, WAVE_FORMAT_EXTENSIBLE, 0,
     WaveFileNotSupported, 'The wave format is not of supported type.'),
    # unsupported subFormatTag = WAVE_FORMAT_ALAW
    ([b'fmt ', ], 40, WAVE_FORMAT_EXTENSIBLE, 0x0006,
     WaveFileNotSupported, 'The wave format is not of supported type.'),
    # unsupported subFormatTag = WAVE_FORMAT_ALAW
    ([b'fmt ', ], 16, WAVE_FORMAT_PCM, 0,
     WaveFileNotSupported, "Sample width '5' is not supported for given type."),
    ([b'fmt ', ], 40, WAVE_FORMAT_EXTENSIBLE, WAVE_FORMAT_PCM,
     WaveFileNotSupported, "Sample width '5' is not supported for given type.")
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
        get_fmt_chunk(None, StreamHandler(True))


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
    [b'data', b'LIST', b'fact']
])
def test_get_data_chunk(chunk_names, mocker):
    """
    Test data chunk is read correctly
    """
    # mock Chunk methods
    mock_chunk = mocker.MagicMock()
    mock_chunk.skip.return_value = None
    mock_chunk.getname.side_effect = lambda: chunk_names.pop()

    get_chunk = mocker.patch('wavy.detail.read.get_chunk', return_value=mock_chunk)

    # list chunk parsing
    has_list = b'LIST' in chunk_names
    read_list_chunk = mocker.patch('wavy.detail.read.read_list_chunk')

    assert get_data_chunk(None) == mock_chunk
    # check all called as expected
    get_chunk.assert_called_with(None)
    mock_chunk.getname.assert_called_with()

    if has_list:
        read_list_chunk.assert_called_with(None, mock_chunk, {})


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
    data_size = 10 * format.nBlockAlign

    chunk = mocker.MagicMock()
    chunk.getsize.return_value = data_size

    data = mocker.MagicMock()
    data.reshape.return_value = data

    handler = mocker.MagicMock()
    handler.read_data.return_value = data

    assert get_data_from_chunk(chunk, format, handler) is data
    # check all called as expected
    chunk.getsize.assert_called_with()
    handler.read_data.assert_called_with(chunk, data_size, format.wBitsPerSample // 8, False)
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
        get_data_from_chunk(chunk, format, None)


mock_tags = {
    'tags': [b'foo', b'bar\x00'],
    'values': [b'value2\x00\x00', b'value1\x00\x00\x00\x00'],
}


def test_read_list_chunk(mocker):
    """
    Test info is read correctly from list chunk
    """
    chunk = mocker.MagicMock()
    chunk.getsize.return_value = 36
    chunk.read.return_value = b'INFO'

    sub_chunk = mocker.MagicMock()
    sub_chunk.getsize.return_value = 8
    sub_chunk.getname.side_effect = lambda: mock_tags['tags'].pop()
    sub_chunk.read.side_effect = lambda: mock_tags['values'].pop()

    mocker.patch('wavy.detail.read.get_chunk', return_value=sub_chunk)
    info_dict = {}
    read_list_chunk('stream', chunk, info_dict)

    assert info_dict == {'bar': 'value1', 'foo': 'value2'}


def test_read_list_chunk_not_info(mocker):
    """
    Test list chunk is skipped if not info
    """
    chunk = mocker.MagicMock()
    chunk.read.return_value = b'foo '
    chunk.skip.return_value = None

    read_list_chunk(None, chunk, None)

    chunk.skip.assert_called_with()


@pytest.mark.parametrize('tags, expected', [
    ({},
     Tags()
     ),
    ({
         'INAM': 'name', 'ISBJ': 'subject', 'IART': 'artist', 'ICMT': 'comment',
         'IKEY': 'keywords', 'ISFT': 'software', 'IENG': 'engineer', 'ITCH': 'technician',
         'ICRD': 'creation_date', 'GENR': 'genre', 'ICOP': 'copyright'
     },
     Tags(name='name', subject='subject', artist='artist', comment='comment',
          keywords='keywords', software='software', engineer='engineer',
          technician='technician', creation_date='creation_date',
          genre='genre', copyright='copyright')
    )
])
def test_get_info_from_tags_dict(tags, expected):
    """
    Test that info is copied in the right field for Tags
    """
    assert get_info_from_tags_dict(tags) == expected


@pytest.mark.parametrize('read_data, tags', [
    (True, {}),
    (True, {'foo': 'bar'}),
    (False, {}),
    (False, {'foo': 'bar'})
])
def test_read_stream(read_data, tags, mocker):
    """
    Test that read stream return correct data
    """

    chunk = mocker.MagicMock()
    chunk.getsize.return_value = 8

    def get_data_chunk_mck(x, y):
        y.update(tags)
        return chunk

    check_head_chunk = mocker.patch('wavy.detail.read.get_stream_handler', return_value='stream_handler')
    get_fmt_chunk = mocker.patch('wavy.detail.read.get_fmt_chunk', return_value='format')
    check_format_info = mocker.patch('wavy.detail.read.check_format_info')

    get_data_chunk = mocker.patch('wavy.detail.read.get_data_chunk', side_effect=get_data_chunk_mck)

    get_info_from_tags_dict = mocker.patch('wavy.detail.read.get_info_from_tags_dict', return_value='info')
    get_data_from_chunk = mocker.patch('wavy.detail.read.get_data_from_chunk', return_value='data')

    result = read_stream('stream', read_data)

    check_head_chunk.assert_called_with('stream')
    get_fmt_chunk.assert_called_with('stream', 'stream_handler')
    check_format_info.assert_called_with('format')
    get_data_chunk.assert_called_with('stream', tags)

    if tags:
        get_info_from_tags_dict.assert_called_with(tags)

    if read_data:
        get_data_from_chunk.assert_called_with(chunk, 'format', 'stream_handler')

    info = 'info' if tags else None

    if read_data:
        assert result == ('format', info, 'data')
    else:
        assert result == ('format', info, 8)
