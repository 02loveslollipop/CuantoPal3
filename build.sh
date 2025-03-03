#! /bin/bash
# This script initializes the Capacitor android and ios projects
echo "Building the React app"
cd react # Change to the React app directory
npm install # Install the React app dependencies
npm run build # Build the React app
cp -r dist ../capacitor-android/dist # Copy the build to the Capacitor android project
cp -r dist ../capacitor-ios/dist # Copy the build to the Capacitor ios project
echo "✅ Done! The React app has been built."
echo "Building the Capacitor android project"
cd ../capacitor-android # Change to the Capacitor android project directory
npm install # Install the Capacitor android project dependencies
npx cap sync android # Sync the Capacitor android project
echo "✅ Done! The Capacitor android project has been updated."
echo "Building the Capacitor ios project"
cd ../capacitor-ios # Change to the Capacitor ios project directory
npm install # Install the Capacitor ios project dependencies
npx cap sync ios # Sync the Capacitor ios project
echo "✅ Done! The Capacitor ios project has been updated."
echo "✨ Done! You can now build for Android and iOS separately."
echo "📱 For Android, navigate to capacitor-android and run: npx cap sync android && npx cap open android
echo "🍏 For iOS, navigate to capacitor-ios and run: npx cap sync ios && npx cap open ios