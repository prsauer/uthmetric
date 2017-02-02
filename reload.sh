#!/bin/bash
git pull origin master
sudo service supervisor stop
sudo pkill gunicorn
sudo service supervisor start
