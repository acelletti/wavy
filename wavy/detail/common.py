import chunk
import contextlib
import io
import numpy
import wavy

RIFF = b'RIFF'
WAVE = b'WAVE'
FMT = b'fmt '
DATA = b'data'
FACT = b'fact'
LIST = b'LIST'
INFO = b'INFO'

WAVE_FORMAT_PCM = 0x0001
WAVE_FORMAT_EXTENSIBLE = 0xFFFE

FMT_CHUNK_SIZES = [16, 18, 40]

INFO_TAGS_TO_PROPS = {
    'INAM': 'name',             # The name of the file (or "project").
    'ISBJ': 'subject',          # The subject.
    'IART': 'artist',           # The artist who created this.
    'ICMT': 'comment',          # A text comment.
    'IKEY': 'keywords',         # The keywords for the project or file.
    'ISFT': 'software',         # The software used to create the file.
    'IENG': 'engineer',         # The engineer.
    'ITCH': 'technician',       # The technician.
    'ICRD': 'creation_date',    # The creation date.
    'GENR': 'genre',            # Genre of content.
    'ICOP': 'copyright'         # The copyright information.
}

INFO_PROPS = [
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

def get_chunk(stream):
    """
    Get chunk for wave file (always little endian)
    """
    try:
        return chunk.Chunk(stream, bigendian=False)
    except EOFError:
        raise wavy.WaveFileIsCorrupted('Reached end of file prematurely.')


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
