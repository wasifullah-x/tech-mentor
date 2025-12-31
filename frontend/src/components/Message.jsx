import React from 'react';
import ReactMarkdown from 'react-markdown';
import './Message.css';

function Message({ message }) {
  const { role, content, timestamp, isError } = message;

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  return (
    <div className={`message ${role} ${isError ? 'error' : ''}`}>
      <div className="message-header">
        <span className="message-role">
          {role === 'user' ? '👤 You' : '🤖 Assistant'}
        </span>
        {timestamp && (
          <span className="message-time">{formatTime(timestamp)}</span>
        )}
      </div>
      <div className="message-content">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    </div>
  );
}

export default Message;
