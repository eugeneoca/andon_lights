@echo off
title RTU-NETWORK
:loop
python rtu-network.py client
goto loop
pause