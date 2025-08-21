# 🦴 Treat Commander - Snack Automat für Tyson

Ein intelligenter Snack-Automat Controller für Tyson über Arduino Nano 33 IoT via Raspberry Pi.

![Treat Commander Mockup](https://github.com/pepperonas/treat-commander/blob/main/public/mockup-treat-commander.png)

## 📱 Features

- **Einfache Bedienung**: Ein-Klick Snack-Ausgabe über Web-Interface
- **🦴 Knochen-Regen Animation**: 4 Sekunden spektakuläre Bone-Rain Animation bei jedem Snack
- **Responsive Design**: Optimiert für Desktop und Mobile
- **Arduino Integration**: Direkte USB Serial-Kommunikation mit Arduino Nano 33 IoT
- **Status Monitoring**: Echtzeit-Überwachung der Arduino-Verbindung
- **PWA Support**: Installierbar als App auf Smartphones
- **Auto-Start**: Automatischer Start beim Raspberry Pi Bootvorgang

## 🔧 Hardware Setup

### Arduino Nano 33 IoT Code
Der Arduino muss mit folgendem Code programmiert sein:

```cpp
const int motorPins[] = {8, 9, 10, 11};

const int steps[4][4] = {
  {1, 0, 0, 0},
  {0, 1, 0, 0},
  {0, 0, 1, 0},
  {0, 0, 0, 1}
};

int currentStep = 0;

void setup() {
  // Motor Pins
  for(int i = 0; i < 4; i++) {
    pinMode(motorPins[i], OUTPUT);
  }
  
  // Serial starten
  Serial.begin(9600);
  Serial.println("Bereit - 'x' für halbe Umdrehung");
}

void stepMotor() {
  for(int i = 0; i < 4; i++) {
    digitalWrite(motorPins[i], steps[currentStep][i]);
  }
  currentStep = (currentStep + 1) % 4;
  delay(3);
}

void motorOff() {
  for(int i = 0; i < 4; i++) {
    digitalWrite(motorPins[i], LOW);
  }
}

void halfRotation() {
  Serial.println("Drehe 180°...");
  for(int i = 0; i < 2048; i++) {
    stepMotor();
  }
  motorOff();
  Serial.println("Fertig!");
}

void loop() {
  if(Serial.available()) {
    char input = Serial.read();
    
    if(input == 'x' || input == 'X') {
      halfRotation();
    }
  }
}
```

### Verkabelung
- **Motor Pins 8-11**: Stepper Motor Anschlüsse
- **USB**: Arduino Uno R3 an Raspberry Pi USB-Port

## 🚀 Installation & Start

### Manuelle Installation
```bash
cd /home/pi/apps/treat-commander

# Virtual Environment aktivieren
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# Server starten (Entwicklung)
python3 server.py
```

### Produktions-Deployment mit PM2
```bash
# PM2 Service starten
pm2 start ecosystem.config.js

# Logs anzeigen
pm2 logs treat-commander

# Status prüfen
pm2 status

# Auto-Start aktivieren (einmalig)
pm2 startup
pm2 save
```

## 🌐 Zugriff

- **Web Interface**: http://localhost:5007
- **Netzwerk**: http://192.168.2.134:5007 (oder aktuelle Pi IP)

## 📊 API Endpoints

### GET /api/status
Liefert aktuellen Status des Dispensers:
```json
{
  "connected": true,
  "last_dispense": "2025-08-20T15:30:00",
  "total_treats": 42,
  "arduino_response": "Fertig!"
}
```

### POST /api/dispense
Gibt einen Snack aus:
```json
{
  "success": true,
  "message": "Snack wird ausgegeben! 🦴",
  "total_treats": 43
}
```

### POST /api/test
Testet Arduino-Verbindung:
```json
{
  "success": true,
  "message": "Arduino verbunden und bereit"
}
```

## 🔧 Konfiguration

### Umgebungsvariablen
```bash
PORT=5007                    # Server Port
ARDUINO_PORT=/dev/ttyACM0    # Arduino Serial Port
FLASK_ENV=production         # Flask Environment
```

### Serial Port Detection
Die App sucht automatisch nach Arduino auf folgenden Ports:
- `/dev/ttyACM0` (Standard)
- `/dev/ttyUSB0` 
- `/dev/ttyACM1`

## 🐕 Verwendung

1. **Snack ausgeben**: Großen orangenen Button drücken
2. **🦴 Knochen-Regen genießen**: Nach erfolgreicher Ausgabe startet automatisch eine 4-sekündige Animation mit fallenden Knochen, Steaks und Fleisch in verschiedenen Größen und Animationsstilen
3. **Status prüfen**: Arduino-Verbindung wird automatisch überwacht
4. **Statistiken**: Anzahl ausgegebener Snacks und letzte Ausgabe
5. **Mobile**: App auf Smartphone installieren für schnellen Zugriff

## 🛠️ Troubleshooting

### Arduino nicht verbunden
```bash
# Verfügbare Ports prüfen
ls -la /dev/tty*

# Berechtigungen prüfen
sudo usermod -a -G dialout pi

# PM2 Logs prüfen
pm2 logs treat-commander
```

### Port bereits belegt
```bash
# Port-Nutzung prüfen
netstat -tlnp | grep 5007

# Anderen Port verwenden
PORT=5008 pm2 restart treat-commander
```

## 📁 Projektstruktur

```
treat-commander/
├── server.py              # Flask Server
├── requirements.txt       # Python Dependencies
├── ecosystem.config.js    # PM2 Konfiguration
├── public/
│   ├── index.html         # Web Interface
│   ├── manifest.json      # PWA Manifest
│   ├── service-worker.js  # Service Worker
│   └── *.png              # App Icons
├── venv/                  # Virtual Environment
└── logs/                  # PM2 Logs
```

## 🎯 Technische Details

- **Backend**: Flask (Python 3.11+)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Design**: Glassmorphism Dark Theme
- **Communication**: USB Serial (9600 Baud)
- **Process Manager**: PM2
- **PWA**: Offline-fähig mit Service Worker

## 📄 Lizenz

Dieses Projekt steht unter der MIT Lizenz. Siehe [LICENSE](LICENSE) für weitere Details.

## 👨‍💻 Autor

**Martin Pfeffer** - [pepperonas](https://github.com/pepperonas)

## 🙏 Danksagungen

**Erstellt für Tyson 🐕 - Der beste Hund der Welt!**

---

*© 2025 Martin Pfeffer - Treat Commander*