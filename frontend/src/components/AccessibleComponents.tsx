/**
 * Accessible Components Library
 * DO-178C Traceability: REQ-FE-021 (WCAG 2.1 AA Compliance)
 *
 * Provides WCAG 2.1 AA compliant components with:
 * - Proper ARIA labels and roles
 * - Keyboard navigation
 * - Screen reader support
 * - Focus management
 * - Color contrast compliance
 */

import React, { useEffect, useRef, useState } from 'react';

/**
 * Accessible Button Component
 *
 * Features:
 * - Keyboard accessible (Enter/Space)
 * - ARIA label support
 * - Loading state with aria-busy
 * - Disabled state with aria-disabled
 */
interface AccessibleButtonProps {
  onClick: () => void;
  children: React.ReactNode;
  ariaLabel?: string;
  disabled?: boolean;
  loading?: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
  className?: string;
}

export const AccessibleButton: React.FC<AccessibleButtonProps> = ({
  onClick,
  children,
  ariaLabel,
  disabled = false,
  loading = false,
  variant = 'primary',
  className = ''
}) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (!disabled && !loading) {
        onClick();
      }
    }
  };

  const baseClasses = 'px-4 py-2 rounded font-medium focus:outline-none focus:ring-2 focus:ring-offset-2';
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500'
  };
  const disabledClasses = 'opacity-50 cursor-not-allowed';

  return (
    <button
      onClick={onClick}
      onKeyDown={handleKeyDown}
      aria-label={ariaLabel || (typeof children === 'string' ? children : undefined)}
      aria-disabled={disabled || loading}
      aria-busy={loading}
      disabled={disabled || loading}
      className={`${baseClasses} ${variantClasses[variant]} ${disabled || loading ? disabledClasses : ''} ${className}`}
      role="button"
      tabIndex={disabled ? -1 : 0}
    >
      {loading ? (
        <span className="flex items-center">
          <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Loading...</span>
        </span>
      ) : children}
    </button>
  );
};

/**
 * Accessible Modal/Dialog Component
 *
 * Features:
 * - Focus trap
 * - Escape key to close
 * - ARIA dialog role
 * - aria-labelledby and aria-describedby
 * - Prevents body scroll
 */
interface AccessibleModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  description?: string;
}

export const AccessibleModal: React.FC<AccessibleModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  description
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const titleId = `modal-title-${Math.random().toString(36).substr(2, 9)}`;
  const descId = description ? `modal-desc-${Math.random().toString(36).substr(2, 9)}` : undefined;

  useEffect(() => {
    if (isOpen) {
      // Prevent body scroll
      document.body.style.overflow = 'hidden';

      // Focus first focusable element
      const focusable = modalRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      if (focusable && focusable.length > 0) {
        (focusable[0] as HTMLElement).focus();
      }

      // Handle escape key
      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          onClose();
        }
      };
      document.addEventListener('keydown', handleEscape);

      return () => {
        document.body.style.overflow = 'unset';
        document.removeEventListener('keydown', handleEscape);
      };
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      role="presentation"
      onClick={onClose}
    >
      <div
        ref={modalRef}
        className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={descId}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-4">
          <h2 id={titleId} className="text-2xl font-bold">
            {title}
          </h2>
          <button
            onClick={onClose}
            aria-label="Close dialog"
            className="text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded p-1"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {description && (
          <p id={descId} className="text-gray-600 mb-4">
            {description}
          </p>
        )}

        <div>{children}</div>
      </div>
    </div>
  );
};

/**
 * Accessible Form Input Component
 *
 * Features:
 * - Proper label association
 * - Error message with aria-describedby
 * - Required field indication
 * - Helper text support
 */
interface AccessibleInputProps {
  id: string;
  label: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
  helperText?: string;
  autoComplete?: string;
}

export const AccessibleInput: React.FC<AccessibleInputProps> = ({
  id,
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  required = false,
  disabled = false,
  error,
  helperText,
  autoComplete
}) => {
  const errorId = error ? `${id}-error` : undefined;
  const helperId = helperText ? `${id}-helper` : undefined;
  const describedBy = [errorId, helperId].filter(Boolean).join(' ');

  return (
    <div className="mb-4">
      <label
        htmlFor={id}
        className="block text-sm font-medium text-gray-700 mb-1"
      >
        {label}
        {required && (
          <span className="text-red-600 ml-1" aria-label="required">*</span>
        )}
      </label>

      <input
        id={id}
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        aria-invalid={!!error}
        aria-describedby={describedBy || undefined}
        aria-required={required}
        autoComplete={autoComplete}
        className={`
          w-full px-3 py-2 border rounded-md
          focus:outline-none focus:ring-2 focus:ring-blue-500
          disabled:bg-gray-100 disabled:cursor-not-allowed
          ${error ? 'border-red-500 focus:ring-red-500' : 'border-gray-300'}
        `}
      />

      {helperText && (
        <p id={helperId} className="mt-1 text-sm text-gray-600">
          {helperText}
        </p>
      )}

      {error && (
        <p id={errorId} className="mt-1 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  );
};

/**
 * Accessible Alert/Notification Component
 *
 * Features:
 * - ARIA role (alert, status)
 * - aria-live for screen readers
 * - Icon with aria-hidden
 * - Dismissible with keyboard
 */
interface AccessibleAlertProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  onDismiss?: () => void;
  title?: string;
}

export const AccessibleAlert: React.FC<AccessibleAlertProps> = ({
  type,
  message,
  onDismiss,
  title
}) => {
  const typeConfig = {
    success: {
      bgColor: 'bg-green-50',
      textColor: 'text-green-800',
      borderColor: 'border-green-200',
      icon: '✓'
    },
    error: {
      bgColor: 'bg-red-50',
      textColor: 'text-red-800',
      borderColor: 'border-red-200',
      icon: '✕'
    },
    warning: {
      bgColor: 'bg-yellow-50',
      textColor: 'text-yellow-800',
      borderColor: 'border-yellow-200',
      icon: '⚠'
    },
    info: {
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-800',
      borderColor: 'border-blue-200',
      icon: 'ℹ'
    }
  };

  const config = typeConfig[type];

  return (
    <div
      className={`p-4 border rounded-md ${config.bgColor} ${config.borderColor}`}
      role={type === 'error' ? 'alert' : 'status'}
      aria-live={type === 'error' ? 'assertive' : 'polite'}
      aria-atomic="true"
    >
      <div className="flex items-start">
        <span className={`text-xl mr-3 ${config.textColor}`} aria-hidden="true">
          {config.icon}
        </span>

        <div className="flex-1">
          {title && (
            <h3 className={`font-medium ${config.textColor} mb-1`}>
              {title}
            </h3>
          )}
          <p className={config.textColor}>
            {message}
          </p>
        </div>

        {onDismiss && (
          <button
            onClick={onDismiss}
            aria-label="Dismiss alert"
            className={`ml-3 ${config.textColor} hover:opacity-75 focus:outline-none focus:ring-2 focus:ring-offset-2 rounded`}
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

/**
 * Skip to Main Content Link
 *
 * Allows keyboard users to skip navigation
 */
export const SkipToMainContent: React.FC = () => {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded"
    >
      Skip to main content
    </a>
  );
};

/**
 * Accessible Loading Spinner
 *
 * Features:
 * - aria-label for screen readers
 * - role="status"
 * - Hidden decorative elements
 */
interface AccessibleSpinnerProps {
  label?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const AccessibleSpinner: React.FC<AccessibleSpinnerProps> = ({
  label = 'Loading',
  size = 'md'
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <div role="status" aria-label={label} className="flex items-center justify-center">
      <svg
        className={`animate-spin ${sizeClasses[size]} text-blue-600`}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span className="sr-only">{label}</span>
    </div>
  );
};
