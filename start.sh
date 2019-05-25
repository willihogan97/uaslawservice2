#!/bin/bash

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn server2.wsgi:application \
    --bind 0.0.0.0:21320 \
    --workers 3