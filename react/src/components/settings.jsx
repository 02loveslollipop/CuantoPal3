import React, { useState } from 'react';
import { SettingsManager } from '../utils/settingsManager';

/* Componente SettingsForm
Permite al usuario modificar configuraciones relacionadas con las notas:
Notifica los cambios al componente padre mediante onValuesChange.*/

export const SettingsForm = ({
    onValuesChange
  }) => {
    // Se obtiene la instancia única para acceder a la configuración actual.
    const settings = SettingsManager.getInstance();
    // Se inicializa el estado local con los valores actuales de configuración.
    const [values, setValues] = useState({
      minAcceptValue: settings.minAcceptValue,
      minValue: settings.minValue,
      maxValue: settings.maxValue
    });
  
    // Maneja el cambio de un campo de configuración.
    const handleChange = (field) => (e) => {
      const newValue = parseFloat(e.target.value);
      
      // Actualiza el valor en el objeto de configuración.
      settings[field] = newValue;
      
      // Actualiza el estado local con los valores actuales del SettingsManager.
      setValues({
        minAcceptValue: settings.minAcceptValue,
        minValue: settings.minValue,
        maxValue: settings.maxValue
      });
      
      // Notifica al componente padre sobre el cambio en los valores.
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
        
        {/* Campo para "Nota minima" */}
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
        
        {/* Campo para "Nota maxima" */}
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