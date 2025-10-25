import axios from './client'

export interface TelegramSettings {
  bot_token: string
  admin_chat_id: string
  reception_chat_id: string
  housekeeping_chat_id: string
  maintenance_chat_id: string
  enabled: boolean
}

export interface GeneralSettings {
  frontend_domain: string
}

export interface SystemSettings {
  telegram: TelegramSettings
  general: GeneralSettings
}

export interface TelegramTestResponse {
  success: boolean
  message: string
  bot_info?: {
    id: number
    is_bot: boolean
    first_name: string
    username?: string
  }
}

/**
 * Get all system settings (Admin only)
 */
export const getSettings = async (): Promise<SystemSettings> => {
  const response = await axios.get<SystemSettings>('/settings')
  return response.data
}

/**
 * Update system settings (Admin only)
 */
export const updateSettings = async (settings: Partial<SystemSettings>): Promise<SystemSettings> => {
  const response = await axios.put<SystemSettings>('/settings', settings)
  return response.data
}

/**
 * Test Telegram bot connection (Admin only)
 */
export const testTelegramConnection = async (
  botToken: string,
  chatId: string
): Promise<TelegramTestResponse> => {
  const response = await axios.post<TelegramTestResponse>(
    '/settings/test-telegram',
    null,
    {
      params: {
        bot_token: botToken,
        chat_id: chatId
      }
    }
  )
  return response.data
}
