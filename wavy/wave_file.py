import numpy
import wavy
import wavy.detail


class WaveFile(object):
    """
    Class that represents a WAVE file.
    """

    @property
    def sample_width(self):
        """
        int: Sample width in bits.
        """
        return self._sample_width

    @property
    def framerate(self):
        """
        int: Sampling frequency (Hz).
        """
        return self._framerate

    @property
    def n_channels(self):
        """
        int: Number of audio channels.
        """
        return self._n_channels

    @property
    def n_frames(self):
        """
        int: Number of audio frames.
        """
        return self._n_frames

    @property
    def data(self):
        """
        numpy.ndarray: Audio data stored in numpy.ndarray.
            If the number of channels is one, the array will be one dimensional.
            Otherwise, the returned array will be two dimensional array of shape (n_frames, n_channels).
        """
        return self._data

    @property
    def tags(self):
        """
        TODO
        """
        return self._tags

    def __init__(self, sample_width, framerate, data, tags=None):
        """

        Args:
            sample_width (int): Sample width in bits.
            framerate (int): Sampling frequency in Hz.
            data (numpy.ndarray): Audio data.
            tags (Tags): Tags containing information about the audio.
        """

        # copy simple info
        self._sample_width = sample_width
        self._framerate = framerate

        # check data is numpy array
        if not isinstance(data, numpy.ndarray):
            raise wavy.WaveValueError("Argument 'data' must be of type numpy.ndarray.")

        # get array shape (numpy is annoying here)
        self._n_frames, self._n_channels = \
            (data.size, 1) if data.ndim == 1 else data.shape

        # check array is not empty
        if not self._n_frames:
            raise wavy.WaveValueError("Data array cannot be empty.")

        # check that sample width is supported for data dtype
        wavy.detail.check_sample_width_supported(sample_width, data.dtype)

        # if we have tags, it must be a valid Tags obj
        if tags and not isinstance(tags, wavy.Tags):
            raise wavy.WaveValueError("Argument 'tags' must be of type 'wavy.Tags'.")

        self._data = data
        self._tags = tags

    def __repr__(self):
        return f"WaveFile(sample_width={self.sample_width}, " \
               f"framerate={self.framerate}, n_channels={self.n_channels}, " \
               f"n_frames={self.n_frames})"
