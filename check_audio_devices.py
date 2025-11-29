import sounddevice as sd

with open("devices.txt", "w", encoding="utf-8") as f:
    f.write(f"{'ID':<3} {'Name'}\n")
    f.write("-" * 30 + "\n")
    
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            f.write(f"{i:<3} {dev['name']}\n")
            
print("Saved to devices.txt")
