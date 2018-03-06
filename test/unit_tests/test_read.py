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

    @contextlib.contextmanager
    def mock_manager(x, y, z):
        yield 'stream'

    get_stream_from_file = mocker.patch('wavy.detail.get_stream_from_file',
                                        side_effect=mock_manager)

    read_stream = mocker.patch('wavy.detail.read_stream',
                               return_value=(format, 'tags', 'data'))

    mocker.patch.object(wavy.WaveFile, '__init__', return_value=None)

    wavy.read('file')

    get_stream_from_file.assert_called_with('file', 'rb', io.BufferedReader)
    read_stream.assert_called_with('stream')
    wavy.WaveFile.__init__.assert_called_with(sample_width=1,
                                              framerate=2,
                                              data='data',
                                              tags='tags')
