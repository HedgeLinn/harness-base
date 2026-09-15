export interface Intent {
  name: string;
  confidence: number;
  matched: string[];
}

export interface PlanStep {
  tool: string;
  args: Record<string, unknown>;
  note: string;
}

export interface Plan {
  intent: Intent;
  source: string;
  steps: PlanStep[];
}

export interface StepResult {
  tool: string;
  status: 'ok' | 'denied' | 'error';
  output?: unknown;
  error?: string;
}

export interface TraceStep {
  kind: string;
  label: string;
  detail: Record<string, unknown>;
  status: string;
  ts: number;
}

export interface Trace {
  id: string;
  steps: TraceStep[];
}

export interface ChatResponse {
  message: string;
  intent: Intent;
  plan: Plan;
  results: StepResult[];
  trace: Trace;
}

export async function sendChat(message: string, useLlm = true): Promise<ChatResponse> {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, use_llm: useLlm }),
  });
  if (!res.ok) {
    throw new Error(`请求失败: ${res.status}`);
  }
  return (await res.json()) as ChatResponse;
}
