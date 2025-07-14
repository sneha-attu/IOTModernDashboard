from flask import Flask, request, render_template, jsonify
import serial
import time
import threading
import json

# Then inside your try block:

   

app = Flask(__name__)

# --- Try to connect to Arduino ---
try:
    arduino = serial.Serial('COM10', 9600, timeout=1)  # Change to your actual COM port
    time.sleep(2)
    print("[INFO] Connected to Arduino on COM10")
    
except Exception as e:
    arduino = None
    print(f"[ERROR] Could not connect to Arduino: {e}")

# --- Global state tracking ---
buzzer_enabled = False
temperature_alert_active = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-sensor-data')
def get_sensor_data():
    global buzzer_enabled, temperature_alert_active

    if arduino:
        try:
            arduino.write(b"READ\n")
            line = arduino.readline().decode().strip()
            print(f"[DEBUG] Arduino response: {line}")

            if not line or not line.startswith('{'):
                raise ValueError("Invalid data format")

            data = eval(line)  # Example: {"temp":25,"hum":60,...}

            # Temperature alert logic
            temp = data.get("temp", 0)
            if temp < 25 and not temperature_alert_active:
                temperature_alert_active = True
                if buzzer_enabled:
                    arduino.write(b"BUZZER_TEMP_ALERT\n")
            elif temp >= 26 and temperature_alert_active:
                temperature_alert_active = False
                arduino.write(b"BUZZER_OFF\n")

            # Add alert state to JSON
            data["temp_alert"] = temperature_alert_active
            data["buzzer_enabled"] = buzzer_enabled

            return jsonify(data)

        except Exception as e:
            print(f"[ERROR] Sensor read failed: {e}")
            return jsonify({'error': f'Sensor read error: {str(e)}'})
    else:
        return jsonify({'error': 'Arduino not connected'}), 500

@app.route('/send-command', methods=['POST'])
def send_command():
    global buzzer_enabled

    if not arduino:
        return jsonify({'status': 'error', 'message': 'Arduino not connected'}), 500

    data = request.get_json()
    command = data.get("command", "")

    try:
        # Handle buzzer logic separately
        if command == "BUZZER_ENABLE":
            buzzer_enabled = True
            arduino.write(b"BUZZER_ENABLE\n")
            return jsonify({'status': 'success', 'message': 'Buzzer enabled'})

        elif command == "BUZZER_DISABLE":
            buzzer_enabled = False
            arduino.write(b"BUZZER_DISABLE\n")
            return jsonify({'status': 'success', 'message': 'Buzzer disabled'})

        elif command == "BUZZER_ON":
            if buzzer_enabled:
                arduino.write(b"BUZZER_ON\n")
                return jsonify({'status': 'success', 'message': 'Buzzer activated'})
            else:
                return jsonify({'status': 'error', 'message': 'Buzzer is disabled'})

        elif command == "BUZZER_OFF":
            arduino.write(b"BUZZER_OFF\n")
            return jsonify({'status': 'success', 'message': 'Buzzer turned off'})

        elif command == "BUZZER_TEST":
            arduino.write(b"BUZZER_TEST\n")
            return jsonify({'status': 'success', 'message': 'Buzzer tested'})

        # Send all other commands directly
        arduino.write((command + '\n').encode())
        return jsonify({'status': 'success', 'message': f'Command sent: {command}'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to send command: {str(e)}'})

@app.route('/get-buzzer-status')
def get_buzzer_status():
    return jsonify({
        'enabled': buzzer_enabled,
        'temp_alert_active': temperature_alert_active
    })

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
