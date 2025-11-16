"""
Breaker Helper Functions

Utility functions for breaker state conversion, validation, and formatting.
"""
from typing import Dict, Any, Optional
from app.models.home_assistant import BreakerState, TargetState
from app.models.room import RoomStatus


def ha_state_to_breaker_state(ha_state: str) -> BreakerState:
    """
    Convert Home Assistant state string to BreakerState enum.

    Args:
        ha_state: Home Assistant state (e.g., "on", "off", "unavailable")

    Returns:
        BreakerState enum value

    Example:
        >>> ha_state_to_breaker_state("on")
        BreakerState.ON
    """
    ha_state = ha_state.lower()

    if ha_state == "on":
        return BreakerState.ON
    elif ha_state == "off":
        return BreakerState.OFF
    else:
        return BreakerState.UNAVAILABLE


def breaker_state_to_display(state: BreakerState) -> Dict[str, Any]:
    """
    Convert BreakerState to display-friendly format.

    Args:
        state: BreakerState enum

    Returns:
        Dict with Thai label, color, and icon

    Example:
        >>> breaker_state_to_display(BreakerState.ON)
        {"label": "เปิด", "color": "success", "icon": "power"}
    """
    state_map = {
        BreakerState.ON: {
            "label": "เปิด",
            "color": "success",
            "icon": "power",
            "badge_color": "green"
        },
        BreakerState.OFF: {
            "label": "ปิด",
            "color": "default",
            "icon": "power-off",
            "badge_color": "gray"
        },
        BreakerState.UNAVAILABLE: {
            "label": "ไม่พร้อมใช้งาน",
            "color": "error",
            "icon": "alert-circle",
            "badge_color": "red"
        }
    }

    return state_map.get(state, state_map[BreakerState.UNAVAILABLE])


def room_status_requires_breaker_on(status: RoomStatus) -> bool:
    """
    Check if room status requires breaker to be ON.

    Business Logic:
    - OCCUPIED: breaker ON (guest is in room)
    - CLEANING: breaker ON (staff needs power for cleaning)
    - AVAILABLE: breaker OFF (save energy)
    - RESERVED: breaker OFF (not yet checked in)
    - OUT_OF_SERVICE: breaker OFF (maintenance mode)

    Args:
        status: Room status

    Returns:
        True if breaker should be ON, False otherwise
    """
    return status in [RoomStatus.OCCUPIED, RoomStatus.CLEANING]


def determine_target_breaker_state(room_status: RoomStatus) -> TargetState:
    """
    Determine target breaker state based on room status.

    Args:
        room_status: Current room status

    Returns:
        Target breaker state (ON or OFF)

    Example:
        >>> determine_target_breaker_state(RoomStatus.OCCUPIED)
        TargetState.ON
        >>> determine_target_breaker_state(RoomStatus.AVAILABLE)
        TargetState.OFF
    """
    if room_status_requires_breaker_on(room_status):
        return TargetState.ON
    else:
        return TargetState.OFF


def validate_entity_id_format(entity_id: str) -> bool:
    """
    Validate Home Assistant entity ID format.

    Format: domain.entity_name (e.g., "switch.room_101_breaker")

    Args:
        entity_id: Entity ID to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_entity_id_format("switch.room_101_breaker")
        True
        >>> validate_entity_id_format("invalid")
        False
    """
    if not entity_id or '.' not in entity_id:
        return False

    parts = entity_id.split('.')
    if len(parts) != 2:
        return False

    domain, entity_name = parts

    # Check domain (common domains)
    valid_domains = ['switch', 'light', 'fan', 'cover']
    if domain not in valid_domains:
        return False

    # Check entity name (alphanumeric and underscore only)
    if not entity_name or not entity_name.replace('_', '').isalnum():
        return False

    return True


def extract_room_number_from_entity_id(entity_id: str) -> Optional[str]:
    """
    Extract room number from entity ID if it follows naming convention.

    Convention: switch.room_101_breaker -> "101"

    Args:
        entity_id: Entity ID

    Returns:
        Room number string or None if not found

    Example:
        >>> extract_room_number_from_entity_id("switch.room_101_breaker")
        "101"
        >>> extract_room_number_from_entity_id("switch.main_breaker")
        None
    """
    import re

    # Try to find room number pattern: room_XXX
    match = re.search(r'room[_-](\d+)', entity_id, re.IGNORECASE)
    if match:
        return match.group(1)

    return None


def format_response_time(response_time_ms: Optional[int]) -> str:
    """
    Format response time for display.

    Args:
        response_time_ms: Response time in milliseconds

    Returns:
        Formatted string (e.g., "234 ms", "1.2 s")

    Example:
        >>> format_response_time(234)
        "234 ms"
        >>> format_response_time(1234)
        "1.2 s"
    """
    if response_time_ms is None:
        return "N/A"

    if response_time_ms < 1000:
        return f"{response_time_ms} ms"
    else:
        seconds = response_time_ms / 1000
        return f"{seconds:.1f} s"


def calculate_energy_savings(
    breakers_off_count: int,
    estimated_power_per_breaker_watts: int = 100
) -> Dict[str, Any]:
    """
    Calculate estimated energy savings.

    Args:
        breakers_off_count: Number of breakers currently OFF
        estimated_power_per_breaker_watts: Estimated power consumption per breaker

    Returns:
        Dict with energy savings metrics

    Example:
        >>> calculate_energy_savings(10)
        {"watts_saved": 1000, "kwh_per_day": 24.0, "baht_per_day": 96.0}
    """
    watts_saved = breakers_off_count * estimated_power_per_breaker_watts
    kwh_per_day = (watts_saved * 24) / 1000  # Convert to kWh
    baht_per_day = kwh_per_day * 4  # Assuming 4 baht per kWh

    return {
        "breakers_off": breakers_off_count,
        "watts_saved": watts_saved,
        "kwh_per_day": round(kwh_per_day, 2),
        "baht_per_day": round(baht_per_day, 2),
        "estimated_power_per_breaker_watts": estimated_power_per_breaker_watts
    }


def should_trigger_admin_notification(consecutive_errors: int, threshold: int = 3) -> bool:
    """
    Check if admin should be notified about breaker errors.

    Args:
        consecutive_errors: Number of consecutive errors
        threshold: Error threshold for notification

    Returns:
        True if notification should be sent

    Example:
        >>> should_trigger_admin_notification(3)
        True
        >>> should_trigger_admin_notification(2)
        False
    """
    return consecutive_errors >= threshold


def format_breaker_name_suggestion(room_number: str) -> str:
    """
    Generate suggested breaker name based on room number.

    Args:
        room_number: Room number

    Returns:
        Suggested friendly name

    Example:
        >>> format_breaker_name_suggestion("101")
        "Breaker ห้อง 101"
    """
    return f"Breaker ห้อง {room_number}"


def parse_debounce_config(config_value: Any, default_seconds: int = 3) -> int:
    """
    Parse debounce configuration value.

    Args:
        config_value: Config value (int, str, or None)
        default_seconds: Default debounce time

    Returns:
        Debounce time in seconds

    Example:
        >>> parse_debounce_config("5")
        5
        >>> parse_debounce_config(None)
        3
    """
    if config_value is None:
        return default_seconds

    try:
        return int(config_value)
    except (ValueError, TypeError):
        return default_seconds
