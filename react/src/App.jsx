import React, { useState, useEffect } from 'react';
import { NavigationBar } from './components/nav-bar';
import { BottomNavigation } from './components/bottom-nav';
import { SettingsForm } from './components/settings';
import { Home } from './components/home';
import { Load } from './components/load';
import { Splash } from './components/splash';
import { Alert } from './components/alert';
import { SettingsManager } from './utils/settingsManager';
import { HomeIcon, Download, Save, Settings } from 'lucide-react';
import './styles/main.scss';

export const App = () => {
  const [showFirstTimeAlert, setShowFirstTimeAlert] = useState(false);
  const [activeNavIndex, setActiveNavIndex] = useState(0);
  const [showSettings, setShowSettings] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [settings, setSettings] = useState({
    minAcceptValue: 0.5,
    minValue: 0,
    maxValue: 100
  });

  useEffect(() => {
    const loadSettings = async () => {
      const settingsManager = SettingsManager.getInstance();
      const initialSettings = {
        minAcceptValue: settingsManager.minAcceptValue,
        minValue: settingsManager.minValue,
        maxValue: settingsManager.maxValue
      };
      const isFirstTime = localStorage.getItem("isFirstTime") === null;
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setShowFirstTimeAlert(isFirstTime);
      setSettings(initialSettings);
      setIsLoading(false);
    };

    loadSettings();
  }, []);

  const navItems = [
    {
      label: 'Home',
      icon: <HomeIcon size={24} />,
      onClick: () => setActiveNavIndex(0)
    },
    {
      label: 'Cargar',
      icon: <Download size={24} />,
      onClick: () => setActiveNavIndex(1)
    },
    {
      label: 'Guardar',
      icon: <Save size={24} />,
      onClick: () => setActiveNavIndex(2)
    }
  ];

  const handleFirstTimeAlert = async () => {
    await localStorage.setItem("isFirstTime", "false");
    setShowFirstTimeAlert(false);
    setShowSettings(true);
  };

  const handleBack = () => {
    if (showSettings) {
      setShowSettings(false);
    } else {
      window.history.back();
    }
  };

  if (isLoading) {
    return <Splash />;
  }

  const renderContent = () => {
    if (showSettings) {
      return (
        <SettingsForm
          onValuesChange={setSettings}
          initialValues={settings}
        />
      );
    }

    switch (activeNavIndex) {
      case 0:
        return <Home />;
      case 1:
        return <Load />;
      case 2:
        return <div>Save Screen</div>;
      default:
        return <Home />;
    }
  };

  return (
    <div className="app">
      <NavigationBar
        title={showSettings ? "Configuracion" : "Cuanto Pal 3"}
        onBack={handleBack}
        onAction={() => setShowSettings(true)}
        icon={Settings}
        hasIcon={!showSettings}
      />
      
      <main className="app__content">
        {renderContent()}
      </main>

      {!showSettings && (
        <BottomNavigation
          items={navItems}
          activeIndex={activeNavIndex}
        />
      )}

      <Alert
        isVisible={showFirstTimeAlert}
        title="Parece que es la primera vez que usas esta App"
        message="Para utilizer de manera corecta esta App es necesario configurarla para calcular las notas de manera correcta."
        confirmLabel="Configurar"
        showCancel={false}
        onConfirm={handleFirstTimeAlert}
      />
    </div>
  );
};

export default App;