import React from 'react';

/* Componente Splash
Muestra una pantalla de inicio o carga mientras se prepara la aplicación.*/

export const Splash = () => {
  return (
    <div className="splash">
      <div className="splash__content">
        <img 
          src="icon.svg"
          alt="App Icon"
          className="splash__icon"
        />
      </div>
    </div>
  );
};