import { describe, expect, it } from 'vitest';
import type { ChatResponse } from '../src/api';
import { summarizeResults } from '../src/ui/render';

function makeResp(
  results: ChatResponse['results'],
  intentName = 'file',
): ChatResponse {
  return {
    message: 'x',
    intent: { name: intentName, confidence: 0.8, matched: [] },
    plan: { intent: { name: intentName, confidence: 0.8, matched: [] }, source: 'fallback', steps: [] },
    results,
    trace: { id: '1', steps: [] },
  };
}

describe('summarizeResults', () => {
  it('summarizes ok results with string output', () => {
    const resp = makeResp([{ tool: 'read_file', status: 'ok', output: 'hello' }]);
    expect(summarizeResults(resp)).toContain('read_file: hello');
  });

  it('marks denied results', () => {
    const resp = makeResp(
      [{ tool: 'run_cmd', status: 'denied', error: '命令未授权' }],
      'command',
    );
    expect(summarizeResults(resp)).toContain('denied');
  });

  it('handles empty results', () => {
    const resp = makeResp([], 'chat');
    expect(summarizeResults(resp)).toContain('无执行步骤');
  });
});
