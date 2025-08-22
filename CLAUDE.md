# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Treat Commander - Smart Pet Treat Dispenser

## Project Overview
Treat Commander is a Flask-based smart treat dispenser for Tyson (a dog) that communicates with an Arduino Uno R3 via USB serial. The system features a web interface for remote treat dispensing and a pressure plate system allowing Tyson to self-serve treats.

## Architecture

### Hardware Components
- **Stepper Motor**: 4-wire stepper motor connected to Arduino pins 8, 9, 10, 11 (NOT a servo motor)
- **Arduino Uno R3**: Controls stepper motor with 2048 steps = 180° rotation for treat dispensing
- **Pressure Plate**: Connected to pin 3 with INPUT_PULLUP for Tyson's self-service
- **Status LED**: Pin 13 indicates plate status (ON when plate active/unlocked, stays ON when pressed)
- **Test Button**: Pin 2 for manual testing (optional)

### Software Stack
- **Backend**: Flask web server with threaded Arduino communication
- **Frontend**: Vanilla JavaScript PWA with glassmorphism design
- **Communication**: USB Serial at 9600 baud with auto-reconnect
- **Process Management**: PM2 for production deployment
- **Arduino Firmware**: Custom stepper motor control with pressure plate integration

### Key Design Patterns
- **Command Queue**: Thread-safe command queuing for Arduino communication
- **Background Threads**: Separate threads for Arduino connection monitoring and command processing
- **Auto-reconnection**: Automatic detection and reconnection to Arduino on multiple ports
- **Status Synchronization**: Real-time status updates between Arduino and web interface

## Development Commands

### Python Environment
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python3 server.py
```

### Arduino Development
```bash
# Clean and compile Arduino sketch
make clean && make

# Upload to Arduino (requires sudo for avrdude config)
sudo avrdude -V -p atmega328p -C /etc/avrdude.conf -D -c arduino -b 115200 -P /dev/ttyACM0 -U flash:w:build-uno/treat-commander_.hex:i

# Alternative: compile and upload in one command
make && sudo avrdude -V -p atmega328p -C /etc/avrdude.conf -D -c arduino -b 115200 -P /dev/ttyACM0 -U flash:w:build-uno/treat-commander_.hex:i
```

### Production Deployment
```bash
# Start PM2 service
pm2 start ecosystem.config.js

# Check status
pm2 status treat-commander

# View logs
pm2 logs treat-commander

# Restart service
pm2 restart treat-commander
```

### Testing and Debugging
```bash
# Test Arduino connection
curl -X POST http://localhost:5007/api/test

# Check dispenser status
curl http://localhost:5007/api/status

# Dispense treat
curl -X POST http://localhost:5007/api/dispense

# Toggle pressure plate
curl -X POST http://localhost:5007/api/plate/toggle
```

## Configuration

### Environment Variables
- `PORT`: Flask server port (default: 5007)
- `ARDUINO_PORT`: Serial port (default: /dev/ttyACM0, auto-detects /dev/ttyUSB0, /dev/ttyACM1)
- `FLASK_ENV`: Flask environment (production for PM2)

### Arduino Communication Protocol
- `x`: Dispense treat (180° stepper rotation)
- `p`: Unlock pressure plate (enable self-service)
- `l`: Lock pressure plate (disable self-service)  
- `s`: Query plate status

### Serial Port Management
The system automatically tries multiple ports in order:
1. `/dev/ttyACM0` (primary)
2. `/dev/ttyUSB0` (fallback)
3. `/dev/ttyACM1` (alternate)

## Critical Implementation Details

### Stepper Motor Control
- **IMPORTANT**: This uses a 4-wire stepper motor, NOT a servo motor
- **Pin Configuration**: Pins 8, 9, 10, 11 with specific step sequence (single coil activation)
- **Step Count**: 2048 steps = 180° rotation for treat dispensing
- **Motor Shutdown**: Motor pins are set LOW after movement to prevent overheating
- **Step Delay**: 3ms between steps for smooth operation

### Thread Safety
- Arduino communication uses command queue with background worker thread
- Connection monitoring runs in separate daemon thread
- Status updates are thread-safe with proper locking mechanisms

### Error Handling
- Automatic reconnection on serial connection loss
- Multiple port detection and fallback
- Command queue timeout handling
- Graceful degradation when Arduino disconnected

## Web Interface Features
- **PWA Support**: Installable as mobile app with service worker
- **Real-time Status**: Live Arduino connection and plate status updates
- **Bone Rain Animation**: 4-second celebration animation after treat dispensing
- **Responsive Design**: Optimized for both desktop and mobile devices
- **Offline Capability**: Service worker enables offline functionality

## Troubleshooting

### Common Issues
1. **Arduino not detected**: Check USB connection and try different ports
2. **Permission denied**: Add user to dialout group: `sudo usermod -a -G dialout pi`
3. **Port conflicts**: Check if port 5007 is available: `netstat -tlnp | grep 5007`
4. **Stepper motor not moving**: Verify pin connections 8, 9, 10, 11 and power supply

### Debug Endpoints
- `/api/debug`: Complete system status and configuration
- `/api/status`: Real-time dispenser status
- PM2 logs: `pm2 logs treat-commander` for detailed operation logs

## Hardware Wiring
```
Arduino Uno R3 Connections:
├── Stepper Motor: Pins 8, 9, 10, 11 (4-wire stepper, specific sequence required)
├── Pressure Plate: Pin 3 (INPUT_PULLUP - connect plate between Pin 3 and GND)
├── Status LED: Pin 13 (built-in LED or external with 220Ω resistor)
├── Test Button: Pin 2 (optional, INPUT mode)
└── USB: Connected to Raspberry Pi for serial communication at 9600 baud
```

## API Endpoints
- `GET /`: Web interface
- `GET /api/status`: Current system status
- `POST /api/dispense`: Trigger treat dispensing
- `POST /api/test`: Test Arduino connection
- `POST /api/plate/toggle`: Enable/disable pressure plate
- `GET /api/plate/status`: Pressure plate status
- `GET /api/debug`: Debug information

## File Structure
```
├── server.py                 # Flask application with threaded Arduino communication
├── tyson_pressure_plate.ino  # Arduino firmware for stepper motor and pressure plate
├── Makefile                  # Arduino build configuration
├── ecosystem.config.js       # PM2 process management configuration
├── requirements.txt          # Python dependencies
├── public/
│   ├── index.html           # PWA web interface
│   ├── manifest.json        # PWA manifest
│   └── service-worker.js    # Offline functionality
└── venv/                    # Python virtual environment
```

## Pressure Plate Behavior
- **Default State**: Plate is locked (disabled) on startup
- **Unlock Command**: Send 'p' via serial or use web interface toggle
- **Lock Command**: Send 'l' via serial or use web interface toggle
- **LED Behavior**: Pin 13 LED is ON when plate is unlocked, OFF when locked
- **Debouncing**: 100ms debounce delay to prevent false triggers
- **Pull-up Configuration**: Pin 3 uses INPUT_PULLUP, so LOW = pressed, HIGH = not pressed

## Last Updated
2025-08-22 - Updated with pressure plate LED behavior and pin configurations