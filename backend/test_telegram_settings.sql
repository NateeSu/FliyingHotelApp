-- Update Telegram Settings
UPDATE system_settings SET value='8295435980:AAGW6okI79lgJtJR674cevYWUGmgSVxDYqU' WHERE `key`='telegram_bot_token';
UPDATE system_settings SET value='8324712085' WHERE `key`='telegram_housekeeping_chat_id';
UPDATE system_settings SET value='8324712085' WHERE `key`='telegram_maintenance_chat_id';
UPDATE system_settings SET value='true' WHERE `key`='telegram_enabled';

-- Check results
SELECT * FROM system_settings WHERE `key` LIKE 'telegram%';
