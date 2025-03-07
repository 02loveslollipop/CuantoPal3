# This script builds the React app, the Capacitor android and ios projects

Write-Host "Building the React app"
Set-Location -Path "react" # Change to the React app directory
npm run build # Build the React app
Copy-Item -Path "dist/*" -Destination "../capacitor-android/dist" -Recurse -Force # Copy the build to Capacitor projects
Copy-Item -Path "dist/*" -Destination "../capacitor-ios/dist" -Recurse -Force # Copy the build to Capacitor projects
Write-Host "`u{2705} Done! The React app has been built."


Write-Host "Building the Capacitor android project"
Set-Location -Path "../capacitor-android" # Change to the Capacitor android project
npm install # Install the Capacitor android project dependencies
npx cap sync android # Sync the Capacitor android project
Write-Host "`u{2705} Done! The Capacitor android project has been updated."


Write-Host "Building the Capacitor ios project"
Set-Location -Path "../capacitor-ios" # Change to the Capacitor ios project
npm install # Install the Capacitor ios project dependencies
npx cap sync ios # Sync the Capacitor ios project
Write-Host " `u{2705} Done! The Capacitor ios project has been updated."

Write-Host "Done! You can now build for Android and iOS separately."
Write-Host "For Android, navigate to capacitor-android and run: npx cap sync android && npx cap open android"
Write-Host "For iOS, navigate to capacitor-ios and run: npx cap sync ios && npx cap open ios"