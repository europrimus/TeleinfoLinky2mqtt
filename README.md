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

Modifier si nécessaire `teleinfo2mqtt.py`:
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

#### creation d'un service `teleinfo2mqtt`

Modifier si nécessaire le fichier `teleinfo2mqtt.service`.  
La ligne suivante doit correspondre au répertoire d'installation.
```
ExecStart=/home/yunohost.app/teleinfo2mqtt/.python.venv/bin/python3 /home/yunohost.app/teleinfo2mqtt/teleinfo2mqtt.py
```

#### Installation du service `teleinfo2mqtt`

```bash
cp teleinfo2mqtt.service /etc/systemd/system/teleinfo2mqtt.service
systemctl daemon-reload
systemctl enable teleinfo2mqtt.service
systemctl start  teleinfo2mqtt.service
```

Pour vérifier que le service fonctione:
```bash
systemctl status teleinfo2mqtt.service
```

Une fois lancé, les infos listées dans `linky_args` du fichier `teleinfo2mqtt.py` sont publiées dans le broker dès réception.

le service est démarré au démarrage du réseau (Ethernet) et relancé si jamais il s'arrête

#### Redémarrage du service `teleinfo2mqtt` après modifications

```bash
systemctl daemon-reload
systemctl restart teleinfo2mqtt.service
```

#### Suivi des messages postés

```bash
mqttui --broker mqtt://127.0.0.1 --username $MQTTUI_USERNAME --password $MQTTUI_PASSWORD
```
