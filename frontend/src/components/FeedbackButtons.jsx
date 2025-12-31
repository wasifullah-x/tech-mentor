import React, { useState } from 'react';
import { FiThumbsUp, FiThumbsDown, FiCheck } from 'react-icons/fi';
import './FeedbackButtons.css';

function FeedbackButtons({ onFeedback }) {
  const [feedbackGiven, setFeedbackGiven] = useState(false);
  const [showComment, setShowComment] = useState(false);
  const [comment, setComment] = useState('');
  const [selectedRating, setSelectedRating] = useState(null);

  const handleFeedback = async (rating, solved) => {
    setSelectedRating(rating);
    setShowComment(true);
  };

  const submitFeedback = async () => {
    if (selectedRating) {
      const solved = selectedRating === 'helpful';
      await onFeedback(selectedRating, solved, comment || null);
      setFeedbackGiven(true);
      setShowComment(false);
      
      // Hide feedback UI after 2 seconds
      setTimeout(() => {
        setFeedbackGiven(false);
      }, 2000);
    }
  };

  if (feedbackGiven) {
    return (
      <div className="feedback-container">
        <div className="feedback-success">
          <FiCheck size={16} />
          <span>Thank you for your feedback!</span>
        </div>
      </div>
    );
  }

  return (
    <div className="feedback-container">
      <div className="feedback-question">Was this solution helpful?</div>
      
      <div className="feedback-buttons">
        <button
          className={`feedback-btn ${selectedRating === 'helpful' ? 'active positive' : ''}`}
          onClick={() => handleFeedback('helpful', true)}
          disabled={showComment}
        >
          <FiThumbsUp size={18} />
          <span>Helpful</span>
        </button>
        
        <button
          className={`feedback-btn ${selectedRating === 'partially_helpful' ? 'active neutral' : ''}`}
          onClick={() => handleFeedback('partially_helpful', false)}
          disabled={showComment}
        >
          <span>Partially</span>
        </button>
        
        <button
          className={`feedback-btn ${selectedRating === 'not_helpful' ? 'active negative' : ''}`}
          onClick={() => handleFeedback('not_helpful', false)}
          disabled={showComment}
        >
          <FiThumbsDown size={18} />
          <span>Not Helpful</span>
        </button>
      </div>

      {showComment && (
        <div className="feedback-comment-section">
          <textarea
            className="feedback-textarea"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Any additional comments? (optional)"
            rows={3}
          />
          <div className="feedback-actions">
            <button
              className="btn btn-outline btn-sm"
              onClick={() => {
                setShowComment(false);
                setSelectedRating(null);
                setComment('');
              }}
            >
              Cancel
            </button>
            <button
              className="btn btn-primary btn-sm"
              onClick={submitFeedback}
            >
              Submit
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default FeedbackButtons;
