#! /bin/bash
# This script builds the React app and compiles a Ionic hybrid app
echo "Building the React app"
npm run build # Build the React app
echo "Moving the build to the Capacitor android and ios projects"
cp -r dist ../capacitor-android/dist # Copy the build to the Capacitor android project
cp -r dist ../capacitor-ios/dist # Copy the build to the Capacitor ios project 
echo "Building the Capacitor android project"
cd ../capacitor-android # Change to the Capacitor android project directory
npx cap sync android # Sync the Capacitor android project
echo "Building the Capacitor ios project"
cd ../capacitor-ios # Change to the Capacitor ios project directory
npx cap sync ios # Sync the Capacitor ios project
echo "Build complete"
