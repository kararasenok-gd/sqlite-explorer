#!/bin/bash

echo "Installing dependencies..."
pip install rich prompt_toolkit

if [ $? -ne 0 ]; then
    echo "Failed to install dependencies. Please check your Python and pip installation."
    exit 1
fi

echo "All dependencies are installed successfully!"

clear
echo "Starting SQLite Explorer..."
python3 main.py
