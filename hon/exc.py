class InvalidBookError(Exception):
    """Raised if a book is invalid, usually raised when a NoneType is passed in
    place of a Book object."""