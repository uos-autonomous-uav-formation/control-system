from adafruit_mcp3xxx.analog_in import AnalogIn
import adafruit_mcp3xxx.mcp3008 as MCP
from numbers import Number

# Implement a zeroing in startup (like with the airspeed sensor)

class PressureSensor:
    _min_voltage_check: float = 0.3 # When performing start up safety checks, 
    
    _zero: int = 0

    def __init__(self, mcp: MCP.MCP3008, channel: int, ref_voltage: Number):
        """ Interface for a MPXV7002DP pressure sensor via a MCP analogue to digital converter.
        
        """

        # Initialize connection
        self._input = AnalogIn(mcp, channel)
        self.channel = channel

        # Perform start up checks
        #self._start_up_safety_checks()

        # Peform zeroing (add time average for zeroing and save)
        self._zero = self.voltage
        print(self._zero)


    def _start_up_safety_checks(self):
        if self.voltage < self._min_voltage_check:
            raise ValueError(f"Voltage too low for {self.channel}. Check if sensor working and wiring connected.")
    
    @property
    def raw_pressure(self) -> float:
        """Raw pressure difference from the sensor"""
        return (self.voltage / (5 * 0.2)) - 0.5

    @property
    def voltage(self) -> float:
        """Volage without calibration"""
        return self._input.voltage

    @property
    def dvoltage(self) -> float:
        """Volage difference from the calibrated zero value"""
        return self.voltage - self._zero

    @property
    def theoretical_error(self):
        pass
    