import chunk
import contextlib
import io
import numpy
import wavy

RIFF = b'RIFF'
RIFX = b'RIFX'

WAVE = b'WAVE'
FMT = b'fmt '
DATA = b'data'
FACT = b'fact'
LIST = b'LIST'
INFO = b'INFO'

SUPPORTED_HEADERS = [RIFF, RIFX]

WAVE_FORMAT_PCM = 0x0001
WAVE_FORMAT_IEEE_FLOAT = 0x0003
WAVE_FORMAT_EXTENSIBLE = 0xFFFE

SUPPORTED_WAVE_FORMATS = [WAVE_FORMAT_PCM, WAVE_FORMAT_IEEE_FLOAT]

FMT_CHUNK_SIZES = [16, 18, 40]
SUPPORTED_SAMPLE_WIDTH = [8, 16, 24, 32]

SUPPORTED_SAMPLE_WIDTH_FOR_DTYPE = {
    'uint8': [8],
    'int16': [16],
    'int32': [24, 32],
    'float32': [32],
    'float64': [64]
}

SUPPORTED_SAMPLE_WIDTH_FOR_FORMAT = {
    0x0001: [8, 16, 24, 32],
    0x0003: [32, 64],
}

TAGS_TO_PROPS = {
    'INAM': 'name',  # The name of the file (or "project").
    'ISBJ': 'subject',  # The subject.
    'IART': 'artist',  # The artist who created this.
    'ICMT': 'comment',  # A text comment.
    'IKEY': 'keywords',  # The keywords for the project or file.
    'ISFT': 'software',  # The software used to create the file.
    'IENG': 'engineer',  # The engineer.
    'ITCH': 'technician',  # The technician.
    'ICRD': 'creation_date',  # The creation date.
    'GENR': 'genre',  # Genre of content.
    'ICOP': 'copyright'  # The copyright information.
}

TAG_PROPS = [
    'name',
    'subject',
    'artist',
    'comment',
    'keywords',
    'software',
    'engineer',
    'technician',
    'creation_date',
    'genre',
    'copyright'
]


def check_sample_width_supported(sample_width, dtype):
    # get supported width for dtype
    supported_sample_width = SUPPORTED_SAMPLE_WIDTH_FOR_DTYPE.get(str(dtype), None)

    # dtype is not supported
    if not supported_sample_width:
        raise wavy.WaveValueError(
            "Data array dtype '{}' is not supported.".format(dtype))

    # sample width is not supported
    if not sample_width in supported_sample_width:
        raise wavy.WaveValueError(
            "Sample width of '{}' is not supported for dtype '{}'.".format(sample_width, dtype))


def get_stream_from_file(file, flag, stream_class):
    """
    Checks that file is either a string or the stream returned by
    builtins.open. If it's string, it opens the stream and returns it.

    Args:
        file: File can be str or <file_class>
        flag: flag to be used for opening file ('rb' or 'wb')
        stream_class: Class type for stream obj

    Returns:
        stream_class: Instance of <stream_class>

    Raises:
        WaveFileNotSupported: If the file is not of either type.

    """
    # if it's a string, open file
    if isinstance(file, str):
        return open(file, flag)
    # then it must be already open
    if isinstance(file, stream_class):
        return file
    # raise exception with expected arg types
    raise wavy.WaveFileNotSupported(
        "'file' argument must be a string or <{}> instance, {} given instead."
            .format(stream_class.__name__, type(file)))
