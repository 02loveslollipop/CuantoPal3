import React from 'react';
import splashIcon from '../assets/icon.svg';

export const Splash = () => {
  return (
    <div className="splash">
      <div className="splash__content">
        <img 
          src={splashIcon} 
          alt="App Icon"
          className="splash__icon"
        />
      </div>
    </div>
  );
};