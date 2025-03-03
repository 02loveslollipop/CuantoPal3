#! /bin/bash
# This script builds the React app and compiles a Ionic hybrid app

npm run build # Build the React app
cp -r dist ../capacitor-android/dist # Copy the build to the Capacitor android project
cp -r dist ../capacitor-ios/dist # Copy the build to the Capacitor ios project
npx cap sync # Sync the Capacitor project
npx cap android # Build the Android app
echo "Build complete"
