import numpy
import os
import re
from wavy import Tags

# audio files for testing
AUDIO_FILES_FOLDER = 'test/integration/data'

# extract info from file name
AUDIO_FILES_REGEX = r"(\d+)bit_(\d+)Hz_(\d+)ch_(\d+)fr_([a-z]+)"

# identify files by number of frames
TAGS = {
    # file used for testing in cpython builtin.wave module
    3307: Tags(name='Pluck', subject='', artist='Serhiy Storchaka',
               comment='Audacity Pluck + Wahwah', keywords='',
               software='', engineer='', technician='',
               creation_date='2013', genre='', copyright=''),
    # sample from http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/Samples.html M1F1 file
    23493: None
}


class TestAudioFile(object):
    """
    Class to store audio file info.
    """

    def __init__(self, sample_width, framerate,
                 n_channels, n_frames, dtype,
                 file_path):

        # get from file name
        self.sample_width = int(sample_width)
        self.framerate = int(framerate)
        self.n_channels = int(n_channels)
        self.n_frames = int(n_frames)
        self.file_path = file_path

        self.tags = TAGS[self.n_frames]

        # work out dtype for data
        if dtype == 'pcm':
            if self.sample_width == 8:
                self.dtype = 'u1'
            elif self.sample_width == 24:
                self.dtype = 'i4'
                # when converting to this one to extensible sox removed
                # the tag
                if '_ext' in self.file_path:
                    self.tags = None
            else:
                self.dtype = 'i{}'.format(self.sample_width // 8)
        else:
            self.dtype = 'f{}'.format(self.sample_width // 8)

        self.dtype = numpy.dtype(self.dtype)

    def __repr__(self):
        # return file name
        return os.path.basename(self.file_path[:-4])


def get_all_files(dir_name):
    """
    Get all files in the folder in alphabetic order.
    """
    return list(sorted(filter(os.path.isfile,
                              [os.path.join(dir_name, file) for file in os.listdir(dir_name)])))


def get_audio_files():
    """
    Get information about the test audio files for tests.
    """
    test_files = []

    for file in get_all_files(AUDIO_FILES_FOLDER):
        # extract info from name and create test obj
        info = re.findall(AUDIO_FILES_REGEX, file)[0]
        test_files.append(TestAudioFile(*info, file))

    return test_files
