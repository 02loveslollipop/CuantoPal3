#! /bin/bash
# This script builds the React app and compiles a Ionic hybrid app

npm run build # Build the React app
npx cap sync # Sync the Capacitor project
npx cap android # Build the Android app
echo "Build complete"
