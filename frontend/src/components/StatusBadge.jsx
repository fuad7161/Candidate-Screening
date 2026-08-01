import React from 'react';
import './StatusBadge.css';

const STATUS_CONFIG = {
  applied: { label: 'Applied', className: 'status-submitted' },
  submitted: { label: 'Applied', className: 'status-submitted' },
  shortlisted: { label: 'Shortlisted', className: 'status-shortlisted' },
  interview: { label: 'Interview', className: 'status-under-review' },
  rejected: { label: 'Rejected', className: 'status-rejected' },
  hired: { label: 'Hired', className: 'status-hired' },
};

function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] || { label: status, className: 'status-default' };
  return (
    <span className={`application-status-badge ${config.className}`}>
      {config.label}
    </span>
  );
}

export default StatusBadge;
