#!/bin/sh
$env:FLASK_APP = "bot.py"
flask run --host=0.0.0.0 --port=80 