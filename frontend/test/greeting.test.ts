import { describe, expect, it } from 'vitest';
import { add, greet } from '../src/greeting';

describe('greeting', () => {
  it('greets by name', () => {
    expect(greet('harness')).toBe('Hello, harness');
  });

  it('adds two numbers', () => {
    expect(add(2, 3)).toBe(5);
  });
});
