#!/bin/bash

if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
fi

echo "Starting Agent Workflow System..."
python app.py