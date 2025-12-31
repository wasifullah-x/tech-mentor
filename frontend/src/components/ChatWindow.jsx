import React, { useState, useEffect, useRef } from 'react';
import { FiSend, FiTrash2, FiAlertCircle } from 'react-icons/fi';
import { chatAPI, healthAPI } from '../services/api';
import Message from './Message';
import SolutionSteps from './SolutionSteps';
import FeedbackButtons from './FeedbackButtons';
import './ChatWindow.css';

function ChatWindow({ deviceInfo }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [currentSolution, setCurrentSolution] = useState(null);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Check API health on mount
    checkAPIHealth();
    
    // Add welcome message
    setMessages([{
      role: 'assistant',
      content: `👋 Hello! I'm your IT Support Assistant. I'm here to help you solve technology problems.

**I can help with:**
• Wi-Fi and network issues
• Computer performance problems
• Hardware troubleshooting
• Software errors and crashes
• Mobile device issues
• Printer and peripheral problems

**How to get the best help:**
1. Describe your problem in detail
2. Mention what you've already tried
3. Include any error messages you see

What tech problem can I help you solve today?`,
      timestamp: new Date()
    }]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const checkAPIHealth = async () => {
    try {
      await healthAPI.checkHealth();
      setApiStatus('online');
      setError(null);
    } catch (err) {
      setApiStatus('offline');
      setError('Cannot connect to API server. Please make sure the backend is running.');
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setError(null);

    // Add user message
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    }]);

    setLoading(true);

    try {
      // Prepare conversation history (last 10 messages)
      const history = messages.slice(-10).map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      // Call API
      const response = await chatAPI.sendMessage(
        userMessage,
        sessionId,
        deviceInfo,
        history,
        'beginner'
      );

      // Update session ID
      if (response.session_id && !sessionId) {
        setSessionId(response.session_id);
      }

      // Add assistant response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        data: response
      }]);

      // Store current solution for feedback
      setCurrentSolution(response);

    } catch (err) {
      console.error('Error sending message:', err);
      setError(err.response?.data?.error || 'Failed to get response. Please try again.');
      
      // Add error message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '❌ I apologize, but I encountered an error. Please try again or rephrase your question.',
        timestamp: new Date(),
        isError: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    if (confirm('Are you sure you want to clear the chat history?')) {
      setMessages([{
        role: 'assistant',
        content: '👋 Chat cleared! What can I help you with?',
        timestamp: new Date()
      }]);
      setSessionId(null);
      setCurrentSolution(null);
      setError(null);
    }
  };

  const handleFeedback = async (rating, solved, comment) => {
    if (!sessionId) return;

    try {
      await chatAPI.submitFeedback(sessionId, rating, solved, comment);
      // Show success (you could add a toast notification here)
      console.log('Feedback submitted successfully');
    } catch (err) {
      console.error('Error submitting feedback:', err);
    }
  };

  return (
    <div className="chat-window">
      {apiStatus === 'offline' && (
        <div className="api-status-banner error">
          <FiAlertCircle size={20} />
          <span>{error}</span>
          <button onClick={checkAPIHealth} className="btn btn-outline btn-sm">
            Retry
          </button>
        </div>
      )}

      <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className="message-wrapper">
            <Message message={message} />
            
            {/* Show solution steps if available */}
            {message.role === 'assistant' && message.data?.solution_steps && message.data.solution_steps.length > 0 && (
              <SolutionSteps 
                steps={message.data.solution_steps}
                warnings={message.data.warnings}
                nextSteps={message.data.next_steps}
              />
            )}
            
            {/* Show feedback buttons for last assistant message */}
            {message.role === 'assistant' && 
             !message.isError && 
             index === messages.length - 1 && 
             sessionId && (
              <FeedbackButtons onFeedback={handleFeedback} />
            )}
          </div>
        ))}

        {loading && (
          <div className="message-wrapper">
            <div className="message assistant loading-message">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span className="loading-text">Analyzing your problem...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <button
          className="btn btn-outline"
          onClick={handleClearChat}
          title="Clear chat"
        >
          <FiTrash2 size={18} />
        </button>

        <form onSubmit={handleSendMessage} className="input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe your tech problem..."
            className="message-input"
            disabled={loading || apiStatus === 'offline'}
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={!input.trim() || loading || apiStatus === 'offline'}
          >
            <FiSend size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatWindow;
