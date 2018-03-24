import numpy
import struct

# prefixes for flagging endianness to struct reader/writer
# little endian
LE_PREFIX = '<'
# big endian
BE_PREFIX = '>'


class StreamHandler(object):
    """
    Wrapper around builtins.struct that stores endianness
    for both read and write operations.
    """

    def __init__(self, little_endian):
        """
        Args:
            little_endian: Whether the stream is little endian.
        """
        self.little_endian = little_endian
        # set prefix for read / write
        self.endian_prefix = \
            LE_PREFIX if little_endian else BE_PREFIX

    def read(self, format, stream, offset=0):
        """
        Read stream using builtins.struct.unpack_from.

        Args:
            format: The format to read from the buffer.
            stream: The stream of bytes (buffer).
            offset: The offset to read from.

        Returns:


        """
        return struct.unpack_from(self.endian_prefix + format, stream, offset)

    def read_data(self, stream, size, n_bytes, is_float):
        """
        Read data from stream as a numpy array.
        Args:
            stream: Stream to read from.
            size: Size of the data to read.
            n_bytes: The number of bytes for each data chunk.

        Returns:
            numpy.array: Array containing the read data.

        """
        # the byte size is supported so we use numpy
        if n_bytes % 3 != 0:
            # float is always f
            if is_float:
                type = 'f'
            else:
                # if 8 bits is unsigned, otherwise signed
                type = 'i' if n_bytes > 1 else 'u'
            # compose dtype for parsing data
            dtype = f"{self.endian_prefix}{type}{n_bytes}"
            # use numpy from string to read data
            return numpy.fromstring(stream.read(size), dtype=dtype)
        else:
            return self.read_data_for_unsupported_dtype(stream, size, n_bytes)

    def read_data_for_unsupported_dtype(self, stream, size, n_bytes):
        """
        Read data from stream as a numpy array for 24 and 48 bit int
        (not supported by numpy.fromstring).

        Args:
            stream: Stream to read from.
            size: Size of the data to read.
            n_bytes: The number of bytes for each data chunk.

        Returns:
            numpy.array: Array containing the read data.

        """
        # we need to add some padding so that we can read the bytes
        n_padding = (4 - n_bytes % 4)
        padding = n_padding * b'\x00'
        # go through the data manually with for loop
        data = []
        for _ in range(size // n_bytes):
            # need to pad depending on the endianness
            data += self.read('i' if n_bytes == 3 else 'q',
                              stream.read(n_bytes) + padding if self.little_endian else
                              padding + stream.read(n_bytes))
        # convert to numpy array
        return numpy.array(data, dtype=numpy.dtype('i{}'.format(n_bytes + n_padding)))
