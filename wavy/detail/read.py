import collections
import numpy
import struct
import wavy
from .common import *

FormatInfo = collections.namedtuple('FormatInfo', [
    'wFormatTag',
    'nChannels',
    'nSamplesPerSec',
    'nAvgBytesPerSec',
    'nBlockAlign',
    'wBitsPerSample'
])


def check_head_chunk(stream):
    """
    Reads the master chunk from the stream and checks that it matches the
    specifications for Wave files.

    Args:
        stream: The stream to read

    Raises:
        wavy.WaveFileIsCorrupted: If file is corrupted.
        wavy.WaveFileNotSupported: If the master chunk does not match
        specifications.

    """
    chunk = get_chunk(stream)
    # the master chunk should always be RIFF
    if chunk.getname() != RIFF:
        raise wavy.WaveFileNotSupported('File does not start with RIFF ID.')
    # WAVEID should always be WAVE
    if stream.read(4) != WAVE:
        raise wavy.WaveFileNotSupported('File does not appear to be a WAVE '
                                        'file.')


def get_sub_format(fmt_chunk):
    """
    Read first two bytes of subFormat tag from fmt_chunk (indicates the actual
    format for extended encoding).
    Args:
        fmt_chunk: The format chunk.

    Returns:
        int: First two bytes of subFormat tag.
    """
    fmt_chunk.seek(24)
    return struct.unpack_from('<H', fmt_chunk.read(2))[0]


def get_fmt_chunk(stream):
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
    info = FormatInfo(*struct.unpack_from('<HHLLHH', chunk.read(16)))

    # we only support PCM
    if info.wFormatTag == WAVE_FORMAT_PCM:
        chunk.skip()
        return info

    # 24b PCM is encoded with WAVE_FORMAT_EXTENSIBLE and
    # WAVE_FORMAT_PCM as subFormat
    if info.wFormatTag == WAVE_FORMAT_EXTENSIBLE and \
            chunk.getsize() == 40 and \
            get_sub_format(chunk) == WAVE_FORMAT_PCM:
        chunk.skip()
        # replace WAVE_FORMAT_PCM with PCM and return info
        return FormatInfo(WAVE_FORMAT_PCM, *list(info)[1:])

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


def get_data_chunk(stream):
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
        chunk.skip()


def read_24_bit_stream(chunk, size):
    """
    Read chunk for 24 bit format (exception since we cannot use builtin
    functionality).

    Args:
        chunk: Data chunk
        size: Actual size (size / 3 bytes)

    Returns:
        numpy.array: Data read from chunk

    """
    data = []
    for _ in range(size):
        # need to pad the last bytes so that we can read 24 bit as 32
        data += struct.unpack('<I', chunk.read(3) + b'\x00')
    # convert to numpy array
    return numpy.array(data)


def get_data_from_chunk(chunk, format):
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
    dtype = format.wBitsPerSample // 8

    # great, if not 24 we can use numpy built in parser
    if format.wBitsPerSample != 24:
        data = numpy.fromstring(chunk.read(size),
                                # if 8 bits is unsigned, otherwise signed
                                dtype=f'<i{dtype}' if dtype > 1 else '<u1')
    else:
        # this is a corner case that, as of now, neither numpy nor struct is
        # capable of handling, so we have to do it ourselves
        data = read_24_bit_stream(chunk, size // dtype)

    # check if there is more than one channel, if so reshape
    return data if format.nChannels == 1 \
        else data.reshape(-1, format.nChannels)


def read_stream(stream, read_data=True):
    # check head chunk is valid
    check_head_chunk(stream)
    # get file format from chunk
    format = get_fmt_chunk(stream)
    # make sure format info is correct
    check_format_info(format)
    # get data chunk
    data_chunk = get_data_chunk(stream)

    if not read_data:
        # stop here and return info
        return format, data_chunk.getsize()

    # parse data from chunk
    data = get_data_from_chunk(data_chunk, format)

    return format, data
