// Pin Definitionen
const int BUTTON_PIN = 2;           // Bestehender Test-Button
const int PRESSURE_PLATE_PIN = 3;   // Tysons Drückerplatte
const int STATUS_LED_PIN = 13;      // Status-LED: AN wenn Platte aktiv, AUS wenn gedrückt

// Stepper Motor Pins (4-Draht Stepper)
const int motorPins[] = {8, 9, 10, 11};

// Stepper Motor Schrittsequenz
const int steps[4][4] = {
  {1, 0, 0, 0},
  {0, 1, 0, 0},
  {0, 0, 1, 0},
  {0, 0, 0, 1}
};

int currentStep = 0;

// Zustandsvariablen
bool lastButtonState = LOW;
bool lastPlateState = LOW;
bool plateEnabled = false;           // Drückerplatte gesperrt/entsperrt
unsigned long lastPlatePress = 0;   // Entprellungs-Timer
const unsigned long DEBOUNCE_DELAY = 100; // 100ms Entprellung

// Funktions-Deklarationen
void handleSerialCommands();
void handleTestButton();
void handlePressurePlate();
void halfRotation();
void stepMotor();
void motorOff();

void setup() {
  Serial.begin(9600);
  
  // Pin-Konfiguration
  pinMode(BUTTON_PIN, INPUT);
  pinMode(PRESSURE_PLATE_PIN, INPUT_PULLUP);  // Pull-up für stabile Signale
  pinMode(STATUS_LED_PIN, OUTPUT);
  
  // Stepper Motor Pins
  for(int i = 0; i < 4; i++) {
    pinMode(motorPins[i], OUTPUT);
  }
  
  // Startzustand: Platte gesperrt
  plateEnabled = false;
  digitalWrite(STATUS_LED_PIN, LOW);
  
  Serial.println("Bereit - 'x' für halbe Umdrehung");
  Serial.println("Drückerplatte: GESPERRT");
  Serial.println("Kommandos: 'p'=entsperren, 'l'=sperren, 's'=status");
}

void loop() {
  // Serial-Kommandos verarbeiten
  handleSerialCommands();
  
  // Test-Button (bestehende Funktionalität)
  handleTestButton();
  
  // Tysons Drückerplatte
  handlePressurePlate();
  
  delay(20); // Kurzes Entprellen
}

void handleSerialCommands() {
  if (Serial.available()) {
    char input = Serial.read();
    
    switch(input) {
      case 'x':
      case 'X':
        // Bestehende Treat-Ausgabe Funktion
        halfRotation();
        break;
        
      case 'p':
      case 'P':
        // Drückerplatte entsperren
        plateEnabled = true;
        digitalWrite(STATUS_LED_PIN, HIGH);
        Serial.println("DRÜCKERPLATTE ENTSPERRT - Tyson kann Treats holen!");
        break;
        
      case 'l':
      case 'L':
        // Drückerplatte sperren
        plateEnabled = false;
        digitalWrite(STATUS_LED_PIN, LOW);
        Serial.println("DRÜCKERPLATTE GESPERRT - Tyson muss warten");
        break;
        
      case 's':
      case 'S':
        // Status abfragen
        Serial.print("STATUS:");
        Serial.println(plateEnabled ? "ENTSPERRT" : "GESPERRT");
        break;
    }
  }
}

void handleTestButton() {
  bool currentButtonState = digitalRead(BUTTON_PIN);
  
  // Test-Button gedrückt (nur wenn Platte entsperrt)
  if (currentButtonState == HIGH && plateEnabled) {
    if (lastButtonState == LOW) {
      Serial.println("Test-Button gedrückt!");
    }
  } 
  // Button losgelassen
  else if (currentButtonState == LOW && lastButtonState == HIGH) {
    Serial.println("Test-Button losgelassen");
  }
  
  lastButtonState = currentButtonState;
}

void handlePressurePlate() {
  bool currentPlateState = digitalRead(PRESSURE_PLATE_PIN);
  unsigned long currentTime = millis();
  
  // Entprellung: Nur verarbeiten wenn genug Zeit vergangen ist
  if (currentTime - lastPlatePress > DEBOUNCE_DELAY) {
    
    // Drückerplatte aktiviert (LOW wegen Pull-up)
    if (currentPlateState == LOW && lastPlateState == HIGH) {
      lastPlatePress = currentTime;
      
      if (plateEnabled) {
        // Tyson darf sich einen Treat holen!
        Serial.println("TYSON DRÜCKT DIE PLATTE - TREAT AUSGABE!");
        halfRotation(); // Treat ausgeben
      } else {
        // Platte ist gesperrt
        Serial.println("Drückerplatte gesperrt - Tyson muss warten!");
      }
    }
  }
  
  lastPlateState = currentPlateState;
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
  Serial.println("DEBUG: Stepper-Motor auf Pins 8,9,10,11 aktiv");
  
  // 2048 Schritte = halbe Umdrehung (4096 Steps = 360°)
  for(int i = 0; i < 2048; i++) {
    stepMotor();
  }
  
  motorOff();
  Serial.println("Fertig!");
  Serial.println("DEBUG: Bewegung abgeschlossen");
}