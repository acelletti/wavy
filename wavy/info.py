import collections
import io
import wavy.detail

WaveFileInfo = collections.namedtuple('WaveFileInfo', [
    'sample_width',
    'framerate',
    'n_channels',
    'n_frames',
    'tags'
])
"""
Named tuple that represent information about the WAVE file.
"""


def info(file):
    """
    Returns information about the audio file.

    Args:
        file (str or File): Either the path to the file or an instance of File.

    Returns:
        WaveFileInfo: Information about the file.

    """
    # get buffer reader, already opened for us
    with wavy.detail.get_stream_from_file(file, 'rb', io.BufferedReader) as \
            stream:
        # get file format & data
        format, tags, size = wavy.detail.read_stream(stream, read_data=False)

    # return WaveFile obj
    return WaveFileInfo(sample_width=format.wBitsPerSample,
                        framerate=format.nSamplesPerSec,
                        n_channels=format.nChannels,
                        n_frames=size // format.nBlockAlign,
                        tags=tags)
