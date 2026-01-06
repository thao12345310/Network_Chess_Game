#!/bin/bash
# Script to rebuild C++ client

echo "=== Rebuilding C++ Chess Client ==="

cd client

echo "Cleaning old build..."
make clean

echo "Building client..."
make

echo "Installing shared library to ui/"
make install

echo ""
echo "=== Build complete! ==="
echo "You can now run the UI application"
