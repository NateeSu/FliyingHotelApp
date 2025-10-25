-- Clear Test Data SQL Script
-- This script removes all test check-in, booking, and related data
-- while preserving system data (users, rooms, room types, products, settings)
--
-- WARNING: This will permanently delete data. Make sure to backup first!

-- Disable foreign key checks temporarily
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Delete all check-ins and related data
DELETE FROM check_ins WHERE id > 0;
DELETE FROM bookings WHERE id > 0;
DELETE FROM payments WHERE id > 0;

-- 2. Delete all customer records (test customers)
-- Keep only if you want to preserve customer history
DELETE FROM customers WHERE id > 0;

-- 3. Delete activity logs (test records)
DELETE FROM activity_logs WHERE id > 0;

-- 4. Delete notifications (test notifications)
DELETE FROM notifications WHERE id > 0;

-- 5. Reset room status to available (clean state)
UPDATE rooms SET status = 'available' WHERE status != 'out_of_service';

-- 6. Delete housekeeping tasks (auto-created from check-outs)
DELETE FROM housekeeping_tasks WHERE id > 0;

-- 7. Delete maintenance tasks (test tasks)
DELETE FROM maintenance_tasks WHERE id > 0;

-- 8. Reset auto-increment counters
ALTER TABLE check_ins AUTO_INCREMENT = 1;
ALTER TABLE bookings AUTO_INCREMENT = 1;
ALTER TABLE payments AUTO_INCREMENT = 1;
ALTER TABLE customers AUTO_INCREMENT = 1;
ALTER TABLE activity_logs AUTO_INCREMENT = 1;
ALTER TABLE notifications AUTO_INCREMENT = 1;
ALTER TABLE housekeeping_tasks AUTO_INCREMENT = 1;
ALTER TABLE maintenance_tasks AUTO_INCREMENT = 1;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Verify cleanup
SELECT 'Database cleanup complete!' as status;
SELECT COUNT(*) as check_ins FROM check_ins;
SELECT COUNT(*) as bookings FROM bookings;
SELECT COUNT(*) as payments FROM payments;
SELECT COUNT(*) as customers FROM customers;
SELECT COUNT(*) as rooms_available FROM rooms WHERE status = 'available';
SELECT COUNT(*) as housekeeping_tasks FROM housekeeping_tasks;
SELECT COUNT(*) as maintenance_tasks FROM maintenance_tasks;
