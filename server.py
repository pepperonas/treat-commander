#!/usr/bin/env python3
"""
Treat Commander v1.0 - Snack Automat Controller für Tyson
Flask server mit Arduino Uno R3 Serial-Kommunikation
"""

import os
import time
import serial
import threading
from queue import Queue, Empty
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime

# Configuration
ARDUINO_PORT = os.environ.get('ARDUINO_PORT', '/dev/ttyACM0')
ARDUINO_BAUDRATE = 9600
SERVER_PORT = int(os.environ.get('PORT', 5007))

# Flask App
app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

class TreatDispenser:
    def __init__(self):
        self.serial_conn = None
        self.connected = False
        self.status = {
            "connected": False,
            "last_dispense": None,
            "total_treats": 0,
            "arduino_response": "",
            "plate_enabled": False
        }
        self.command_queue = Queue()
        self.running = True
        
        # Start background threads
        threading.Thread(target=self.connect_arduino, daemon=True).start()
        threading.Thread(target=self.command_worker, daemon=True).start()
        
    def connect_arduino(self):
        """Connect to Arduino and handle reconnection"""
        while self.running:
            try:
                if not self.connected:
                    print(f"🔌 Connecting to Arduino on {ARDUINO_PORT}...")
                    
                    # Try multiple possible ports
                    ports_to_try = [ARDUINO_PORT, '/dev/ttyUSB0', '/dev/ttyACM0']
                    
                    for port in ports_to_try:
                        try:
                            self.serial_conn = serial.Serial(port, ARDUINO_BAUDRATE, timeout=2)
                            time.sleep(3)  # Arduino boot time
                            
                            # Test connection by sending a test command
                            self.serial_conn.write(b'\n')
                            time.sleep(0.5)
                            
                            self.connected = True
                            self.status["connected"] = True
                            print(f"✅ Arduino connected on {port}")
                            break
                            
                        except (serial.SerialException, PermissionError) as e:
                            print(f"❌ Failed to connect to {port}: {e}")
                            continue
                    
                    if not self.connected:
                        print("❌ Could not connect to Arduino on any port")
                        time.sleep(5)  # Wait before retry
                        continue
                
                # Monitor connection
                if self.connected and self.serial_conn:
                    try:
                        # Read any incoming data
                        if self.serial_conn.in_waiting > 0:
                            response = self.serial_conn.readline().decode('utf-8').strip()
                            if response:
                                self.status["arduino_response"] = response
                                print(f"📥 Arduino: {response}")
                                
                                # Parse plate status from Arduino responses
                                if "STATUS:" in response:
                                    self.status["plate_enabled"] = "ENTSPERRT" in response
                                elif "ENTSPERRT" in response:
                                    self.status["plate_enabled"] = True
                                elif "GESPERRT" in response:
                                    self.status["plate_enabled"] = False
                    except Exception as e:
                        print(f"❌ Connection lost: {e}")
                        self.connected = False
                        self.status["connected"] = False
                        if self.serial_conn:
                            self.serial_conn.close()
                            
            except Exception as e:
                print(f"❌ Arduino connection error: {e}")
                self.connected = False
                self.status["connected"] = False
                
            time.sleep(1)
    
    def command_worker(self):
        """Process commands from queue"""
        while self.running:
            try:
                command = self.command_queue.get(timeout=1)
                if self.connected and self.serial_conn:
                    try:
                        print(f"📤 Sending command: {command}")
                        self.serial_conn.write(f"{command}\n".encode())
                        self.serial_conn.flush()  # Force send immediately
                        time.sleep(0.5)  # Wait for Arduino response
                        
                        # Try to read immediate response
                        if self.serial_conn.in_waiting > 0:
                            response = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                            if response:
                                self.status["arduino_response"] = response
                                print(f"📥 Arduino immediate response: {response}")
                    except Exception as e:
                        print(f"❌ Failed to send command: {e}")
                        self.connected = False
                        self.status["connected"] = False
                        
            except Empty:
                continue
            except Exception as e:
                print(f"❌ Command worker error: {e}")
    
    def dispense_treat(self):
        """Send treat dispense command to Arduino"""
        if not self.connected:
            return {"success": False, "message": "Arduino nicht verbunden"}
        
        try:
            self.command_queue.put('x')
            self.status["last_dispense"] = datetime.now().isoformat()
            self.status["total_treats"] += 1
            
            return {
                "success": True, 
                "message": "Snack wird ausgegeben! 🦴",
                "total_treats": self.status["total_treats"]
            }
            
        except Exception as e:
            print(f"❌ Dispense error: {e}")
            return {"success": False, "message": f"Fehler: {str(e)}"}
    
    def get_status(self):
        """Get current dispenser status"""
        return self.status.copy()
    
    def toggle_plate(self):
        """Toggle pressure plate enabled/disabled"""
        if not self.connected:
            return {"success": False, "message": "Arduino nicht verbunden"}
        
        try:
            # Toggle the state
            new_state = not self.status.get("plate_enabled", False)
            command = 'p' if new_state else 'l'
            
            self.command_queue.put(command)
            time.sleep(1)  # Wait longer for Arduino response
            
            # Update the status immediately
            self.status["plate_enabled"] = new_state
            
            return {
                "success": True,
                "message": f"Drückerplatte {'entsperrt' if new_state else 'gesperrt'}! {'🟢' if new_state else '🔴'}",
                "plate_enabled": new_state
            }
            
        except Exception as e:
            print(f"❌ Plate toggle error: {e}")
            return {"success": False, "message": f"Fehler: {str(e)}"}
    
    def get_plate_status(self):
        """Get current plate status"""
        if not self.connected:
            return {"success": False, "message": "Arduino nicht verbunden"}
        
        try:
            # Request status from Arduino
            self.command_queue.put('s')
            time.sleep(0.5)  # Wait for response
            
            return {
                "success": True,
                "plate_enabled": self.status.get("plate_enabled", False),
                "message": "Drückerplatte " + ("entsperrt 🟢" if self.status.get("plate_enabled", False) else "gesperrt 🔴")
            }
            
        except Exception as e:
            print(f"❌ Plate status error: {e}")
            return {"success": False, "message": f"Fehler: {str(e)}"}

# Global dispenser instance
dispenser = TreatDispenser()

@app.route('/')
def index():
    """Serve main HTML page"""
    return send_from_directory('public', 'index.html')

@app.route('/api/dispense', methods=['POST'])
def dispense_treat():
    """Dispense a treat"""
    result = dispenser.dispense_treat()
    return jsonify(result)

@app.route('/api/status')
def get_status():
    """Get dispenser status"""
    status = dispenser.get_status()
    return jsonify(status)

@app.route('/api/test', methods=['POST'])
def test_connection():
    """Test Arduino connection"""
    if dispenser.connected:
        # Send a test command and wait for response
        try:
            dispenser.command_queue.put('x')
            time.sleep(1)  # Wait for response
            return jsonify({
                "success": True, 
                "message": "Arduino verbunden - Test-Kommando gesendet",
                "last_response": dispenser.status.get("arduino_response", "Keine Antwort")
            })
        except Exception as e:
            return jsonify({"success": False, "message": f"Test fehlgeschlagen: {str(e)}"})
    else:
        return jsonify({"success": False, "message": "Arduino nicht verbunden"})

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Debug information"""
    return jsonify({
        "connected": dispenser.connected,
        "serial_port": ARDUINO_PORT,
        "baudrate": ARDUINO_BAUDRATE,
        "last_response": dispenser.status.get("arduino_response", ""),
        "total_treats": dispenser.status.get("total_treats", 0),
        "plate_enabled": dispenser.status.get("plate_enabled", False),
        "python_version": os.sys.version
    })

@app.route('/api/plate/toggle', methods=['POST'])
def toggle_pressure_plate():
    """Toggle pressure plate enabled/disabled"""
    result = dispenser.toggle_plate()
    return jsonify(result)

@app.route('/api/plate/status', methods=['GET'])
def get_plate_status():
    """Get pressure plate status"""
    result = dispenser.get_plate_status()
    return jsonify(result)

# Static file serving
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('public', filename)

if __name__ == '__main__':
    print(f"🐕 Treat Commander starting on port {SERVER_PORT}")
    print(f"🔧 Arduino port: {ARDUINO_PORT}")
    print(f"🌐 Web interface: http://localhost:{SERVER_PORT}")
    
    try:
        app.run(host='0.0.0.0', port=SERVER_PORT, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Treat Commander...")
        dispenser.running = False