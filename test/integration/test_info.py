import pytest
from wavy import *
from test.utils import *


@pytest.mark.parametrize('file', get_audio_files(), ids=lambda x: str(x))
def test_read(file):
    """
    Test info function with real audio files.
    """
    # read file information
    result = info(file.file_path)

    # check that file info matches expected
    assert result.sample_width == file.sample_width
    assert result.framerate == file.framerate
    assert result.n_channels == file.n_channels
    assert result.n_frames == file.n_frames
    assert result.tags == file.tags

