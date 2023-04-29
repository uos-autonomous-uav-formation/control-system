import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from .pressure_sensor import PressureSensor
import numpy as np
from dataclasses import dataclass


@dataclass(init=True)
class AoAConfig:
    val1: float
    val2: float
    val3: float
    val4: float


AoA1_conf = AoAConfig(val1=0.3630852, val2=-0.131146, val3=-0.04228435 , val4= -0.13692735)
AoA2_conf = AoAConfig(val1=0.1877579, val2=-0.13755193, val3=0.24853187, val4=-0.16666902)


class AoaSensor:
    id: int

    def __init__(self, id, spi, chip_select, ref_voltage, aoa_conf: AoAConfig,
                 orientation: dict[int, int] = None):
        """
        Angle of attack sensor implementation using MCP3008.

        Args:
            spi: The SPI bus connecting to the MCP3008 chip.
            chip_select: The chipselect pin. For example board.D7
            ref_voltage: The refernce voltage the chip is connected to
            orientaion: The pin alloction of each probe hole. Key is the probe hole based on image, value is the pin (min 0, max 7)  Defaults to: {1: 0, 2: 1, 3: 2, 4: 3, 5: 4}
        
        """

        if orientation is None:
            orientation = {
                1: 0,
                2: 1,
                3: 2,
                4: 3,
                5: 4
            }
        else:
            if max(orientation.values()) > 8:
                raise ValueError("Pin value too high for an MCP3008 chip, maximum value 7")
            if min(orientation.values()) < 0:
                raise ValueError("Pin value too low for an MCP3008 chip, minimum value 0")

        self._chip_select = digitalio.DigitalInOut(chip_select)
        self._aoa_conf = aoa_conf
        self._mcp = MCP.MCP3008(spi, self._chip_select, ref_voltage=ref_voltage)
        self.ref_voltage = ref_voltage
        self._allocate_pressure_sensor(orientation)
        self.id = id

    def _allocate_pressure_sensor(self, orientation):
        self._pressure_sensors: dict[int, PressureSensor] = {}

        for key, item in orientation.items():
            self._pressure_sensors[key] = PressureSensor(self._mcp, item, ref_voltage=self.ref_voltage)

    def pressure_sensor_voltage(self, pressure_sensor: int) -> float:
        return self._pressure_sensors[pressure_sensor].voltage

    def pressure_sensor_dvoltage(self, pressure_sensor: int) -> float:
        return self._pressure_sensors[pressure_sensor].dvoltage

    def pressure_sensor_zero(self, pressure_sensor: int) -> float:
        return self._pressure_sensors[pressure_sensor]._zero

    def aoa_corr_voltage(self, pressure_sensor: int, speed: float) -> float:
        corr_factor = (0.0114528 * speed) + 1.06449159 #Speed obtained externally
        return corr_factor * self.pressure_sensor_voltage(pressure_sensor)  # return corrected value

    def aoa_corr_pressure(self, pressure_sensor: int, speed: float) -> float:
        Vdd = 3.3
        return 525 * (np.sign((self.aoa_corr_voltage(pressure_sensor, speed) / Vdd) - 0.5)) * (((self.aoa_corr_voltage(pressure_sensor, speed) / (Vdd * 0.4)) - 1.25) ** 2)

    def alpha_aoa(self, speed: float) -> float:
        p_avg = (self.aoa_corr_pressure(1, speed) + self.aoa_corr_pressure(2, speed) + self.aoa_corr_pressure(3, speed) + self.aoa_corr_pressure(4, speed)) / 4
        cp_alpha = (self.aoa_corr_pressure(1, speed) - self.aoa_corr_pressure(3, speed)) / (self.aoa_corr_pressure(5, speed) - p_avg)
        return (cp_alpha + self._aoa_conf.val1) / self._aoa_conf.val2  # return aoa

    def beta_aoa(self, speed: float) -> float:
        p_avg = (self.aoa_corr_pressure(1, speed) + self.aoa_corr_pressure(2, speed) + self.aoa_corr_pressure(3, speed) + self.aoa_corr_pressure(4, speed)) / 4
        cp_beta = (self.aoa_corr_pressure(2, speed) - self.aoa_corr_pressure(4, speed)) / (self.aoa_corr_pressure(5, speed) - p_avg)
        return (cp_beta + self._aoa_conf.val3) / self._aoa_conf.val4  # return aos
