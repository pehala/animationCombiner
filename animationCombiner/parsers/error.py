class ParserError(Exception):
    """Error which indicates that something went wrong while parsing file"""

    def __init__(self, message, *args: object) -> None:
        self.message = message
        super().__init__(message, *args)
