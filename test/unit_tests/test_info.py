import contextlib
import io
import wavy
import wavy.detail


def test_read(mocker):
    """
    Test function behaves as expected
    """
    format = mocker.MagicMock()
    format.wBitsPerSample = 1
    format.nSamplesPerSec = 2
    format.nChannels = 3
    format.nBlockAlign = 1

    @contextlib.contextmanager
    def mock_manager(x, y, z):
        yield 'stream'

    get_stream_from_file = mocker.patch('wavy.detail.get_stream_from_file',
                                        side_effect=mock_manager)

    read_stream = mocker.patch('wavy.detail.read_stream',
                               return_value=(format, 'tags', 10))

    assert wavy.info('file') == wavy.WaveFileInfo(sample_width=1,
                                                  framerate=2,
                                                  n_channels=3,
                                                  n_frames=10,
                                                  tags='tags')

    get_stream_from_file.assert_called_with('file', 'rb', io.BufferedReader)
    read_stream.assert_called_with('stream', read_data=False)
