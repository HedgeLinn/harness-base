import type { ChatResponse, StepResult, Trace } from '../api';

function el(tag: string, className?: string, text?: string): HTMLElement {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

export function renderMessage(role: 'user' | 'agent', text: string): void {
  const container = document.getElementById('messages');
  if (!container) return;
  const bubble = el('div', `bubble ${role}`, text);
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

export function renderResult(results: StepResult[]): void {
  const container = document.getElementById('messages');
  if (!container) return;
  const box = el('div', 'result-box');
  results.forEach((r: StepResult) => {
    const line = el('div', `result-line ${r.status}`);
    const label = `${r.tool} · ${r.status}`;
    line.appendChild(el('span', 'result-label', label));
    if (r.output !== undefined) {
      line.appendChild(el('pre', 'result-output', JSON.stringify(r.output, null, 2)));
    }
    if (r.error) {
      line.appendChild(el('pre', 'result-error', r.error));
    }
    box.appendChild(line);
  });
  container.appendChild(box);
  container.scrollTop = container.scrollHeight;
}

export function renderTrace(trace: Trace): void {
  const container = document.getElementById('trace');
  if (!container) return;
  container.replaceChildren();
  const list = el('ol', 'trace-list');
  trace.steps.forEach((s: import('../api').TraceStep) => {
    const item = el('li', `trace-step ${s.status}`);
    item.appendChild(el('span', 'trace-kind', s.kind));
    item.appendChild(el('span', 'trace-label', s.label));
    list.appendChild(item);
  });
  container.appendChild(list);
}

export function summarizeResults(resp: ChatResponse): string {
  if (resp.results.length === 0) {
    return `[${resp.intent.name}] 无执行步骤`;
  }
  const parts = resp.results.map((r) => {
    if (r.status === 'ok') {
      const out = typeof r.output === 'string' ? r.output : JSON.stringify(r.output);
      return `${r.tool}: ${out}`;
    }
    return `${r.tool}: ${r.status} ${r.error ?? ''}`;
  });
  return parts.join('\n');
}
