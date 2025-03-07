import React from 'react';

/*Componente Alert
Muestra una alerta modal con título, mensaje y botones de acción.*/

export const Alert = ({
  isVisible,
  title,
  message,
  onCancel,
  onConfirm,
  confirmLabel = 'OK',
  isDestructive = false,
  showCancel = true
}) => {
  // Si la alerta no es visible, no se renderiza nada.
  if (!isVisible) return null;

  return (
    <div className="alert__overlay" onClick={e => {
      if (e.target === e.currentTarget && showCancel) onCancel();
    }}>
      <div className="alert__container">
        <div className="alert__content">
          <div className="alert__title">{title}</div>
          <div className="alert__message">{message}</div>
        </div>
        <div className="alert__actions">
          {showCancel && (
            <button 
              className="alert__button alert__button--cancel" 
              onClick={onCancel}
            >
              Cancelar
            </button>
          )}
          <button 
            className={`alert__button ${isDestructive ? 'alert__button--destructive' : ''} ${!showCancel ? 'alert__button--single' : ''}`}
            onClick={onConfirm}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};