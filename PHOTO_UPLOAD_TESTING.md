# Photo Upload Feature - Complete Testing Guide

## Overview
This guide walks you through testing the complete photo upload feature for maintenance tasks.

## Features Implemented

### Frontend (Vue 3 + TypeScript)
- ✅ Photo upload input field in MaintenanceCreateModal
- ✅ Support for up to 5 photos per task
- ✅ Image preview grid with thumbnails (100px × 100px)
- ✅ Delete button for each photo
- ✅ File type validation (images only)
- ✅ Error messages for invalid files or too many photos
- ✅ FormData multipart upload

### Backend (FastAPI + Python)
- ✅ Updated MaintenanceTask model with photos field
- ✅ Updated MaintenanceTaskCreate schema to support photo URLs
- ✅ Modified POST /api/v1/maintenance/ endpoint to accept multipart/form-data
- ✅ File upload handling with automatic filename generation
- ✅ Photo storage in uploads/maintenance/ directory
- ✅ Photo URLs stored as JSON array in database
- ✅ Database migration applied

## Testing Steps

### 1. Access the Application
```
Frontend: http://localhost:5173/maintenance
API Docs: http://localhost:8000/docs
```

### 2. Test Photo Upload UI
1. Open http://localhost:5173/maintenance in your browser
2. Click "➕ เพิ่มงานซ่อม" (Add Maintenance Task) button
3. Fill in the form:
   - **ห้อง (Room):** Select a room
   - **หัวข้อ (Title):** Enter task title
   - **รายละเอียด (Description):** Enter description (optional)
   - **ประเภทงาน (Category):** Select category
   - **ลำดับความสำคัญ (Priority):** Select priority

### 3. Test Photo Selection
1. Click "📷 เลือกรูปถ่าย" (Select Photos) button
2. Choose 1-5 image files (JPG, PNG, etc.)
3. Verify preview grid appears below the button
4. Verify each photo shows thumbnail and delete button (✕)

### 4. Test Photo Validation
1. Try to select non-image files:
   - Expected: Error message "กรุณาเลือกเฉพาะไฟล์รูปภาพ"
2. Try to select more than 5 photos:
   - Expected: Error message "อนุญาตได้สูงสุด 5 รูป"

### 5. Test Photo Deletion
1. Click ✕ button on any photo thumbnail
2. Verify the photo is removed from the grid
3. Verify you can select new photos

### 6. Test Form Submission
1. Ensure all required fields are filled
2. Select 1-3 photos
3. Click "บันทึก" (Save) button
4. Expected results:
   - Success message: "เพิ่มงานซ่อมบำรุงสำเร็จ"
   - Form closes
   - Task appears in the maintenance list
   - Photos are uploaded and stored

### 7. Test API Endpoint (using curl or Postman)
```bash
# Example: Create maintenance task with photos
curl -X POST http://localhost:8000/api/v1/maintenance/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "room_id=1" \
  -F "category=PLUMBING" \
  -F "title=Test Task" \
  -F "description=Test description" \
  -F "priority=MEDIUM" \
  -F "photos=@/path/to/photo1.jpg" \
  -F "photos=@/path/to/photo2.jpg"
```

### 8. Verify Database
```bash
# Check that photos are stored in database
docker-compose exec mysql mysql -h localhost -u root -ppassword flying_hotel_db -e \
  "SELECT id, title, photos FROM maintenance_tasks WHERE photos IS NOT NULL LIMIT 1\G"
```

Expected output:
```
photos: ["/uploads/maintenance/maintenance_20251101_153000_photo1.jpg", "/uploads/maintenance/maintenance_20251101_153001_photo2.jpg"]
```

### 9. Verify File Storage
```bash
# Check uploaded files in container
docker-compose exec backend ls -la /app/uploads/maintenance/
```

Expected: Files with names like:
- maintenance_20251101_153000_photo1.jpg
- maintenance_20251101_153001_photo2.jpg

### 10. Test Form Reset
1. Submit a task with photos
2. Form should automatically clear:
   - All text fields empty
   - Photo preview grid hidden
   - Ready for new task creation

## API Endpoint Details

### POST /api/v1/maintenance/
**Content-Type:** multipart/form-data

**Parameters:**
- `room_id` (required): Room ID (integer)
- `category` (required): Task category (string)
- `title` (required): Task title (string)
- `description` (optional): Task description (string)
- `priority` (optional): Task priority (string, default: MEDIUM)
- `assigned_to` (optional): User ID to assign to (integer)
- `notes` (optional): Additional notes (string)
- `photos` (optional): Photo files (array of files, max 5)

**Response:** MaintenanceTaskResponse
```json
{
  "id": 1,
  "room_id": 101,
  "category": "PLUMBING",
  "title": "Leaking faucet",
  "description": "Kitchen faucet is leaking",
  "priority": "MEDIUM",
  "status": "PENDING",
  "created_by": 1,
  "created_at": "2025-11-01T15:30:00",
  "updated_at": "2025-11-01T15:30:00",
  "photos": ["/uploads/maintenance/maintenance_20251101_153000_photo1.jpg"]
}
```

## Troubleshooting

### Photos not saving
1. Verify uploads/maintenance directory exists:
   ```bash
   docker-compose exec backend mkdir -p /app/uploads/maintenance
   ```
2. Check permissions on uploads directory
3. Check backend logs: `docker-compose logs -f backend`

### Form not submitting
1. Ensure all required fields are filled (room, title, category, priority)
2. Check browser console for errors (F12)
3. Check network tab to see API response

### Photos not displayed in list
1. Verify photos are stored in database (step 8)
2. Check that file paths are correct
3. Ensure uploads directory is web-accessible

## Files Modified/Created

**Backend:**
- `backend/app/models/maintenance_task.py` - Added photos field
- `backend/app/schemas/maintenance.py` - Updated schema
- `backend/app/api/v1/endpoints/maintenance.py` - Updated endpoint
- `backend/app/services/maintenance_service.py` - Added photo handling
- `backend/alembic/versions/20251101_1535_add_photos_to_maintenance.py` - Migration

**Frontend:**
- `frontend/src/components/MaintenanceCreateModal.vue` - Added photo upload UI
- `frontend/src/types/maintenance.ts` - Updated types

## Success Criteria

✅ All tests pass
✅ Photos upload successfully
✅ Photos display in preview grid before submission
✅ Photos are stored in database as JSON array
✅ Photos are saved to uploads/maintenance directory
✅ Form resets after successful submission
✅ Error messages display for validation failures

---
**Status:** Ready for testing ✅
**Date:** 2025-11-01
**Version:** 1.0
