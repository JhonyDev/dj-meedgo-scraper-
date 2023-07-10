#!/bin/sh

ssh admin22@20.244.115.152 <<EOF
  cd dj-meedgo
  git pull 
  source env/bin/activate
  ./manage.py makemigrations
  ./manage.py migrate
  sudo systemctl restart nginx
  sudo systemctl restart gunicorn.service
  sudo systemctl restart gunicorn.socket
  exit
EOF