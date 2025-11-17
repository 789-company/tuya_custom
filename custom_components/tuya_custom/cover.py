"""Support for Tuya Cover."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tuya_sharing import CustomerDevice, Manager

# Import workaround functions for Tuya Cloud state update issues
# Uncomment the line below to enable workarounds
# from .workarounds import polling_fallback, post_command_refresh, optimistic_cover_update

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityDescription,
    CoverEntityFeature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import TuyaConfigEntry
from .const import TUYA_DISCOVERY_NEW, DeviceCategory, DPCode, DPType
from .entity import TuyaEntity
from .models import DPCodeIntegerWrapper, find_dpcode
from .util import get_dpcode


class _DPCodePercentageMappingWrapper(DPCodeIntegerWrapper):
    """Wrapper for DPCode position values mapping to 0-100 range."""

    def _position_reversed(self, device: CustomerDevice) -> bool:
        """Check if the position and direction should be reversed."""
        return False

    def read_device_status(self, device: CustomerDevice) -> float | None:
        if (value := self._read_device_status_raw(device)) is None:
            return None

        return round(
            self.type_information.remap_value_to(
                value,
                0,
                100,
                self._position_reversed(device),
            )
        )

    def _convert_value_to_raw_value(self, device: CustomerDevice, value: Any) -> Any:
        return round(
            self.type_information.remap_value_from(
                value,
                0,
                100,
                self._position_reversed(device),
            )
        )


class _InvertedPercentageMappingWrapper(_DPCodePercentageMappingWrapper):
    """Wrapper for DPCode position values mapping to 0-100 range."""

    def _position_reversed(self, device: CustomerDevice) -> bool:
        """Check if the position and direction should be reversed."""
        return True


class _ControlBackModePercentageMappingWrapper(_DPCodePercentageMappingWrapper):
    """Wrapper for DPCode position values with control_back_mode support."""

    def _position_reversed(self, device: CustomerDevice) -> bool:
        """Check if the position and direction should be reversed."""
        return device.status.get(DPCode.CONTROL_BACK_MODE) != "back"


@dataclass(frozen=True)
class TuyaCoverEntityDescription(CoverEntityDescription):
    """Describe an Tuya cover entity."""

    current_state: DPCode | tuple[DPCode, ...] | None = None
    current_state_inverse: bool = False
    current_position: DPCode | tuple[DPCode, ...] | None = None
    position_wrapper: type[_DPCodePercentageMappingWrapper] = (
        _InvertedPercentageMappingWrapper
    )
    set_position: DPCode | None = None
    open_instruction_value: str = "open"
    close_instruction_value: str = "close"
    stop_instruction_value: str = "stop"


COVERS: dict[DeviceCategory, tuple[TuyaCoverEntityDescription, ...]] = {
    DeviceCategory.CKMKZQ: (
        TuyaCoverEntityDescription(
            key=DPCode.SWITCH_1,
            translation_key="indexed_door",
            translation_placeholders={"index": "1"},
            current_state=DPCode.DOORCONTACT_STATE,
            current_state_inverse=True,
            device_class=CoverDeviceClass.GARAGE,
        ),
        TuyaCoverEntityDescription(
            key=DPCode.SWITCH_2,
            translation_key="indexed_door",
            translation_placeholders={"index": "2"},
            current_state=DPCode.DOORCONTACT_STATE_2,
            current_state_inverse=True,
            device_class=CoverDeviceClass.GARAGE,
        ),
        TuyaCoverEntityDescription(
            key=DPCode.SWITCH_3,
            translation_key="indexed_door",
            translation_placeholders={"index": "3"},
            current_state=DPCode.DOORCONTACT_STATE_3,
            current_state_inverse=True,
            device_class=CoverDeviceClass.GARAGE,
        ),
    ),
    DeviceCategory.CL: (
        TuyaCoverEntityDescription(
            key=DPCode.CONTROL,
            translation_key="curtain",
            current_state=(DPCode.SITUATION_SET, DPCode.CONTROL),
            current_position=(DPCode.PERCENT_STATE, DPCode.PERCENT_CONTROL),
            set_position=DPCode.PERCENT_CONTROL,
            device_class=CoverDeviceClass.CURTAIN,
        ),
        TuyaCoverEntityDescription(
            key=DPCode.CONTROL_2,
            translation_key="indexed_curtain",
            translation_placeholders={"index": "2"},
            current_position=DPCode.PERCENT_STATE_2,
            set_position=DPCode.PERCENT_CONTROL_2,
            device_class=CoverDeviceClass.CURTAIN,
        ),
        TuyaCoverEntityDescription(
            key=DPCode.CONTROL_3,
            translation_key="indexed_curtain",
            translation_placeholders={"index": "3"},
            current_position=DPCode.PERCENT_STATE_3,
            set_position=DPCode.PERCENT_CONTROL_3,
            device_class=CoverDeviceClass.CURTAIN,
        ),
        TuyaCoverEntityDescription(
            key=DPCode.MACH_OPERATE,
            translation_key="curtain",
            current_position=DPCode.POSITION,
            set_position=DPCode.POSITION,
            device_class=CoverDeviceClass.CURTAIN,
            open_instruction_value="FZ",
            close_instruction_value="ZZ",
            stop_instruction_value="STOP",
        ),
        # switch_1 is an undocumented code that behaves identically to control
        # It is used by the Kogan Smart Blinds Driver
        TuyaCoverEntityDescription(
            key=DPCode.SWITCH_1,
            translation_key="blind",
            current_position=DPCode.PERCENT_CONTROL,
            set_position=DPCode.PERCENT_CONTROL,
            device_class=CoverDeviceClass.BLIND,
        ),
    ),
    DeviceCategory.CLKG: (
        TuyaCoverEntityDescription(
            key=DPCode.CONTROL,
            translation_key="curtain",
            current_position=DPCode.PERCENT_CONTROL,
            position_wrapper=_ControlBackModePercentageMappingWrapper,
            set_position=DPCode.PERCENT_CONTROL,
            device_class=CoverDeviceClass.CURTAIN,
        ),
        TuyaCoverEntityDescription(
            key=DPCode.CONTROL_2,
            translation_key="indexed_curtain",
            translation_placeholders={"index": "2"},
            current_position=DPCode.PERCENT_CONTROL_2,
            position_wrapper=_ControlBackModePercentageMappingWrapper,
            set_position=DPCode.PERCENT_CONTROL_2,
            device_class=CoverDeviceClass.CURTAIN,
        ),
    ),
    DeviceCategory.JDCLJQR: (
        TuyaCoverEntityDescription(
            key=DPCode.CONTROL,
            translation_key="curtain",
            current_position=DPCode.PERCENT_STATE,
            set_position=DPCode.PERCENT_CONTROL,
            device_class=CoverDeviceClass.CURTAIN,
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TuyaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Tuya cover dynamically through Tuya discovery."""
    manager = entry.runtime_data.manager

    @callback
    def async_discover_device(device_ids: list[str]) -> None:
        """Discover and add a discovered tuya cover."""
        entities: list[TuyaCoverEntity] = []
        for device_id in device_ids:
            device = manager.device_map[device_id]
            if descriptions := COVERS.get(device.category):
                entities.extend(
                    TuyaCoverEntity(
                        device,
                        manager,
                        description,
                        current_position=description.position_wrapper.find_dpcode(
                            device, description.current_position
                        ),
                        set_position=description.position_wrapper.find_dpcode(
                            device, description.set_position, prefer_function=True
                        ),
                        tilt_position=description.position_wrapper.find_dpcode(
                            device,
                            (DPCode.ANGLE_HORIZONTAL, DPCode.ANGLE_VERTICAL),
                            prefer_function=True,
                        ),
                    )
                    for description in descriptions
                    if (
                        description.key in device.function
                        or description.key in device.status_range
                    )
                )

        async_add_entities(entities)

    async_discover_device([*manager.device_map])

    entry.async_on_unload(
        async_dispatcher_connect(hass, TUYA_DISCOVERY_NEW, async_discover_device)
    )


class TuyaCoverEntity(TuyaEntity, CoverEntity):
    """Tuya Cover Device."""

    _current_state: DPCode | None = None
    entity_description: TuyaCoverEntityDescription

    def __init__(
        self,
        device: CustomerDevice,
        device_manager: Manager,
        description: TuyaCoverEntityDescription,
        *,
        current_position: _DPCodePercentageMappingWrapper | None = None,
        set_position: _DPCodePercentageMappingWrapper | None = None,
        tilt_position: _DPCodePercentageMappingWrapper | None = None,
    ) -> None:
        """Init Tuya Cover."""
        super().__init__(device, device_manager)
        self.entity_description = description
        self._attr_unique_id = f"{super().unique_id}{description.key}"
        self._attr_supported_features = CoverEntityFeature(0)

        self._current_position = current_position or set_position
        self._set_position = set_position
        self._tilt_position = tilt_position
        
        # ============================================================================
        # WORKAROUND CONFIGURATION
        # ============================================================================
        # Enable these flags to activate workarounds for Tuya Cloud state update issues
        # Related issue: https://github.com/home-assistant/core/issues/156543
        
        # Enable polling fallback (periodically fetch state from cloud)
        self._enable_polling = False  # Set to True to enable
        self._polling_interval = 30  # seconds
        self._polling_task = None
        
        # Enable optimistic updates (immediate UI feedback)
        self._enable_optimistic = False  # Set to True to enable
        self._optimistic_position = None
        
        # Enable post-command refresh (force refresh after commands)
        self._enable_post_command_refresh = True  # Recommended: keep True
        self._post_command_delay = 3  # seconds
        
        # ============================================================================

        # Check if this cover is based on a switch or has controls
        if get_dpcode(self.device, description.key):
            if device.function[description.key].type == "Boolean":
                self._attr_supported_features |= (
                    CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE
                )
            elif enum_type := find_dpcode(
                self.device, description.key, dptype=DPType.ENUM, prefer_function=True
            ):
                if description.open_instruction_value in enum_type.range:
                    self._attr_supported_features |= CoverEntityFeature.OPEN
                if description.close_instruction_value in enum_type.range:
                    self._attr_supported_features |= CoverEntityFeature.CLOSE
                if description.stop_instruction_value in enum_type.range:
                    self._attr_supported_features |= CoverEntityFeature.STOP

        self._current_state = get_dpcode(self.device, description.current_state)

        if set_position:
            self._attr_supported_features |= CoverEntityFeature.SET_POSITION
        if tilt_position:
            self._attr_supported_features |= CoverEntityFeature.SET_TILT_POSITION
    
    async def async_added_to_hass(self) -> None:
        """Call when entity is added to hass."""
        await super().async_added_to_hass()
        
        # ============================================================================
        # WORKAROUND: POLLING FALLBACK
        # ============================================================================
        # Uncomment the code below to enable periodic polling for device state
        # This is useful when Tuya Cloud doesn't send MQTT push updates
        
        # if self._enable_polling:
        #     from .workarounds import polling_fallback
        #     self._polling_task = self.hass.async_create_task(
        #         polling_fallback(
        #             self.hass,
        #             self.device_manager,
        #             self.device.id,
        #             interval=self._polling_interval,
        #         )
        #     )
        #     self.async_on_remove(lambda: self._polling_task.cancel())
        
        # ============================================================================
    
    async def async_will_remove_from_hass(self) -> None:
        """Call when entity will be removed from hass."""
        # Cancel polling task if it exists
        if self._polling_task is not None:
            self._polling_task.cancel()

    @property
    def current_cover_position(self) -> int | None:
        """Return cover current position."""
        return self._read_wrapper(self._current_position)

    @property
    def current_cover_tilt_position(self) -> int | None:
        """Return current position of cover tilt.

        None is unknown, 0 is closed, 100 is fully open.
        """
        return self._read_wrapper(self._tilt_position)

    @property
    def is_closed(self) -> bool | None:
        """Return true if cover is closed."""
        # If it's available, prefer the position over the current state
        if (position := self.current_cover_position) is not None:
            return position == 0

        if (
            self._current_state is not None
            and (current_state := self.device.status.get(self._current_state))
            is not None
            and current_state != "stop"
        ):
            return self.entity_description.current_state_inverse is not (
                current_state in (True, "close", "fully_close")
            )

        return None

    def open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        # ============================================================================
        # WORKAROUND: OPTIMISTIC UPDATE
        # ============================================================================
        # Uncomment to enable immediate UI feedback before cloud confirms
        
        # if self._enable_optimistic:
        #     from .workarounds import optimistic_cover_update
        #     self._optimistic_position = optimistic_cover_update(
        #         self.current_cover_position,
        #         100,
        #         is_opening=True,
        #     )
        #     self.async_write_ha_state()
        
        # ============================================================================
        
        value: bool | str = True
        if find_dpcode(
            self.device,
            self.entity_description.key,
            dptype=DPType.ENUM,
            prefer_function=True,
        ):
            value = self.entity_description.open_instruction_value

        commands: list[dict[str, str | int]] = [
            {"code": self.entity_description.key, "value": value}
        ]

        if self._set_position is not None:
            commands.append(self._set_position.get_update_command(self.device, 100))

        self._send_command(commands)
        
        # ============================================================================
        # WORKAROUND: POST-COMMAND REFRESH
        # ============================================================================
        # Force a state refresh after sending command (recommended)
        
        if self._enable_post_command_refresh:
            from .workarounds import post_command_refresh
            self.hass.async_create_task(
                post_command_refresh(
                    self.hass,
                    self.device_manager,
                    self.device.id,
                    delay=self._post_command_delay,
                )
            )
        
        # ============================================================================

    def close_cover(self, **kwargs: Any) -> None:
        """Close cover."""
        # ============================================================================
        # WORKAROUND: OPTIMISTIC UPDATE
        # ============================================================================
        # Uncomment to enable immediate UI feedback before cloud confirms
        
        # if self._enable_optimistic:
        #     from .workarounds import optimistic_cover_update
        #     self._optimistic_position = optimistic_cover_update(
        #         self.current_cover_position,
        #         0,
        #         is_opening=False,
        #     )
        #     self.async_write_ha_state()
        
        # ============================================================================
        
        value: bool | str = False
        if find_dpcode(
            self.device,
            self.entity_description.key,
            dptype=DPType.ENUM,
            prefer_function=True,
        ):
            value = self.entity_description.close_instruction_value

        commands: list[dict[str, str | int]] = [
            {"code": self.entity_description.key, "value": value}
        ]

        if self._set_position is not None:
            commands.append(self._set_position.get_update_command(self.device, 0))

        self._send_command(commands)
        
        # ============================================================================
        # WORKAROUND: POST-COMMAND REFRESH
        # ============================================================================
        # Force a state refresh after sending command (recommended)
        
        if self._enable_post_command_refresh:
            from .workarounds import post_command_refresh
            self.hass.async_create_task(
                post_command_refresh(
                    self.hass,
                    self.device_manager,
                    self.device.id,
                    delay=self._post_command_delay,
                )
            )
        
        # ============================================================================

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        target_position = kwargs[ATTR_POSITION]
        
        # ============================================================================
        # WORKAROUND: OPTIMISTIC UPDATE
        # ============================================================================
        # Uncomment to enable immediate UI feedback before cloud confirms
        
        # if self._enable_optimistic:
        #     self._optimistic_position = target_position
        #     self.async_write_ha_state()
        
        # ============================================================================
        
        await self._async_send_dpcode_update(self._set_position, target_position)
        
        # ============================================================================
        # WORKAROUND: POST-COMMAND REFRESH
        # ============================================================================
        # Force a state refresh after sending command (recommended)
        
        if self._enable_post_command_refresh:
            from .workarounds import post_command_refresh
            self.hass.async_create_task(
                post_command_refresh(
                    self.hass,
                    self.device_manager,
                    self.device.id,
                    delay=self._post_command_delay,
                )
            )
        
        # ============================================================================

    def stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        self._send_command(
            [
                {
                    "code": self.entity_description.key,
                    "value": self.entity_description.stop_instruction_value,
                }
            ]
        )
        
        # ============================================================================
        # WORKAROUND: POST-COMMAND REFRESH
        # ============================================================================
        # Force a state refresh after sending command (recommended)
        
        if self._enable_post_command_refresh:
            from .workarounds import post_command_refresh
            self.hass.async_create_task(
                post_command_refresh(
                    self.hass,
                    self.device_manager,
                    self.device.id,
                    delay=self._post_command_delay,
                )
            )
        
        # ============================================================================

    async def async_set_cover_tilt_position(self, **kwargs: Any) -> None:
        """Move the cover tilt to a specific position."""
        await self._async_send_dpcode_update(
            self._tilt_position, kwargs[ATTR_TILT_POSITION]
        )
