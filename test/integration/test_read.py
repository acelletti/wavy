import os
import pytest
import numpy
import scipy.io.wavfile
from wavy import *

def get_all_files(dir_name):
    return list(filter(os.path.isfile,
        [os.path.join(dir_name, file) for file in os.listdir(dir_name)]))


@pytest.mark.parametrize('file', get_all_files('test/integration/data'))
def test_read(file):
    wave_file = read(file)

    if wave_file.sample_width != 24:
        _, comp = scipy.io.wavfile.read(file)
        assert numpy.array_equal(wave_file.data, comp)
