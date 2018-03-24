import numpy
import pytest
from re import escape as esc
from wavy import *


@pytest.mark.parametrize('sample_width, data, channels, tags', [
    (8, numpy.array([1, 2], dtype=numpy.uint8), 1, None),
    (16, numpy.array([1, 2], dtype=numpy.int16), 1, None),
    (24, numpy.array([1, 2], dtype=numpy.int32), 1, None),
    (32, numpy.array([1, 2], dtype=numpy.int32), 1, None),
    (32, numpy.array([1, 2], dtype=numpy.float32), 1, None),
    (64, numpy.array([1, 2], dtype=numpy.float64), 1, None),
    (32, numpy.array([1, 2], dtype=numpy.int32), 1, None),
    (32, numpy.array([1, 2, 3, 4], dtype=numpy.int32).reshape(-1, 2), 2, Tags()),
])
def test_wave_file(sample_width, data, channels, tags):
    """
    Test that WaveFile is created correctly.
    """
    wav_file = WaveFile(sample_width, 100, data, tags)

    assert wav_file.sample_width == sample_width
    assert wav_file.framerate == 100
    assert wav_file.n_channels == channels
    assert wav_file.n_frames == 2
    assert numpy.array_equal(wav_file.data, data)
    assert wav_file.tags == tags


@pytest.mark.parametrize('sample_width, data, tags, error', [
    (None, [], None, "Argument 'data' must be of type numpy.ndarray."),
    (8, numpy.array([], dtype=numpy.uint8), None, "Data array cannot be empty."),
    (16, numpy.array([1], dtype=numpy.float16), None, "Data array dtype 'float16' is not supported."),
    (16, numpy.array([1], dtype=numpy.uint8), None, "Sample width of '16' is not supported for dtype 'uint8'."),
    (8, numpy.array([1, 2], dtype=numpy.uint8), 'Tags', "Argument 'tags' must be of type 'wavy.Tags'."),
])
def test_wave_file_invalid_args(sample_width, data, tags, error):
    """
    Test that WaveFile is created correctly.
    """
    with pytest.raises(wavy.WaveValueError, match=esc(error)):
        WaveFile(sample_width, 100, data, tags)
