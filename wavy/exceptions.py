
class WavyException(Exception):
    """
    Generic exception class for Wavy module.
    """
    pass


class WaveFileNotSupported(WavyException):
    """
    Exception for when file types are not supported.
    """
    pass


class WaveFileIsCorrupted(WavyException):
    """
    Exception for when files are corrupted.
    """
    pass
