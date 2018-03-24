import pytest
import scipy.io.wavfile
import wave
from wavy import *
from test.utils import *


def supported_by_scipy(file):
    """
    Filter files not supported by scipy.
    """
    return not (file.sample_width == 24 and \
                file.dtype == numpy.int32)


@pytest.mark.parametrize('file',
                         filter(supported_by_scipy, get_audio_files()),
                         ids=lambda x: str(x))
def test_scipy_read(file):
    """
    Test equivalence in between wavy and scipy.
    """
    # read file in wavy
    result = read(file.file_path)

    # read file with scipy
    framerate, comp = scipy.io.wavfile.read(file.file_path)

    # test equivalence
    assert result.framerate == framerate
    assert numpy.array_equal(result.data, comp)


def supported_by_wave(file):
    """
    Filter files not supported by builtins.wave.
    """
    return 'int' in file.dtype.name \
           and '_ext' not in str(file)


@pytest.mark.parametrize('file',
                         filter(supported_by_wave, get_audio_files()),
                         ids=lambda x: str(x))
def test_wave_read(file):
    """
    Test equivalence in between wavy and scipy.
    """
    # read file in wavy
    result = read(file.file_path)

    # read file with scipy
    comp = wave.open(file.file_path, mode='rb')

    # check that file info matches wave.open info
    assert result.sample_width == comp.getsampwidth() * 8
    assert result.framerate == comp.getframerate()
    assert result.n_channels == comp.getnchannels()
    assert result.n_frames == comp.getnframes()
