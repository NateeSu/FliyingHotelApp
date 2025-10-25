-- Script to clear test data from database
-- This will clear: check-ins, check-outs, bookings, customers
-- WARNING: This will permanently delete data!

-- Disable foreign key checks temporarily
SET FOREIGN_KEY_CHECKS = 0;

-- Clear check-ins and check-outs
DELETE FROM check_ins;

-- Clear bookings
DELETE FROM bookings;

-- Clear customers
DELETE FROM customers;

-- Clear orders (if any)
DELETE FROM orders WHERE 1=1;

-- Clear housekeeping tasks
DELETE FROM housekeeping_tasks WHERE 1=1;

-- Clear maintenance tasks (if table exists)
DELETE FROM maintenance_tasks WHERE 1=1;

-- Clear notifications
DELETE FROM notifications WHERE 1=1;

-- Clear activity logs (if table exists)
-- Note: This table may not exist yet
-- DELETE FROM activity_logs WHERE 1=1;

-- Reset room status to available
UPDATE rooms
SET status = 'AVAILABLE',
    updated_at = NOW()
WHERE status IN ('OCCUPIED', 'CLEANING', 'RESERVED');

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Show summary
SELECT 'Data cleared successfully!' as message;
SELECT
    (SELECT COUNT(*) FROM check_ins) as check_ins_count,
    (SELECT COUNT(*) FROM bookings) as bookings_count,
    (SELECT COUNT(*) FROM customers) as customers_count,
    (SELECT COUNT(*) FROM orders) as orders_count,
    (SELECT COUNT(*) FROM housekeeping_tasks) as housekeeping_count,
    (SELECT COUNT(*) FROM rooms WHERE status = 'AVAILABLE') as available_rooms,
    (SELECT COUNT(*) FROM rooms WHERE status = 'OCCUPIED') as occupied_rooms,
    (SELECT COUNT(*) FROM rooms WHERE status = 'RESERVED') as reserved_rooms;
