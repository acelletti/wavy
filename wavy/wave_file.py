
class WaveFile(object):

    @property
    def sample_width(self):
        return self._sample_width

    @property
    def framerate(self):
        return self._framerate

    @property
    def n_channels(self):
        return self._n_channels

    @property
    def n_frames(self):
        return self._n_frames

    @property
    def data(self):
        return self._data

    def __init__(self, sample_width, framerate, data):
        # copy info
        self._sample_width = sample_width
        self._framerate = framerate
        # extract info from array
        self._n_frames, self._n_channels = data.shape
        self._data = data

    def __repr__(self):
        return f"WaveFile(sample_width={self.sample_width}, " \
               f"framerate={self.framerate}, n_channels={self.n_channels}, " \
               f"n_frames={self.n_frames})"
