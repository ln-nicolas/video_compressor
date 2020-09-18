class VideoCompressorException(Exception):
    pass


class MissingLibraryError(VideoCompressorException):
    pass


class InvalidVideoInput(VideoCompressorException):
    pass
