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
echo "✨ Done! You can now build for Android and iOS separately."
echo "📱 For Android, navigate to capacitor-android and run: npx cap sync android && npx cap open android"
echo "🍏 For iOS, navigate to capacitor-ios and run: npx cap sync ios && npx cap open ios"