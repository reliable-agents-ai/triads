"""Custom exceptions for agent upgrade system.

Provides domain-specific exception hierarchy for better error handling
and more meaningful error messages in upgrade operations.
"""


class UpgradeError(Exception):
    """Base exception for agent upgrade operations.
    
    All upgrade-related exceptions inherit from this base class,
    making it easy to catch upgrade-specific errors.
    """
    pass


class InvalidAgentError(UpgradeError):
    """Agent file validation failed.
    
    Raised when agent file structure or content is invalid.
    """
    
    def __init__(self, agent_path: str, reason: str):
        """Initialize with agent path and reason.
        
        Args:
            agent_path: Path to invalid agent file
            reason: Human-readable description of validation failure
        """
        self.agent_path = agent_path
        self.reason = reason
        super().__init__(f"Invalid agent {agent_path}: {reason}")


class UpgradeSecurityError(UpgradeError):
    """Security validation failed (path traversal, unsafe paths).
    
    Raised when security checks detect potentially malicious input.
    """
    
    def __init__(self, path: str, violation: str):
        """Initialize with path and violation description.
        
        Args:
            path: Path that triggered security violation
            violation: Description of security violation detected
        """
        self.path = path
        self.violation = violation
        super().__init__(f"Security violation for {path}: {violation}")


class UpgradeIOError(UpgradeError):
    """File I/O operation failed during upgrade.
    
    Wraps underlying I/O errors with upgrade context.
    """
    
    def __init__(self, operation: str, path: str, cause: Exception):
        """Initialize with operation, path, and underlying cause.
        
        Args:
            operation: Description of I/O operation (e.g., "backup_creation")
            path: File path where operation failed
            cause: Underlying exception that caused the failure
        """
        self.operation = operation
        self.path = path
        self.cause = cause
        super().__init__(f"{operation} failed for {path}: {cause}")


class AgentNotFoundError(UpgradeError):
    """Requested agent or agents directory not found.
    
    Raised when agents directory doesn't exist or specific agent not found.
    """
    pass
