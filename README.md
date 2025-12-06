## ResQWear System 
# 1. Brugerinterface / Aktivering
Manuel aktiveringsknap integreret i tøjet.
Valgfri pre-aktiveringsstatus ("connected") for at bekræfte, at enheden er klar.

# 2. IoT-modul
Microcontroller (f.eks. ESP32 eller Arduino-kompatibel enhed)
GPS-modul til geolokation
Temperatur­sensor

# 3. Datahåndtering
Sender alarmsignal og sensordata til server / alarmcentral.
Periodiske “seneste kendte position”-opdateringer, hvis aktiveret.
Valgfri statusbeskeder (“connected”) til verificering af, at enheden fungerer korrekt før aktiviteten.

# 4. Kommunikation
Mobilkommunikation (LTE / NB-IoT) eller satellitmodul til områder uden dækning
Overfører data til skyen / alarmcentralen.

# 5. Cloud / Alarmcentral
Modtager position, temperatur og alarmdata
Viser realtids­lokation for redningsteams
Gemmer “seneste kendte positioner” og historiske sensor­data
