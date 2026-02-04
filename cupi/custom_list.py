#!/usr/bin/env python3
"""
List all connected Waveshare ST3215 servos.

This script scans the serial bus and displays information about each
connected servo including its position, voltage, and temperature.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_serial_port():
    """Get the serial port from environment variable."""
    port = os.getenv("ST3215_DEV")
    if not port:
        raise EnvironmentError(
            "ST3215_DEV environment variable not set.\n"
            "Please create a .env file with: ST3215_DEV=/dev/tty.usbmodem5A680113571"
        )
    return port


def list_servos():
    """Scan for and display all connected ST3215 servos."""
    from st3215 import ST3215

    port = get_serial_port()
    print(f"Connecting to serial port: {port}")
    print("-" * 50)

    try:
        servo_bus = ST3215(port)
    except Exception as e:
        print(f"Error: Could not open serial port '{port}'")
        print(f"Details: {e}")
        return

    # Scan for all connected servos
    print("Scanning for servos...")
    servo_ids = servo_bus.ListServos()

    if not servo_ids:
        print("No servos found on the bus.")
        return

    print(f"\nFound {len(servo_ids)} servo(s):\n")

    # Display info for each servo
    for servo_id in servo_ids:
        print(f"Servo ID: {servo_id}")

        # Read position
        position = servo_bus.ReadPosition(servo_id)
        if position is not None:
            degrees = (position / 4096) * 360
            print(f"  Position:    {position} steps ({degrees:.1f}°)")

        # Read voltage
        voltage = servo_bus.ReadVoltage(servo_id)
        if voltage is not None:
            print(f"  Voltage:     {voltage:.1f} V")

        # Read temperature
        temperature = servo_bus.ReadTemperature(servo_id)
        if temperature is not None:
            print(f"  Temperature: {temperature} °C")

        # Read mode
        mode = servo_bus.ReadMode(servo_id)
        mode_names = {
            0: "Position Servo",
            1: "Constant Speed Motor",
            2: "PWM Open-Loop",
            3: "Step Servo",
        }
        if mode is not None:
            mode_name = mode_names.get(mode, f"Unknown ({mode})")
            print(f"  Mode:        {mode_name}")

        # Read load
        load = servo_bus.ReadLoad(servo_id)
        if load is not None:
            print(f"  Load:        {load:.1f}%")

        print()

    print("-" * 50)
    print(f"Scan complete. Total servos found: {len(servo_ids)}")


if __name__ == "__main__":
    list_servos()