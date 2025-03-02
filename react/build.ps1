# PowerShell script to build React app and compile Ionic hybrid app

# Build the React app
npm run build

# Sync the Capacitor project
npx cap sync

Write-Host "Build complete"
