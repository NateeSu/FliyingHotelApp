# Bug Fix: Rooms Page Not Displaying

**Date**: October 14, 2025
**Status**: ✅ **FIXED**
**Severity**: Critical
**Affected Endpoint**: `GET /api/v1/rooms/`

## Problem Description

The rooms management page at `http://localhost:5173/rooms` was not displaying any room data. Users reported a blank page with no room listings.

### User Reports

1. Initial report: "ที่หน้า http://localhost:5173/rooms ไม่แสดงห้องพัก"
2. Follow-up: "ที่หน้า http://localhost:5173/rooms ยังไม่แสดงห้องพัก" with error logs

### Error Symptoms

**Frontend (Browser Console)**:
```
Access to XMLHttpRequest at 'http://localhost:8000/api/v1/rooms/' from origin 'http://localhost:5173' has been blocked by CORS policy
GET http://localhost:8000/api/v1/rooms/ net::ERR_FAILED 500 (Internal Server Error)
```

**Backend (Docker Logs)**:
```
TypeError: app.schemas.room.RoomWithRoomType() got multiple values for keyword argument 'room_type'
pydantic_core._pydantic_core.ValidationError: 1 validation error for RoomWithRoomType
```

## Root Cause Analysis

### Issue 1: Pydantic V2 Serialization Error

The `RoomWithRoomType` schema expects `room_type` to be a `dict`, but the code was:
1. Passing `room.__dict__` which already includes `room_type` (SQLAlchemy relationship object)
2. Then explicitly passing `room_type` again, causing duplicate keyword argument error

**Problematic Code** (lines 46-52 in `rooms.py`):
```python
return [
    RoomWithRoomType(
        **room.__dict__,  # ❌ Contains 'room_type' key
        room_type=room.room_type.__dict__  # ❌ Passing 'room_type' again
    )
    for room in rooms
]
```

### Issue 2: Incorrect SQLAlchemy Object Serialization

Even after excluding `room_type` from the dict spread, passing `room.room_type` directly caused Pydantic validation error because:
- Pydantic V2 with `from_attributes=True` can convert SQLAlchemy objects to dicts
- But the schema defined `room_type: Optional[dict]` explicitly
- Need to manually serialize the nested relationship object

## Solution Implemented

### 1. Created Helper Function for Manual Serialization

Added `_serialize_room_with_type()` function to properly convert SQLAlchemy Room and RoomType objects to dictionaries:

```python
def _serialize_room_with_type(room: Room) -> dict:
    """Helper to serialize Room with RoomType to dict"""
    room_dict = {
        "id": room.id,
        "room_number": room.room_number,
        "room_type_id": room.room_type_id,
        "floor": room.floor,
        "status": room.status,
        "qr_code": room.qr_code,
        "notes": room.notes,
        "is_active": room.is_active,
        "created_at": room.created_at,
        "updated_at": room.updated_at,
        "room_type": None
    }

    if room.room_type:
        room_dict["room_type"] = {
            "id": room.room_type.id,
            "name": room.room_type.name,
            "description": room.room_type.description,
            "amenities": room.room_type.amenities,
            "max_guests": room.room_type.max_guests,
            "bed_type": room.room_type.bed_type,
            "room_size_sqm": room.room_type.room_size_sqm,
            "is_active": room.room_type.is_active,
            "created_at": room.room_type.created_at,
            "updated_at": room.room_type.updated_at,
        }

    return room_dict
```

### 2. Updated All Room Endpoints

Applied the fix to **all 7 endpoints** that return `RoomWithRoomType`:

1. `GET /` - List all rooms (line 79)
2. `GET /available` - List available rooms (line 98)
3. `GET /floor/{floor}` - List rooms by floor (line 115)
4. `GET /{room_id}` - Get single room (line 138)
5. `POST /` - Create room (line 158)
6. `PATCH /{room_id}` - Update room (line 178)
7. `PATCH /{room_id}/status` - Update room status (line 201)

**Fixed Code Pattern**:
```python
return [RoomWithRoomType(**_serialize_room_with_type(room)) for room in rooms]
# or for single room:
return RoomWithRoomType(**_serialize_room_with_type(room))
```

### 3. Updated Schema Configuration

Added `from_attributes = True` to `RoomWithRoomType` schema to allow Pydantic to work with ORM objects (lines 52-53 in `schemas/room.py`):

```python
class RoomWithRoomType(RoomResponse):
    """Schema for room response with room type details"""
    room_type: Optional[dict] = Field(None, description="ข้อมูลประเภทห้อง")

    class Config:
        from_attributes = True
```

## Files Modified

1. **`backend/app/api/v1/endpoints/rooms.py`**
   - Added `_serialize_room_with_type()` helper function
   - Updated 7 endpoints to use the helper
   - Added `Room` import

2. **`backend/app/schemas/room.py`**
   - Added `Config` class to `RoomWithRoomType` with `from_attributes = True`

## Testing & Verification

### Before Fix
```bash
GET /api/v1/rooms/ HTTP/1.1" 500 Internal Server Error
TypeError: got multiple values for keyword argument 'room_type'
```

### After Fix
```bash
GET /api/v1/rooms/ HTTP/1.1" 200 OK
```

### Database Query Verification
Backend successfully loads rooms with room_type relationship:
```sql
SELECT rooms.*, room_types.*
FROM rooms
LEFT OUTER JOIN room_types ON room_types.id = rooms.room_type_id
ORDER BY rooms.floor, rooms.room_number
LIMIT 0, 100
```

### API Response Format
```json
[
  {
    "id": 1,
    "room_number": "101",
    "room_type_id": 1,
    "floor": 1,
    "status": "available",
    "qr_code": "ROOM-ABC123",
    "notes": null,
    "is_active": true,
    "created_at": "2025-10-14T...",
    "updated_at": "2025-10-14T...",
    "room_type": {
      "id": 1,
      "name": "Standard Room",
      "description": "ห้องพักมาตรฐาน",
      "amenities": ["TV", "Air Conditioning", "WiFi"],
      "max_guests": 2,
      "bed_type": "Queen",
      "room_size_sqm": 25.0,
      "is_active": true,
      "created_at": "2025-10-14T...",
      "updated_at": "2025-10-14T..."
    }
  }
]
```

## Lessons Learned

### Pydantic V2 Best Practices

1. **Avoid duplicate keyword arguments**: When using `**dict`, ensure you exclude keys that will be passed explicitly
2. **Manual serialization for nested relationships**: For complex nested objects, manual serialization is more reliable than relying on `from_attributes=True`
3. **Type safety**: Using `Optional[dict]` is less type-safe than using the actual schema class (future improvement: use `Optional[RoomTypeResponse]`)

### Debugging Tips

1. **Read error messages carefully**: "got multiple values for keyword argument" immediately points to dict spreading issue
2. **Check backend logs first**: 500 errors are always backend issues, CORS errors are often secondary
3. **Test endpoints directly**: Use curl or Swagger UI to test API endpoints independently of frontend

## Future Improvements

### Option 1: Use Nested Schema (Recommended)
```python
# In schemas/room.py
from app.schemas.room_type import RoomTypeResponse

class RoomWithRoomType(RoomResponse):
    room_type: Optional[RoomTypeResponse] = Field(None, description="ข้อมูลประเภทห้อง")
```

This would enable:
```python
# In endpoints
return [RoomWithRoomType.model_validate(room) for room in rooms]
```

### Option 2: Use BaseModel.model_dump()
```python
return [
    RoomWithRoomType(
        **room.__dict__,
        room_type=room.room_type.model_dump() if room.room_type else None
    )
]
```

## Related Issues

- ✅ Phase 2 completion was blocked by this bug
- ✅ Room management functionality was completely broken
- ✅ Frontend room listing was non-functional

## Status

**Bug Fixed**: ✅ October 14, 2025 07:17 AM
**Endpoints Working**: ✅ All 7 room endpoints return 200 OK
**Frontend Tested**: ⏳ Needs manual verification at http://localhost:5173/rooms

---

*Fixed by Claude Code*
