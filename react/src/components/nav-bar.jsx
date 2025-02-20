import React from 'react';
import {ChevronLeft} from 'lucide-react';

export const NavigationBar = ({
  title,
  onBack,
  onAction,
  icon,
  hasIcon
}) => {
    const ActionButton = hasIcon ? icon : null;


  return (
    <nav className="nav-bar">
      {onBack && (
        <button className="nav-bar__button" onClick={onBack}>
          <span className="back-icon">
              <ChevronLeft />
          </span>
          Atras
        </button>
      )}
      <span className="nav-bar__title">{title}</span>
        <button className="nav-bar__button" onClick={onAction}>
            {hasIcon ? <ActionButton /> : null}
        </button>
    </nav>
  );
};