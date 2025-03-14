import React from 'react';
import {ChevronLeft} from 'lucide-react';

/* Componente NavigationBar
Renderiza una barra de navegación superior con título, botón de retroceso y un botón de acción adicional.*/

export const NavigationBar = ({
  title,
  hasBack,
  onBack,
  onAction,
  icon,
  hasIcon
}) => {
    const ActionButton = hasIcon ? icon : null;

    // Determina si se debe mostrar el botón de retroceso comprobando ambas props.
    const showBack = hasBack && onBack;

  return (
    <nav className="nav-bar">
      {/* Botón de retroceso */}
      {showBack && (
        <button className="nav-bar__button" onClick={onBack}>
          <span className="back-icon">
              <ChevronLeft />
          </span>
          Atras
        </button>
      )}
      {!showBack && <div className="nav-bar__button" />}
      <span className="nav-bar__title">{title}</span>
        <button className="nav-bar__button" onClick={onAction}>
            {hasIcon ? <ActionButton /> : null}
        </button>
    </nav>
  );
};