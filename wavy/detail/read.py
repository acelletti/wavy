import collections
import numpy
import struct
import wavy
from .common import *
from .stream_handler import *

FormatInfo = collections.namedtuple('FormatInfo', [
    'wFormatTag',
    'nChannels',
    'nSamplesPerSec',
    'nAvgBytesPerSec',
    'nBlockAlign',
    'wBitsPerSample'
])


def get_chunk(stream):
    """
    Get chunk for wave file (always little endian)
    """
    try:
        return chunk.Chunk(stream, bigendian=False)
    except EOFError:
        raise wavy.WaveFileIsCorrupted('Reached end of file prematurely.')


def get_stream_handler(stream):
    """
    Reads the master chunk from the stream and checks that it matches the
    specifications for Wave files. Returns StreamHandler with the correct
    endianness set based on file header (RIFF or RIFX).

    Args:
        stream: The stream to read.

    Returns:
        StreamHandler: handler with correct endianness set.

    Raises:
        wavy.WaveFileIsCorrupted: If file is corrupted.
        wavy.WaveFileNotSupported: If the master chunk does not match
        specifications.

    """
    header = stream.read(4)
    # the master chunk should always be RIFF or RIFX
    if header not in SUPPORTED_HEADERS:
        raise wavy.WaveFileNotSupported("Unsupported header for "
                                        "file '{}'.".format(header.decode()))

    handler = StreamHandler(little_endian=header == RIFF)
    # this will be the size of the chunk
    stream.read(4)
    # WAVEID should always be WAVE
    if stream.read(4) != WAVE:
        raise wavy.WaveFileNotSupported('File does not appear to be a WAVE '
                                        'file.')

    return handler


def get_sub_format(fmt_chunk, handler):
    """
    Read first two bytes of subFormat tag from fmt_chunk (indicates the actual
    format for extended encoding).
    Args:
        fmt_chunk: The format chunk.

    Returns:
        int: First two bytes of subFormat tag.
    """
    fmt_chunk.seek(24)
    return handler.read('H', fmt_chunk.read(2))[0]


def get_fmt_chunk(stream, handler):
    """
    Reads the format chunk from the stream, checks that it matches the
    specifications for Wave files and returns format information.

    Args:
        stream: The stream to read.

    Returns:
        FormatInfo: Format info from fmt chunk.

    Raises:
        wavy.WaveFileIsCorrupted: If file is corrupted.
        wavy.WaveFileNotSupported: If file type is not PCM.

    """
    # iterate through chunks until we find format
    while True:
        chunk = get_chunk(stream)
        name = chunk.getname()
        # found format
        if name == FMT:
            break
        # we got to the data chunks, something is wrong
        if name == DATA:
            raise wavy.WaveFileIsCorrupted('Found data chunk before fmt chunk.')
        chunk.skip()

    # chunk size is not supported
    if chunk.getsize() not in FMT_CHUNK_SIZES:
        raise wavy.WaveFileIsCorrupted(
            'Format chunk is of unexpected size: {}.'.format(chunk.getsize()))

    # extract common chunk info into tuple
    info = FormatInfo(*handler.read('HHLLHH', chunk.read(16)))

    format_tag = info.wFormatTag

    # if format extensible is used, the format tag
    # will be specified in the sub format
    if format_tag == WAVE_FORMAT_EXTENSIBLE and \
            chunk.getsize() == 40:
        # get format tag
        format_tag = get_sub_format(chunk, handler)
        # replace tag in FormatInfo
        info = FormatInfo(format_tag, *list(info)[1:])

    # we only support PCM and FLOAT
    if format_tag in SUPPORTED_WAVE_FORMATS:

        # check that the sample width is supported for type
        if info.wBitsPerSample not in \
                SUPPORTED_SAMPLE_WIDTH_FOR_FORMAT[format_tag]:
            raise wavy.WaveFileNotSupported(
                "Sample width '{}' is not supported for "
                "given type.".format(info.wBitsPerSample))

        chunk.skip()
        return info

    raise wavy.WaveFileNotSupported('The wave format is not of supported type.')


def check_format_info(info):
    """
    Check that format info is correct.

    Args:
        info: Format info from fmt chunk.

    Raises:
        wavy.WaveFileIsCorrupted: If format info is incorrect.

    """
    # check that block align matches bits per sample
    block_align = int(info.wBitsPerSample / 4)
    if block_align != info.nBlockAlign:
        raise wavy.WaveFileIsCorrupted(
            f"Block align is incorrect for {info.wBitsPerSample} bits. "
            f"Expected: {block_align}, "
            f"Actual: {info.nBlockAlign}.")

    # check that avg bytes per sample matches expected value
    n_avg_bytes_per_sec = info.nSamplesPerSec * info.nBlockAlign
    if n_avg_bytes_per_sec != info.nAvgBytesPerSec:
        raise wavy.WaveFileIsCorrupted(
            f"Avg. bytes per sec. is incorrect. "
            f"Expected: {n_avg_bytes_per_sec}, "
            f"Actual: {info.nAvgBytesPerSec}.")


def get_data_chunk(stream, info_tags={}):
    """
    Reads the data chunk from the stream.

    Args:
        stream: The stream to read.

    Returns:
        chunk: Data chunk.

    Raises:
        wavy.WaveFileIsCorrupted: If file is corrupted.

    """
    # iterate through chunks until we find data
    while True:
        chunk = get_chunk(stream)
        name = chunk.getname()
        # found data
        if name == DATA:
            return chunk
        elif name == LIST:
            read_list_chunk(stream, chunk, info_tags)
        else:
            chunk.skip()


def get_string_from_bytes(bytes_list):
    """
    Get string from bytes list.

    Args:
        bytes_list: Bytes list.

    Returns:
        str: The corresponding string.

    """
    # remove padding at the end
    return bytes_list.decode().rstrip('\x00')


def get_info_from_tags_dict(tags_dict):
    """
    Create Tags tuple from parsed tag dictionary.

    Args:
        tags_dict: Tag Dictionary

    Returns:
        Tags: The corresponding object.

    """
    return wavy.Tags(**{
        value: tags_dict.get(key, '')
        for key, value in TAGS_TO_PROPS.items()
    })


def read_list_chunk(stream, list_chunk, info_tags):
    """
    Parse LIST chunk information into provided dictionary.

    Args:
        stream: Byte stream.
        list_chunk: The LIST chunk.
        info_tags: Dictionary where to store parsed tags.

    """
    # if sub header is not info, skip chunk
    if INFO != list_chunk.read(4):
        list_chunk.skip()
        return

    # get size of chunk to parse (size - sub-header)
    bytes_to_parse = list_chunk.getsize() - 4

    # parse whole chunk one at the time
    while bytes_to_parse:
        chunk = get_chunk(stream)
        # remove chunk size from bytes to parse (size + chunk header)
        bytes_to_parse -= chunk.getsize() + 8
        # insert tag, value into dictionary
        tag = get_string_from_bytes(chunk.getname())
        info_tags[tag] = get_string_from_bytes(chunk.read())


def get_data_from_chunk(chunk, format, handler):
    """
    Read data from data chunk.
    Args:
        chunk: Data chunk.
        format: File format information.

    Returns:
        numpy.array: Data read from chunk.
    """
    # get size of data
    size = chunk.getsize()

    # this gives us the number of frames
    if size % format.nBlockAlign != 0:
        # something is wrong here, size should be a multiple
        raise wavy.WaveFileIsCorrupted("Data size does not match frame size of"
                                       f" {format.wBitsPerSample} bits")

    # number of bytes for data type to be parsed
    n_bytes = format.wBitsPerSample // 8

    # read data from raw
    data = handler.read_data(chunk, size, n_bytes,
                             format.wFormatTag == WAVE_FORMAT_IEEE_FLOAT)

    # check if there is more than one channel, if so reshape
    return data if format.nChannels == 1 \
        else data.reshape(-1, format.nChannels)


def read_stream(stream, read_data=True):
    """

    Args:
        stream: Byte stream
        read_data: Whether to read the file data or stop at the header.

    Returns:
        tuple: (format, info, data) if read_data is True.
        Otherwise (format, info, n_frames)

    """
    # check head chunk is valid
    handler = get_stream_handler(stream)
    # get file format from chunk
    format = get_fmt_chunk(stream, handler)
    # make sure format info is correct
    check_format_info(format)
    # create info dict to store optional info
    info_tags = {}
    # get data chunk
    data_chunk = get_data_chunk(stream, info_tags)
    # build info obj from tags (if any was found)
    info = get_info_from_tags_dict(info_tags) \
        if info_tags else None

    if not read_data:
        # stop here and return info
        return format, info, data_chunk.getsize()

    # parse data from chunk
    data = get_data_from_chunk(data_chunk, format, handler)

    return format, info, data
