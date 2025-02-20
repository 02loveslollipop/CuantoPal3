import React from 'react';

export const BottomNavigation = ({
  items,
  activeIndex
}) => (
  <nav className="bottom-nav">
    {items.map((item, index) => (
      <button
        key={item.label}
        className={`bottom-nav__item ${index === activeIndex ? 'bottom-nav__item--active' : ''}`}
        onClick={item.onClick}
      >
        <div className="bottom-nav__icon">{item.icon}</div>
        <span className="bottom-nav__label">{item.label}</span>
      </button>
    ))}
  </nav>
);
