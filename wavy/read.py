import io
import wavy
import wavy.detail


def read(file):
    """
    Read the the audio file.

    Args:
        file (str or File): Either the path to the file or an instance of File.

    Returns:
        WaveFile: An object that represents the file.

    """
    # get buffer reader, already opened for us
    with wavy.detail.get_stream_from_file(file, 'rb', io.BufferedReader) as \
            stream:
        # get file format & data
        format, tags, data = wavy.detail.read_stream(stream)

    # return WaveFile obj
    return wavy.WaveFile(sample_width=format.wBitsPerSample,
                         framerate=format.nSamplesPerSec,
                         data=data,
                         tags=tags)
