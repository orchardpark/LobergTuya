from typing import override
import tinytuya
import json

#consts 
kesser_heater_product_id: str = "sa7ty0oxseyuzzlp"

# Connect to the heater
class KesserHeater:
    def __init__(self, device_id: str, device_ip: str, local_key: str, name: str, version: str) -> None:
        self.heater = tinytuya.OutletDevice(device_id, device_ip, local_key)
        self.heater.set_version(version)
        self.name: str = name
        self.version: str = version

    def get_status(self):
        """Fetch and display heater status."""
        data = self.heater.status()
        if "dps" in data:
            dps = data["dps"]
            output = ""
            output += "Heater Status:\n"
            output += f" Power: {'ON' if dps.get('1') else 'OFF'}\n"
            output += f" Current Temp: {dps.get('3', 'Unknown')}°C\n"
            output += f" Target Temp: {dps.get('2', 'Unknown')}°C\n"
            return output
        else:
            return "Failed to retrieve status."

    def turn_on(self):
        """Turn the heater on."""
        self.heater.set_value("1", True)
        print("Heater turned ON.")

    def turn_off(self):
        """Turn the heater off."""
        self.heater.set_value("1", False)
        print("Heater turned OFF.")

    def set_temperature(self, temp):
        """Set the target temperature (adjust range as needed)."""
        if 10 <= temp <= 30:  # Example valid range
            self.heater.set_value("2", temp)
            print(f"Target temperature set to {temp}°C.")
        else:
            print("Temperature out of range!")

    @override
    def __str__(self) -> str:
        return self.get_status()

    @override
    def __repr__(self) -> str:
        return self.get_status()

def parse_devices():
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
    print(devices)
