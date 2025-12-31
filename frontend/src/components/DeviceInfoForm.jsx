import React, { useState } from 'react';
import { FiX } from 'react-icons/fi';
import './DeviceInfoForm.css';

function DeviceInfoForm({ initialData, onSubmit, onClose }) {
  const [formData, setFormData] = useState(initialData || {
    device_type: '',
    os: '',
    os_version: '',
    manufacturer: '',
    model: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Device Information</h2>
          <button className="modal-close" onClick={onClose}>
            <FiX size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="device-form">
          <p className="form-description">
            Providing your device information helps me give you more accurate and relevant solutions.
          </p>

          <div className="form-group">
            <label htmlFor="device_type">Device Type *</label>
            <select
              id="device_type"
              name="device_type"
              value={formData.device_type}
              onChange={handleChange}
              required
            >
              <option value="">Select device type</option>
              <option value="laptop">Laptop</option>
              <option value="desktop">Desktop</option>
              <option value="phone">Phone</option>
              <option value="tablet">Tablet</option>
              <option value="printer">Printer</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="os">Operating System *</label>
            <select
              id="os"
              name="os"
              value={formData.os}
              onChange={handleChange}
              required
            >
              <option value="">Select operating system</option>
              <option value="windows">Windows</option>
              <option value="macos">macOS</option>
              <option value="linux">Linux</option>
              <option value="android">Android</option>
              <option value="ios">iOS</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="os_version">OS Version</label>
            <input
              type="text"
              id="os_version"
              name="os_version"
              value={formData.os_version}
              onChange={handleChange}
              placeholder="e.g., Windows 11, macOS Sonoma, Android 14"
            />
          </div>

          <div className="form-group">
            <label htmlFor="manufacturer">Manufacturer</label>
            <input
              type="text"
              id="manufacturer"
              name="manufacturer"
              value={formData.manufacturer}
              onChange={handleChange}
              placeholder="e.g., Dell, Apple, HP, Samsung"
            />
          </div>

          <div className="form-group">
            <label htmlFor="model">Model</label>
            <input
              type="text"
              id="model"
              name="model"
              value={formData.model}
              onChange={handleChange}
              placeholder="e.g., XPS 13, MacBook Pro, ThinkPad T14"
            />
          </div>

          <div className="form-actions">
            <button type="button" className="btn btn-outline" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Save Device Info
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default DeviceInfoForm;
