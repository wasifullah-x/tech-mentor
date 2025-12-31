import React from 'react';
import { FiSun, FiMoon, FiInfo, FiSettings } from 'react-icons/fi';
import './Header.css';

function Header({ theme, toggleTheme, deviceInfo, onDeviceInfoClick }) {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="header-title">
            <span className="header-icon">🛠️</span>
            IT Support Assistant
          </h1>
          <span className="header-subtitle">AI-Powered Technical Help</span>
        </div>

        <div className="header-right">
          {deviceInfo && (
            <div className="device-badge" onClick={onDeviceInfoClick}>
              <FiInfo size={16} />
              <span>
                {deviceInfo.device_type} - {deviceInfo.os}
              </span>
            </div>
          )}

          {!deviceInfo && (
            <button className="btn btn-outline" onClick={onDeviceInfoClick}>
              <FiSettings size={16} />
              Set Device Info
            </button>
          )}

          <button 
            className="theme-toggle" 
            onClick={toggleTheme}
            aria-label="Toggle theme"
          >
            {theme === 'light' ? <FiMoon size={20} /> : <FiSun size={20} />}
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;
