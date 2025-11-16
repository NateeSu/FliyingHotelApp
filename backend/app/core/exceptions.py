"""
Custom Exception Classes for FlyingHotelApp

Provides specific exceptions for different error scenarios.
"""
from fastapi import HTTPException, status


# ============================================================================
# Home Assistant Exceptions
# ============================================================================

class HomeAssistantException(HTTPException):
    """Base exception for Home Assistant related errors"""
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)


class HomeAssistantNotConfiguredError(HomeAssistantException):
    """Raised when Home Assistant is not configured"""
    def __init__(self, detail: str = "Home Assistant ยังไม่ได้ตั้งค่า"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class HomeAssistantConnectionError(HomeAssistantException):
    """Raised when cannot connect to Home Assistant"""
    def __init__(self, detail: str = "ไม่สามารถเชื่อมต่อ Home Assistant ได้"):
        super().__init__(detail=detail, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class HomeAssistantAuthError(HomeAssistantException):
    """Raised when authentication fails"""
    def __init__(self, detail: str = "การยืนยันตัวตน Home Assistant ล้มเหลว (Access Token ไม่ถูกต้อง)"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class HomeAssistantTimeoutError(HomeAssistantException):
    """Raised when request times out"""
    def __init__(self, detail: str = "Home Assistant ไม่ตอบกลับภายในเวลาที่กำหนด"):
        super().__init__(detail=detail, status_code=status.HTTP_504_GATEWAY_TIMEOUT)


class HomeAssistantAPIError(HomeAssistantException):
    """Raised when Home Assistant API returns an error"""
    def __init__(self, detail: str = "Home Assistant API ส่งคืน error"):
        super().__init__(detail=detail, status_code=status.HTTP_502_BAD_GATEWAY)


# ============================================================================
# Breaker Exceptions
# ============================================================================

class BreakerException(HTTPException):
    """Base exception for Breaker related errors"""
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)


class BreakerNotFoundError(BreakerException):
    """Raised when breaker is not found"""
    def __init__(self, detail: str = "ไม่พบ breaker นี้ในระบบ"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class BreakerUnavailableError(BreakerException):
    """Raised when breaker is unavailable in Home Assistant"""
    def __init__(self, detail: str = "Breaker นี้ไม่พร้อมใช้งานใน Home Assistant"):
        super().__init__(detail=detail, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class BreakerControlError(BreakerException):
    """Raised when breaker control command fails"""
    def __init__(self, detail: str = "ไม่สามารถควบคุม breaker ได้"):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BreakerAlreadyExistsError(BreakerException):
    """Raised when trying to create a breaker that already exists"""
    def __init__(self, detail: str = "Breaker นี้มีอยู่แล้วในระบบ"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class BreakerRoomConflictError(BreakerException):
    """Raised when room already has a breaker assigned"""
    def __init__(self, detail: str = "ห้องนี้มี breaker กำหนดอยู่แล้ว"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# Encryption Exceptions
# ============================================================================

class EncryptionError(HTTPException):
    """Base exception for encryption/decryption errors"""
    def __init__(self, detail: str = "เกิดข้อผิดพลาดในการเข้ารหัส/ถอดรหัส"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class DecryptionError(EncryptionError):
    """Raised when decryption fails"""
    def __init__(self, detail: str = "ไม่สามารถถอดรหัสข้อมูลได้ (key อาจไม่ถูกต้อง)"):
        super().__init__(detail=detail)
