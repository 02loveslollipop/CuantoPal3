import React, { useState, useEffect } from 'react';
import { NavigationBar } from './components/nav-bar';
import { BottomNavigation } from './components/bottom-nav';
import { SettingsForm } from './components/settings';
import { Save as SaveComp } from './components/save';
import { Home } from './components/home';
import { Load } from './components/load';
import { Splash } from './components/splash';
import { Alert } from './components/alert';
import { SettingsManager } from './utils/settingsManager';
import { fillLocalStorage } from './utils/Utils';
import { HomeIcon, Download, Save, Settings } from 'lucide-react';
import { Result } from './components/result';
import './styles/main.scss';

export const App = () => {
  const [showFirstTimeAlert, setShowFirstTimeAlert] = useState(false);
  const [activeNavIndex, setActiveNavIndex] = useState(0);
  const [showSettings, setShowSettings] = useState(false);
  const [showReturn, setShowReturn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [settings, setSettings] = useState({
    minAcceptValue: 0.5,
    minValue: 0,
    maxValue: 100
  });
  const [showResult, setShowResult] = useState(false);


  useEffect(() => {
    const loadSettings = async () => {
      const settingsManager = SettingsManager.getInstance();
      const initialSettings = {
        minAcceptValue: settingsManager.minAcceptValue,
        minValue: settingsManager.minValue,
        maxValue: settingsManager.maxValue
      };
      const isFirstTime = localStorage.getItem("isFirstTime") === null;

      //TODO: Remove from here for production
      //if first time and its debug call the fill LocalStorage function from utils
      


      if (process.env.NODE_ENV === 'development' && isFirstTime) {
        fillLocalStorage();
      }
      //TODO: Remove to here for production
      
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

  const handleOnAction = () => {
    if (!showSettings) setShowReturn(true);
    else setShowReturn(false);
    setShowSettings(true);
  }

  const handleToSettings = () => {
    setShowSettings(true);
    setShowReturn(true);
  }

  const handleFirstTimeAlert = async () => {
    await localStorage.setItem("isFirstTime", "false");
    setShowFirstTimeAlert(false);
    setShowSettings(true);
    setShowReturn(true);
  };
  
  const onCalculate = () => {
    setShowResult(true);
    setShowReturn(true);
    setShowSettings(false);
  }

  const handleBack = () => {
    if (showSettings) {
      setShowReturn(false);
      setShowSettings(false);

    } else if (showResult) {
      setShowResult(false)
      setShowReturn(false);
      setShowReturn(false);
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

    if (showResult) {
      return <Result/>;
    }

    switch (activeNavIndex) {
      case 0:
        return <Home onCalculate={onCalculate} toSettings={handleToSettings} />;
      case 1:
        return <Load setActiveNavIndex={setActiveNavIndex} />;
      case 2:
        return <SaveComp setActiveNavIndex={setActiveNavIndex} />;
      default:
        return <Home />;
    }
  };

  //if ShowSetting is true or showResult is true disable the bottom navigation
  const showBotom = !showSettings && !showResult;
  const showSettingsIcon = !showSettings && !showResult;

  return (
    <div className="app">
      <NavigationBar
        title={showSettings ? "Configuracion" : "Cuanto Pal 3"}
        hasBack={showReturn}
        onBack={handleBack}
        onAction={handleOnAction}
        icon={Settings}
        hasIcon={showSettingsIcon}
      />
      
      <main className="app__content">
        {renderContent()}
      </main>

      {showBotom && (
        <BottomNavigation
          items={navItems}
          activeIndex={activeNavIndex}
        />
      )}

      <Alert
        isVisible={showFirstTimeAlert}
        title="Parece que es la primera vez que usas esta App"
        message="Para utilizar esta App es necesario configurarla para calcular las notas de manera correcta."
        confirmLabel="Configurar"
        showCancel={false}
        onConfirm={handleFirstTimeAlert}
      />
    </div>
  );
};

export default App;