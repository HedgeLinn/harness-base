import { sendChat } from './api';
import {
  renderMessage,
  renderResult,
  renderTrace,
  summarizeResults,
} from './ui/render';

function init(): void {
  const form = document.getElementById('chat-form') as HTMLFormElement | null;
  const input = document.getElementById('chat-input') as HTMLInputElement | null;
  if (!form || !input) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;
    input.value = '';
    renderMessage('user', message);
    try {
      const resp = await sendChat(message);
      renderMessage('agent', summarizeResults(resp));
      renderResult(resp.results);
      renderTrace(resp.trace);
    } catch (err) {
      renderMessage('agent', `错误：${err instanceof Error ? err.message : String(err)}`);
    }
  });
}

init();
