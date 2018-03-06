import numpy
import pytest
from re import escape as esc
from wavy import *


@pytest.mark.parametrize('data, channels, tags', [
    (numpy.array([1, 2]), 1, None),
    (numpy.array([1, 2, 3, 4]).reshape(-1, 2), 2, Tags())
])
def test_wave_file(data, channels, tags):
    """
    Test that WaveFile is created correctly.
    """
    wav_file = WaveFile(32, 100, data, tags)

    assert wav_file.sample_width == 32
    assert wav_file.framerate == 100
    assert wav_file.n_channels == channels
    assert wav_file.n_frames == 2
    assert numpy.array_equal(wav_file.data, data)
    assert wav_file.tags == tags


@pytest.mark.parametrize('data, tags, error', [
    ([], None, "Argument 'data' must be of type numpy.ndarray."),
    (numpy.array([]), None, "Data array cannot be empty."),
    (numpy.array([1, 2]), 'Tags', "Argument 'tags' must be of type 'wavy.Tags'."),
])
def test_wave_file_invalid_args(data, tags, error):
    """
    Test that WaveFile is created correctly.
    """
    with pytest.raises(wavy.WaveValueError, match=esc(error)):
        WaveFile(32, 100, data, tags)
