import React from 'react';
import {ChevronLeft} from 'lucide-react';

export const NavigationBar = ({
  title,
  hasBack,
  onBack,
  onAction,
  icon,
  hasIcon
}) => {
    const ActionButton = hasIcon ? icon : null;

    const showBack = hasBack && onBack;

  return (
    <nav className="nav-bar">
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