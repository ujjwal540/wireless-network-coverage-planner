"""
transmitter.py
==============
Represents a single Wi-Fi Access Point / Base Station placed on the site.
"""


class Transmitter:
    def __init__(self, name, x, y, power_dbm, antenna_gain_dbi=0.0, frequency_mhz=2400.0):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.power_dbm = float(power_dbm)
        self.antenna_gain_dbi = float(antenna_gain_dbi)
        self.frequency_mhz = float(frequency_mhz)

    def eirp_dbm(self):
        """Effective Isotropic Radiated Power = Tx power + antenna gain."""
        return self.power_dbm + self.antenna_gain_dbi

    def __repr__(self):
        return (f"<Transmitter {self.name} @ ({self.x:.1f},{self.y:.1f}) "
                f"{self.power_dbm}dBm +{self.antenna_gain_dbi}dBi @ {self.frequency_mhz:.0f}MHz>")

    @staticmethod
    def from_config(entries):
        """Build a list of Transmitter objects from config.TRANSMITTERS."""
        return [Transmitter(**e) for e in entries]
