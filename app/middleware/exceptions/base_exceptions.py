
class ServiceError(Exception):
    """Base class for all service-layer exceptions."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message