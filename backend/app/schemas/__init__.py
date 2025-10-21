"""
Schemas package
Contains all Pydantic schemas for API validation
"""
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    LoginRequest,
    LoginResponse,
    UserRole
)
from .room_type import (
    RoomTypeBase,
    RoomTypeCreate,
    RoomTypeUpdate,
    RoomTypeResponse,
    RoomTypeWithStats
)
from .room import (
    RoomBase,
    RoomCreate,
    RoomUpdate,
    RoomResponse,
    RoomWithRoomType,
    RoomStatusUpdate,
    RoomListResponse
)
from .room_rate import (
    RoomRateBase,
    RoomRateCreate,
    RoomRateUpdate,
    RoomRateResponse,
    RoomRateWithRoomType,
    RoomRateMatrix
)
from .notification import (
    NotificationBase,
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
    NotificationMarkAllReadResponse
)
from .check_in import (
    CheckInCreate,
    CheckInUpdate,
    CheckInResponse,
    CheckInWithDetails,
    CheckInListResponse,
    CheckOutRequest,
    CheckOutSummary
)
from .customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerSearchResult,
    CustomerListResponse
)
from .dashboard import (
    DashboardRoomCard,
    DashboardStats,
    DashboardResponse,
    OvertimeAlert,
    OvertimeAlertsResponse
)
from .housekeeping import (
    HousekeepingTaskCreate,
    HousekeepingTaskUpdate,
    HousekeepingTaskResponse,
    HousekeepingTaskWithDetails,
    HousekeepingTaskListResponse,
    HousekeepingTaskStartRequest,
    HousekeepingTaskCompleteRequest,
    HousekeepingStats
)
from .booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingListResponse,
    BookingCalendarEvent,
    PublicHoliday,
    RoomAvailabilityCheck,
    RoomAvailabilityResponse,
    BookingConfirmRequest,
    BookingStats,
    BookingReminderData
)
from .product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse
)
