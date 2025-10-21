-- Create system_settings table
CREATE TABLE IF NOT EXISTS system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(255) NOT NULL UNIQUE,
    value TEXT,
    data_type ENUM('string', 'number', 'json', 'boolean') NOT NULL DEFAULT 'string',
    description TEXT,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_settings_key (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default Telegram settings
INSERT INTO system_settings (`key`, value, data_type, description) VALUES
('telegram_bot_token', '', 'string', 'Telegram Bot API Token'),
('telegram_admin_chat_id', '', 'string', 'Telegram Admin Group Chat ID'),
('telegram_reception_chat_id', '', 'string', 'Telegram Reception Group Chat ID'),
('telegram_housekeeping_chat_id', '', 'string', 'Telegram Housekeeping Group Chat ID'),
('telegram_maintenance_chat_id', '', 'string', 'Telegram Maintenance Group Chat ID'),
('telegram_enabled', 'false', 'boolean', 'Enable/Disable Telegram notifications')
ON DUPLICATE KEY UPDATE `key`=`key`;
