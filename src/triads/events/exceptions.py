"""Exception classes for event sourcing system."""


class EventStorageError(Exception):
    """Base exception for event storage operations.
    
    Raised when saving, updating, or deleting events fails.
    """
    pass


class EventQueryError(Exception):
    """Exception for event query operations.
    
    Raised when querying or filtering events fails.
    """
    pass


class InvalidEventError(Exception):
    """Exception for invalid event data.
    
    Raised when event data doesn't meet validation requirements.
    """
    pass
