class InpaintException(Exception):
    """Base exception for inpainting operations"""
    pass


class ModelNotLoadedException(InpaintException):
    """Exception raised when model is not loaded"""
    pass


class InvalidImageException(InpaintException):
    """Exception raised for invalid image data"""
    pass


class ProcessingTimeoutException(InpaintException):
    """Exception raised when processing takes too long"""
    pass


class InvalidCoordinatesException(InpaintException):
    """Exception raised for invalid point coordinates"""
    pass


class FileTooLargeException(InpaintException):
    """Exception raised when file size exceeds limit"""
    pass


class UnsupportedImageFormatException(InpaintException):
    """Exception raised for unsupported image formats"""
    pass