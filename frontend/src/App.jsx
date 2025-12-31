import React, { useState, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import DeviceInfoForm from './components/DeviceInfoForm';
import Header from './components/Header';
import './App.css';

function App() {
  const [theme, setTheme] = useState('light');
  const [deviceInfo, setDeviceInfo] = useState(null);
  const [showDeviceForm, setShowDeviceForm] = useState(false);

  useEffect(() => {
    // Load theme from localStorage
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  const handleDeviceInfoSubmit = (info) => {
    setDeviceInfo(info);
    setShowDeviceForm(false);
  };

  return (
    <div className="app">
      <Header 
        theme={theme} 
        toggleTheme={toggleTheme}
        deviceInfo={deviceInfo}
        onDeviceInfoClick={() => setShowDeviceForm(true)}
      />
      
      <main className="main-content">
        <ChatWindow deviceInfo={deviceInfo} />
      </main>

      {showDeviceForm && (
        <DeviceInfoForm
          initialData={deviceInfo}
          onSubmit={handleDeviceInfoSubmit}
          onClose={() => setShowDeviceForm(false)}
        />
      )}
    </div>
  );
}

export default App;
