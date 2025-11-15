"""Workaround hooks for the Tuya Custom integration.

These helpers give you dedicated entry points to add the polling and
state-estimation logic you need for curtain motors that never push
updates through Tuya Cloud.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from .const import LOGGER

if TYPE_CHECKING:  # pragma: no cover - only used for typing hints
    from tuya_sharing import Manager

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity import Entity
    from . import TuyaConfigEntry


async def polling_fallback(
    hass: "HomeAssistant",
    entry: "TuyaConfigEntry",
    manager: "Manager",
) -> None:
    """Placeholder to enable periodic polling against Tuya Cloud.

    Add your own schedule here to fetch updated DP states when MQTT never
    arrives. The typical pattern is:
    1. Use ``hass.helpers.event.async_track_time_interval`` with your
       desired interval (for example every 15 seconds – adjust as needed).
    2. Inside the callback call ``await hass.async_add_executor_job(
           manager.update_device_cache
       )`` to refresh Tuya's device cache.
    3. Dispatch state updates to entities (``manager.device_map`` is
       automatically updated by the Tuya SDK).

    This function is intentionally empty so you can tailor it to your
    hardware and quota limits.
    """

    LOGGER.debug(
        "polling_fallback placeholder invoked for entry %s; no polling is scheduled yet",
        entry.entry_id,
    )


def optimistic_cover_update(
    entity: "Entity",
    *,
    operation: str,
    target_position: int | None = None,
    assumed_dpcode: str | None = None,
) -> None:
    """Optimistically update cover state immediately after a command.

    Implement your local DP estimation here. Recommended steps:
    - Update ``entity.device.status[assumed_dpcode]`` with the expected
      value (e.g. 0 for close, 100 for open, or the requested percentage).
    - Call ``entity.async_write_ha_state()`` so Home Assistant reflects the
      assumed state while waiting for cloud confirmation.

    The helper currently just logs so the default behaviour matches the
    official integration. Extend it to store whatever optimistic state you
    need.
    """

    LOGGER.debug(
        "optimistic_cover_update placeholder for %s: operation=%s, target_position=%s, dpcode=%s",
        getattr(entity, "entity_id", "unknown"),
        operation,
        target_position,
        assumed_dpcode,
    )


async def post_command_refresh(
    hass: "HomeAssistant",
    manager: "Manager",
    device_id: str,
    delay: float = 2.0,
) -> None:
    """Force a one-off refresh after commands complete.

    Customize this to guarantee that a device refresh runs shortly after
    sending open/close/stop commands.

    Suggested implementation:
        await asyncio.sleep(delay)
        await hass.async_add_executor_job(manager.update_device, device_id)

    For full-cache refreshes, replace ``update_device`` with
    ``update_device_cache`` or any bespoke API call you need. Adjust the
    ``delay`` parameter when calling this helper to match the curtain
    travel time.
    """

    LOGGER.debug(
        "post_command_refresh placeholder triggered for %s; delay=%s (no refresh performed)",
        device_id,
        delay,
    )
    # When you are ready to enable the workaround, replace the debug
    # statement with the forced refresh logic described above.
    await asyncio.sleep(0)
