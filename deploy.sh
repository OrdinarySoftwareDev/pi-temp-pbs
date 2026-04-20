#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
SERVICE_NAME="pi-temp-pbs.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"

echo "Deploying $PROJECT_DIR to /opt/pi-temp-pbs"

sudo mkdir -p /opt/pi-temp-pbs
sudo chown pi:pi /opt/pi-temp-pbs

sudo rsync -a "$PROJECT_DIR/" /opt/pi-temp-pbs/
sudo chown -R pi:pi /opt/pi-temp-pbs


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
