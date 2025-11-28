/**
 * Keyboard Shortcuts Hook
 * DO-178C Traceability: REQ-FE-022
 *
 * Provides global keyboard shortcuts for improved productivity.
 *
 * Shortcuts:
 * - Ctrl/Cmd + K: Global search
 * - Ctrl/Cmd + P: Quick navigation
 * - Ctrl/Cmd + N: New item (context-dependent)
 * - Ctrl/Cmd + S: Save
 * - Ctrl/Cmd + /: Show keyboard shortcuts help
 * - Escape: Close modals/dialogs
 * - Ctrl/Cmd + B: Toggle sidebar
 * - Ctrl/Cmd + E: Export current view
 * - Ctrl/Cmd + F: Find in page
 * - Alt + 1-9: Navigate to specific section
 */

import { useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

export interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  action: () => void;
  description: string;
}

export interface KeyboardShortcutsConfig {
  globalSearch?: () => void;
  quickNav?: () => void;
  newItem?: () => void;
  save?: () => void;
  export?: () => void;
  toggleSidebar?: () => void;
  findInPage?: () => void;
  navigateTo?: (section: number) => void;
}

/**
 * Use keyboard shortcuts hook
 *
 * @param config - Configuration object with shortcut handlers
 * @param enabled - Whether shortcuts are enabled (default: true)
 */
export function useKeyboardShortcuts(
  config: KeyboardShortcutsConfig = {},
  enabled: boolean = true
) {
  const navigate = useNavigate();

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!enabled) return;

    // Don't trigger shortcuts when typing in inputs
    const target = event.target as HTMLElement;
    if (
      target.tagName === 'INPUT' ||
      target.tagName === 'TEXTAREA' ||
      target.contentEditable === 'true'
    ) {
      // Allow Ctrl+S even in inputs
      if (!(event.ctrlKey || event.metaKey) || event.key !== 's') {
        return;
      }
    }

    const ctrl = event.ctrlKey || event.metaKey;
    const shift = event.shiftKey;
    const alt = event.altKey;
    const key = event.key.toLowerCase();

    // Ctrl/Cmd + K: Global search
    if (ctrl && key === 'k') {
      event.preventDefault();
      if (config.globalSearch) {
        config.globalSearch();
      }
    }

    // Ctrl/Cmd + P: Quick navigation
    else if (ctrl && key === 'p') {
      event.preventDefault();
      if (config.quickNav) {
        config.quickNav();
      }
    }

    // Ctrl/Cmd + N: New item
    else if (ctrl && key === 'n') {
      event.preventDefault();
      if (config.newItem) {
        config.newItem();
      }
    }

    // Ctrl/Cmd + S: Save
    else if (ctrl && key === 's') {
      event.preventDefault();
      if (config.save) {
        config.save();
      }
    }

    // Ctrl/Cmd + E: Export
    else if (ctrl && key === 'e') {
      event.preventDefault();
      if (config.export) {
        config.export();
      }
    }

    // Ctrl/Cmd + B: Toggle sidebar
    else if (ctrl && key === 'b') {
      event.preventDefault();
      if (config.toggleSidebar) {
        config.toggleSidebar();
      }
    }

    // Ctrl/Cmd + F: Find in page
    else if (ctrl && key === 'f') {
      event.preventDefault();
      if (config.findInPage) {
        config.findInPage();
      }
    }

    // Ctrl/Cmd + /: Show shortcuts help
    else if (ctrl && key === '/') {
      event.preventDefault();
      showShortcutsHelp();
    }

    // Alt + 1-9: Navigate to sections
    else if (alt && /^[1-9]$/.test(key)) {
      event.preventDefault();
      const section = parseInt(key);
      if (config.navigateTo) {
        config.navigateTo(section);
      } else {
        // Default navigation
        const routes = [
          '/dashboard',
          '/projects',
          '/requirements',
          '/design',
          '/tests',
          '/traceability',
          '/documents',
          '/product-structure',
          '/process-management'
        ];
        if (section <= routes.length) {
          navigate(routes[section - 1]);
        }
      }
    }
  }, [enabled, config, navigate]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
}

/**
 * Show keyboard shortcuts help dialog
 */
function showShortcutsHelp() {
  // Create modal overlay
  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
  `;

  // Create modal content
  const modal = document.createElement('div');
  modal.style.cssText = `
    background: white;
    padding: 2rem;
    border-radius: 0.5rem;
    max-width: 600px;
    max-height: 80vh;
    overflow-y: auto;
    color: #1a202c;
  `;

  modal.innerHTML = `
    <h2 style="font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">
      Keyboard Shortcuts
    </h2>
    <div style="display: grid; gap: 0.5rem;">
      <div style="display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #e2e8f0;">
        <span><kbd>Ctrl/⌘ + K</kbd></span>
        <span>Global search</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #e2e8f0;">
        <span><kbd>Ctrl/⌘ + P</kbd></span>
        <span>Quick navigation</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #e2e8f0;">
        <span><kbd>Ctrl/⌘ + N</kbd></span>
        <span>New item</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #e2e8f0;">
        <span><kbd>Ctrl/⌘ + S</kbd></span>
        <span>Save</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #e2e8f0;">
        <span><kbd>Ctrl/⌘ + E</kbd></span>
        <span>Export current view</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #e2e8f0;">
        <span><kbd>Ctrl/⌘ + B</kbd></span>
        <span>Toggle sidebar</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #e2e8f0;">
        <span><kbd>Ctrl/⌘ + F</kbd></span>
        <span>Find in page</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #e2e8f0;">
        <span><kbd>Ctrl/⌘ + /</kbd></span>
        <span>Show this help</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #e2e8f0;">
        <span><kbd>Alt + 1-9</kbd></span>
        <span>Navigate to section</span>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 0.5rem;">
        <span><kbd>Esc</kbd></span>
        <span>Close dialog</span>
      </div>
    </div>
    <button id="closeShortcutsHelp" style="
      margin-top: 1rem;
      padding: 0.5rem 1rem;
      background: #3b82f6;
      color: white;
      border: none;
      border-radius: 0.25rem;
      cursor: pointer;
      width: 100%;
    ">Close</button>
  `;

  overlay.appendChild(modal);
  document.body.appendChild(overlay);

  // Close handlers
  const closeHelp = () => overlay.remove();
  document.getElementById('closeShortcutsHelp')?.addEventListener('click', closeHelp);
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeHelp();
  });
  document.addEventListener('keydown', function escapeHandler(e) {
    if (e.key === 'Escape') {
      closeHelp();
      document.removeEventListener('keydown', escapeHandler);
    }
  });
}

/**
 * Get all available shortcuts
 */
export function getAvailableShortcuts(): KeyboardShortcut[] {
  return [
    {
      key: 'k',
      ctrl: true,
      action: () => {},
      description: 'Global search'
    },
    {
      key: 'p',
      ctrl: true,
      action: () => {},
      description: 'Quick navigation'
    },
    {
      key: 'n',
      ctrl: true,
      action: () => {},
      description: 'New item'
    },
    {
      key: 's',
      ctrl: true,
      action: () => {},
      description: 'Save'
    },
    {
      key: 'e',
      ctrl: true,
      action: () => {},
      description: 'Export current view'
    },
    {
      key: 'b',
      ctrl: true,
      action: () => {},
      description: 'Toggle sidebar'
    },
    {
      key: 'f',
      ctrl: true,
      action: () => {},
      description: 'Find in page'
    },
    {
      key: '/',
      ctrl: true,
      action: () => {},
      description: 'Show keyboard shortcuts'
    },
    {
      key: '1-9',
      alt: true,
      action: () => {},
      description: 'Navigate to section'
    }
  ];
}
