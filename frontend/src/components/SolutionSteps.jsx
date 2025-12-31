import React, { useState } from 'react';
import { FiCheckCircle, FiAlertTriangle, FiChevronDown, FiChevronUp } from 'react-icons/fi';
import './SolutionSteps.css';

function SolutionSteps({ steps, warnings, nextSteps }) {
  const [completedSteps, setCompletedSteps] = useState(new Set());
  const [expandedSteps, setExpandedSteps] = useState(new Set([0])); // First step expanded by default

  const toggleStep = (stepNumber) => {
    setCompletedSteps(prev => {
      const newSet = new Set(prev);
      if (newSet.has(stepNumber)) {
        newSet.delete(stepNumber);
      } else {
        newSet.add(stepNumber);
      }
      return newSet;
    });
  };

  const toggleExpanded = (stepNumber) => {
    setExpandedSteps(prev => {
      const newSet = new Set(prev);
      if (newSet.has(stepNumber)) {
        newSet.delete(stepNumber);
      } else {
        newSet.add(stepNumber);
      }
      return newSet;
    });
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'safe': return 'success';
      case 'caution': return 'warning';
      case 'risky': return 'danger';
      default: return 'info';
    }
  };

  if (!steps || steps.length === 0) {
    return null;
  }

  return (
    <div className="solution-steps-container">
      {warnings && warnings.length > 0 && (
        <div className="warnings-section">
          {warnings.map((warning, index) => (
            <div key={index} className="warning-item">
              <FiAlertTriangle size={16} />
              <span>{warning}</span>
            </div>
          ))}
        </div>
      )}

      <div className="steps-header">
        <h3>Step-by-Step Solution</h3>
        <span className="steps-count">
          {completedSteps.size} / {steps.length} completed
        </span>
      </div>

      <div className="steps-list">
        {steps.map((step) => {
          const isCompleted = completedSteps.has(step.step_number);
          const isExpanded = expandedSteps.has(step.step_number);

          return (
            <div
              key={step.step_number}
              className={`step-item ${isCompleted ? 'completed' : ''}`}
            >
              <div className="step-header" onClick={() => toggleExpanded(step.step_number)}>
                <div className="step-left">
                  <button
                    className="step-checkbox"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleStep(step.step_number);
                    }}
                  >
                    {isCompleted && <FiCheckCircle size={20} />}
                  </button>
                  <div className="step-number">Step {step.step_number}</div>
                  <span className={`risk-badge badge-${getRiskColor(step.risk_level)}`}>
                    {step.risk_level}
                  </span>
                </div>
                <button className="expand-button">
                  {isExpanded ? <FiChevronUp size={18} /> : <FiChevronDown size={18} />}
                </button>
              </div>

              <div className="step-action">{step.action}</div>

              {isExpanded && (
                <div className="step-details">
                  <div className="step-detail-item">
                    <strong>Why this helps:</strong>
                    <p>{step.explanation}</p>
                  </div>

                  {step.expected_outcome && (
                    <div className="step-detail-item">
                      <strong>Expected result:</strong>
                      <p>{step.expected_outcome}</p>
                    </div>
                  )}

                  {step.troubleshooting_tips && step.troubleshooting_tips.length > 0 && (
                    <div className="step-detail-item">
                      <strong>Tips:</strong>
                      <ul>
                        {step.troubleshooting_tips.map((tip, index) => (
                          <li key={index}>{tip}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {nextSteps && (
        <div className="next-steps-section">
          <h4>What if this doesn't work?</h4>
          <p>{nextSteps}</p>
        </div>
      )}
    </div>
  );
}

export default SolutionSteps;
