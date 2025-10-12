"""
Time validation utilities for regional challenge start times.
"""
from datetime import datetime, timezone
from typing import Optional

async def is_challenge_open(region: str, db) -> tuple[bool, Optional[datetime]]:
    """
    Check if the challenge has opened for a specific region.

    Args:
        region: The region code (EMEA, AMRS, or APAC)
        db: Database connection

    Returns:
        Tuple of (is_open: bool, start_time: datetime)
    """
    # Get regional start times configuration
    config = await db.challenges.find_one({"regional_start_times": {"$exists": True}})

    if not config or "regional_start_times" not in config:
        # If no config exists, allow access (for development/testing)
        return True, None

    start_time_str = config["regional_start_times"].get(region)
    if not start_time_str:
        # Region not configured, allow access
        return True, None

    # Parse ISO format UTC time and make current time timezone-aware
    start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
    current_time = datetime.now(timezone.utc)  # Use timezone-aware current time

    is_open = current_time >= start_time
    return is_open, start_time


def format_utc_time(dt: datetime) -> str:
    """
    Format datetime as UTC string for display.

    Args:
        dt: datetime object

    Returns:
        Formatted string like "2025-10-15 08:00:00 UTC"
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
