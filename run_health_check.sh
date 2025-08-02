#!/bin/bash

cd /home/ec2-user/test/FlaskHealthMonitor/automation
/usr/bin/python3 /home/ec2-user/test/FlaskHealthMonitor/automation/health_checker.py >> /home/ec2-user/test/FlaskHealthMonitor/logs/health-checker-log.txt 2>&1
