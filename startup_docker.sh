#!/usr/bin/env bash

export FLASK_APP=/app/flaskr
export FLASK_ENV=development
flask run -h 0.0.0.0 -p 80
