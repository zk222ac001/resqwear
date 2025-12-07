<img width="1189" height="635" alt="image" src="https://github.com/user-attachments/assets/a44bba5a-2cd2-4eb4-b662-44051ad2529e" />

## ResQWear System MOCK Simulation 
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

# Login User Role :
user name : operator1 
password : op123

user name : dispatcher1 
password : dp123

Starter som program kører text prompt i terminalen  
> streamlit run app.py

<img width="1920" height="1200" alt="image" src="https://github.com/user-attachments/assets/2a4be6f6-bb11-4070-8fab-26163f85fdf1" />

# Login som operator1

<img width="1920" height="1200" alt="image" src="https://github.com/user-attachments/assets/941655b5-bdfc-4641-bd20-93d281a01580" />

<img width="1920" height="1200" alt="image" src="https://github.com/user-attachments/assets/93c0d448-e82c-4b87-9463-1c8ed8637be5" />

<img width="1920" height="1200" alt="image" src="https://github.com/user-attachments/assets/106ec84c-8dcd-4d54-80f4-3832335130bc" />

<img width="1920" height="1200" alt="image" src="https://github.com/user-attachments/assets/9444c104-2c50-4d55-b59a-2cb6c3fa9186" />

# Login som dispatcher 

<img width="1920" height="1200" alt="image" src="https://github.com/user-attachments/assets/f2ddcdb6-09c1-4a71-a188-62aa88dc66d5" />

## Run som Command for Docker containarizarion:
docker-compose build
docker-compose up

