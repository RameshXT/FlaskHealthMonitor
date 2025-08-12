#!/bin/bash

cd /home/ec2-user/test/FlaskHealthMonitor/health-checker
/usr/bin/python3 /home/ec2-user/test/FlaskHealthMonitor/health-checker/health-checker.py >> /home/ec2-user/test/FlaskHealthMonitor/logs/health-checker-log.txt 2>&1
