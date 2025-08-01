from typing import override
import tinytuya
import json
from dataclasses import dataclass

#consts 
kesser_heater_product_id: str = "sa7ty0oxseyuzzlp"

@dataclass
class KesserHeaterStatus:
    current_temp: int
    set_temp: int
    power: bool
    online: bool
    display: bool

# Connect to the heater
class KesserHeater:
    def __init__(self, device_id: str, device_ip: str, local_key: str, name: str, version: str) -> None:
        self.heater = tinytuya.OutletDevice(device_id, device_ip, local_key)
        self.heater.set_version(version)
        self.name: str = name
        self.version: str = version

    def get_status_str(self):
        """Fetch and display heater status."""
        data = self.heater.status()
        if "dps" in data:
            dps = data["dps"]
            output = ""
            output += "Heater Status:\n"
            output += f" Power: {'ON' if dps.get('1') else 'OFF'}\n"
            output += f" Current Temp: {dps.get('3', 'Unknown')}°C\n"
            output += f" Target Temp: {dps.get('2', 'Unknown')}°C\n"
            output += f" Display: {'OFF' if dps.get('10') else 'ON'}"
            return output
        else:
            return "Failed to retrieve status."
        
    def get_status(self)->KesserHeaterStatus:
        data = self.heater.status()
        if "dps" in data:
            dps = data["dps"]
            return KesserHeaterStatus(int(dps.get('3', '-99')), int(dps.get('2', '-99')), bool(dps.get('1')), True, not bool(dps.get('10')))
        else:
            return KesserHeaterStatus(0, 0, False, False, False)


    def turn_on(self):
        """Turn the heater on."""
        self.heater.set_value("1", True)

    def turn_off(self):
        """Turn the heater off."""
        self.heater.set_value("1", False)

    def set_temperature(self, temp):
        """Set the target temperature, ignore if outside range"""
        if 5 <= temp <= 40:  
            self.heater.set_value("2", temp)
    
    def turn_display_on(self):
        self.heater.set_value("10", False)
    
    def turn_display_off(self):
        self.heater.set_value("10", True)

    @override
    def __str__(self) -> str:
        return "Device " + self.name + "\n" +self.get_status_str()

    @override
    def __repr__(self) -> str:
        return self.__str__()

def parse_devices() -> list[KesserHeater]:
    devices = []
    with open('devices.json', 'r') as fin:
        data = json.load(fin)
        for device_json in data:
            if(device_json['product_id'] == kesser_heater_product_id):
                device = KesserHeater(device_json['id'], device_json['ip'], device_json['key'], device_json['name'], device_json['version'])
                devices.append(device)
    return devices

if __name__ == "__main__":
    devices = parse_devices()
    print("\n\n".join(map(str, devices)))
