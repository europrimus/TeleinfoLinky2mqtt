# Scripts bash et Python permettant de monitorer la telealimentation du compteur Linky

* Le Linky est en mode 'standard' (nouveau mode à 9600 bauds au lieu de 1200), ici en triphasé donc avec IRMS1/2/3 et URMS1/2/3.
NB: Ces items ne sont pas forcément disponibles ni n'ont les mêmes noms en mode 'historique' (à 1200 bauds)

* Changer baudrate=9600 en baudrate=1200 pour fonctionner en mode 'historique'

## Linky vers MQTT

### 1. Installer

```bash
git clone git@github.com:europrimus/TeleinfoLinky2mqtt.git
cd TeleinfoLinky2mqtt
python3 -m venv .python.venv
source .python.venv/bin/activate
pip3 install -r requirements.txt
deactivate
```

### 2. Configurer

Modifier si nécessaire `mqtt_linky_read_publish.py`:
```python
client_id="linky2mqtt"
linky_args = ["ADCO", "ISOUSC", "BASE", "IINST", "PAPP"]
broker="127.0.0.1"
port = 1883
"""
Mode de teleinformation dit 'standard':
  permettant de monitorer les 3 phases
  utilise un baudrate=9600
NB: Le mode de teleinformation dit 'historique':
  ne permet pas de monitorer le triphasé
  fonctionne avec baudrate=1200
"""
baudrate=1200
serialPort="/dev/ttyUSB1"
```

### 3. Lancement au demarrage du script

#### creation d'un service `mqtt_linky`

Modifier si nécessaire le fichier `mqtt_linky.service`.  
La ligne suivante doit correspondre au répertoire d'installation.
```
ExecStart=/home/yunohost.app/teleinfo2mqtt/.python.venv/bin/python3 /home/yunohost.app/teleinfo2mqtt/mqtt_linky_read_publish.py
```

#### Installation du service `mqtt_linky`

```bash
cp mqtt_linky.service /etc/systemd/system/mqtt_linky.service
systemctl daemon-reload
systemctl enable mqtt_linky.service
systemctl start  mqtt_linky.service
systemctl status mqtt_linky.service
```

Une fois lancé, les infos listées dans `linky_args` du fichier `mqtt_linky_read_publish.py` sont publiées dans le broker dès réception.

le service est démarré au démarrage du réseau (Ethernet) et relancé si jamais il s'arrête

#### Redémarrage du service `mqtt_linky` après modifications

```bash
systemctl daemon-reload
systemctl restart mqtt_linky.service
```

#### Suivi des messages postés

```bash
mqttui --broker mqtt://127.0.0.1 --username $MQTTUI_USERNAME --password $MQTTUI_PASSWORD
```
