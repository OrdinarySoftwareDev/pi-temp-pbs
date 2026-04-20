#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
TARGET_DIR="/opt/pi-temp-pbs"
SERVICE_NAME="pi-temp-pbs.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"

echo "Deploying $PROJECT_DIR to $TARGET_DIR"

sudo mkdir -p "$TARGET_DIR"
sudo chown pi:pi "$TARGET_DIR"

sudo rsync -a "$PROJECT_DIR/" "$TARGET_DIR"
sudo chown -R pi:pi "$TARGET_DIR"

cd "$TARGET_DIR"
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

sudo tee "$SERVICE_FILE" > /dev/null << 'EOF'
[Unit]
Description=DS18B20 Sensor API for the Raspberry Pi
After=network.target

[Service]
User=pi
Group=www-data
WorkingDirectory=/opt/pi-temp-pbs
Environment=PATH=/opt/pi-temp-pbs/venv/bin
ExecStart=/opt/pi-temp-pbs/venv/bin/gunicorn --bind unix:app.sock -m 007 wsgi:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo "Deployed! Status:"
sudo systemctl status $SERVICE_NAME --no-pager
