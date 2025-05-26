import { expect, afterEach, beforeEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// extends Vitest's expect method with methods from react-testing-library
expect.extend(matchers);

// Mock global jest for compatibility
globalThis.jest = vi;

// Mock window.confirm for jsdom environment
beforeEach(() => {
  // Reset and set up window.confirm for each test
  const mockConfirm = vi.fn(() => true);
  
  Object.defineProperty(window, 'confirm', {
    writable: true,
    configurable: true,
    value: mockConfirm
  });
  
  globalThis.confirm = mockConfirm;
  vi.stubGlobal('confirm', mockConfirm);
});

// runs a cleanup after each test case (e.g. clearing jsdom)
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});
