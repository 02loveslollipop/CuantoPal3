import React, { useState } from 'react';
import { SettingsManager } from '../utils/settingsManager';

export const SettingsForm = ({
    onValuesChange
  }) => {
    const settings = SettingsManager.getInstance();
    const [values, setValues] = useState({
      minAcceptValue: settings.minAcceptValue,
      minValue: settings.minValue,
      maxValue: settings.maxValue
    });
  
    const handleChange = (field) => (e) => {
      const newValue = parseFloat(e.target.value);
      
      settings[field] = newValue;
      
      setValues({
        minAcceptValue: settings.minAcceptValue,
        minValue: settings.minValue,
        maxValue: settings.maxValue
      });
      
      onValuesChange({
        minAcceptValue: settings.minAcceptValue,
        minValue: settings.minValue,
        maxValue: settings.maxValue
      });
    };

  return (
    <div className="settings__container">
      <div className="settings__header">
        <h2 className="settings__title">Configuracion</h2>
      </div>
      
      <form className="settings__group">
        <div className="settings__row">
          <label className="settings__label">Cuanto necesito</label>
          <input
            type="number"
            className="settings__input"
            placeholder="Enter value"
            step="0.1"
            value={values.minAcceptValue}
            onChange={handleChange('minAcceptValue')}
          />
        </div>
        
        <div className="settings__row">
          <label className="settings__label">Nota minima</label>
          <input
            type="number"
            className="settings__input"
            placeholder="Enter value"
            step="0.1"
            value={values.minValue}
            onChange={handleChange('minValue')}
          />
        </div>
        
        <div className="settings__row">
          <label className="settings__label">Nota maxima</label>
          <input
            type="number"
            className="settings__input"
            placeholder="Enter value"
            step="0.1"
            value={values.maxValue}
            onChange={handleChange('maxValue')}
          />
        </div>
      </form>
    </div>
  );
};