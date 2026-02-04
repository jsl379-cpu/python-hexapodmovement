#!/usr/bin/env python3
"""
Change the ID of a Waveshare ST3215 servo.

IMPORTANT: Connect only ONE servo at a time when changing IDs!
If multiple servos have the same ID, they cannot be distinguished.

The new ID is permanently saved in the servo's EEPROM.
"""

import os
import sys
from dotenv import load_dotenv

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


def find_single_servo(servo_bus):
    """
    Find the single servo connected to the bus.
    Returns the servo ID if exactly one is found, None otherwise.
    """
    print("Scanning for servos...")
    servo_ids = servo_bus.ListServos()

    if not servo_ids:
        print("\n❌ No servos found!")
        print("   Make sure the servo is powered and connected.")
        return None

    if len(servo_ids) > 1:
        print(f"\n⚠️  Found {len(servo_ids)} servos: {servo_ids}")
        print("   Please connect only ONE servo at a time to change its ID.")
        print("   Disconnect all but one servo and try again.")
        return None

    return servo_ids[0]


def change_servo_id(current_id: int, new_id: int):
    """Change a servo's ID from current_id to new_id."""
    from st3215 import ST3215

    port = get_serial_port()
    print(f"Connecting to: {port}")
    print("-" * 50)

    try:
        servo_bus = ST3215(port)
    except Exception as e:
        print(f"Error: Could not open serial port '{port}'")
        print(f"Details: {e}")
        return False

    # Verify the servo exists
    if not servo_bus.PingServo(current_id):
        print(f"\n❌ No servo found with ID {current_id}")
        print("   Scanning to see what's connected...")
        servo_ids = servo_bus.ListServos()
        if servo_ids:
            print(f"   Found servos with IDs: {servo_ids}")
        else:
            print("   No servos found on the bus.")
        return False

    # Check if new ID is already in use
    if current_id != new_id and servo_bus.PingServo(new_id):
        print(f"\n❌ ID {new_id} is already in use by another servo!")
        print("   Please choose a different ID.")
        return False

    # Change the ID
    print(f"\nChanging servo ID: {current_id} → {new_id}")
    result = servo_bus.ChangeId(current_id, new_id)

    if result is None:
        print("✅ ID changed successfully!")
        print(f"\n   The servo now has ID {new_id}")
        print("   This change is permanent (saved in EEPROM).")

        # Verify the change
        if servo_bus.PingServo(new_id):
            print(f"   ✅ Verified: Servo responds at ID {new_id}")
        return True
    else:
        print(f"❌ Failed to change ID: {result}")
        return False


def interactive_mode():
    """Interactive mode to guide the user through changing servo IDs."""
    from st3215 import ST3215

    port = get_serial_port()
    print("=" * 50)
    print("  ST3215 Servo ID Changer - Interactive Mode")
    print("=" * 50)
    print(f"\nSerial port: {port}")
    print("\n⚠️  IMPORTANT: Connect only ONE servo at a time!")
    print("-" * 50)

    try:
        servo_bus = ST3215(port)
    except Exception as e:
        print(f"Error: Could not open serial port '{port}'")
        print(f"Details: {e}")
        return

    # Find the connected servo
    current_id = find_single_servo(servo_bus)
    if current_id is None:
        return

    print(f"\n✅ Found servo with ID: {current_id}")

    # Show current servo info
    position = servo_bus.ReadPosition(current_id)
    voltage = servo_bus.ReadVoltage(current_id)
    if position is not None:
        print(f"   Position: {position} steps")
    if voltage is not None:
        print(f"   Voltage:  {voltage:.1f} V")

    # Ask for new ID
    print(f"\nCurrent ID: {current_id}")
    print("Valid IDs: 1-253 (254 is broadcast)")

    while True:
        try:
            new_id_input = input("\nEnter new ID (or 'q' to quit): ").strip()

            if new_id_input.lower() == 'q':
                print("Cancelled.")
                return

            new_id = int(new_id_input)

            if not 1 <= new_id <= 253:
                print("❌ ID must be between 1 and 253")
                continue

            if new_id == current_id:
                print(f"ℹ️  Servo already has ID {current_id}")
                return

            break
        except ValueError:
            print("❌ Please enter a valid number")

    # Confirm the change
    print(f"\nAbout to change ID: {current_id} → {new_id}")
    confirm = input("Proceed? (y/n): ").strip().lower()

    if confirm != 'y':
        print("Cancelled.")
        return

    # Perform the change
    result = servo_bus.ChangeId(current_id, new_id)

    if result is None:
        print("\n✅ ID changed successfully!")
        print(f"   Servo now has ID: {new_id}")

        # Verify
        if servo_bus.PingServo(new_id):
            print("   ✅ Verified: Servo responds at new ID")
    else:
        print(f"\n❌ Failed to change ID: {result}")


def print_usage():
    """Print usage information."""
    print("""
Usage: python change_servo_id.py [current_id] [new_id]

Examples:
  python change_servo_id.py           # Interactive mode
  python change_servo_id.py 1 5       # Change ID 1 to ID 5

IMPORTANT:
  - Connect only ONE servo at a time when changing IDs
  - Valid IDs are 1-253 (254 is broadcast address)
  - The ID change is permanent (saved in servo EEPROM)

Workflow for multiple servos with same ID:
  1. Disconnect all servos
  2. Connect just one servo
  3. Run this script to change its ID
  4. Disconnect it, connect the next one
  5. Repeat until all servos have unique IDs
""")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Interactive mode
        interactive_mode()
    elif len(sys.argv) == 3:
        # Command line mode
        try:
            current_id = int(sys.argv[1])
            new_id = int(sys.argv[2])

            if not 1 <= current_id <= 253:
                print("Error: Current ID must be between 1 and 253")
                sys.exit(1)
            if not 1 <= new_id <= 253:
                print("Error: New ID must be between 1 and 253")
                sys.exit(1)

            success = change_servo_id(current_id, new_id)
            sys.exit(0 if success else 1)
        except ValueError:
            print("Error: IDs must be integers")
            print_usage()
            sys.exit(1)
    else:
        print_usage()
        sys.exit(1)