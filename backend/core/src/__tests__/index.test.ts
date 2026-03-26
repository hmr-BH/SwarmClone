import { describe, it, expect } from 'vitest';
import { VERSION } from '../index.js';

describe('Core Module', () => {
  it('should export VERSION constant', () => {
    expect(VERSION).toBeDefined();
    expect(VERSION).toBe('0.1.0');
  });

  it('should have correct version format', () => {
    const versionPattern = /^\d+\.\d+\.\d+$/;
    expect(VERSION).toMatch(versionPattern);
  });
});
