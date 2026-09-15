#!/usr/bin/env node
import { chmod, mkdir } from 'node:fs/promises';
import path from 'node:path';
import {
  copyFileSafe,
  copyTemplate,
  detectPackageManager,
  detectProject,
  exists,
  initScriptFromCommands,
  listFiles,
  parseArgs,
  SKILL_ROOT,
  verificationCommands,
  writeText
} from './lib/harness-utils.mjs';

const args = parseArgs(process.argv.slice(2));

if (args.help) {
  console.log(`Usage: node scripts/create-harness.mjs [--target DIR] [--agent-file AGENTS.md|CLAUDE.md] [--package-manager npm|pnpm|yarn|bun] [--with-scenario NAME[,NAME...]] [--force]

Creates a minimal production harness:
  AGENTS.md or CLAUDE.md
  feature_list.json
  progress.md
  session-handoff.md
  init.sh

--with-scenario NAME copies scenarios/NAME (a self-contained landing scenario)
into the target, preserving the scenarios/NAME/ structure. Comma-separate for
multiple scenarios.

Existing files are skipped unless --force is set.`);
  process.exit(0);
}

const target = path.resolve(args.target || args._[0] || process.cwd());
const agentFile = args.agentFile || 'AGENTS.md';
const force = Boolean(args.force);
const project = await detectProject(target);
project.packageManager = detectPackageManager(target, args.packageManager);
const commands = args.commands
  ? String(args.commands).split(',').map((command) => command.trim()).filter(Boolean)
  : verificationCommands(project, args.packageManager);

await mkdir(target, { recursive: true });

const replacements = {
  AGENT_FILE_NAME: agentFile,
  PROJECT_PURPOSE: project.stack === 'generic'
    ? 'Project harness for reliable agent-assisted development.'
    : `Project harness for reliable agent-assisted development in a ${project.stack} codebase.`,
  VERIFICATION_COMMANDS: commands.map((command) => `- \`${command}\``).join('\n'),
  PRIMARY_VERIFICATION_COMMAND: './init.sh'
};

const results = [];
results.push(await copyTemplate('agents.md', path.join(target, agentFile), replacements, { force }));
results.push(await copyTemplate('feature-list.json', path.join(target, 'feature_list.json'), {}, { force }));
results.push(await copyTemplate('progress.md', path.join(target, 'progress.md'), {}, { force }));
results.push(await copyTemplate('session-handoff.md', path.join(target, 'session-handoff.md'), {}, { force }));

const initPath = path.join(target, 'init.sh');
if (force || !await exists(initPath)) {
  await writeText(initPath, initScriptFromCommands(commands));
  await chmod(initPath, 0o755);
  results.push({ path: initPath, status: 'written' });
} else {
  results.push({ path: initPath, status: 'skipped', reason: 'exists' });
}

// --- 场景复制：--with-scenario <name[,name...]> ---
const scenarioNames = args.withScenario
  ? String(args.withScenario).split(',').map((name) => name.trim()).filter(Boolean)
  : [];
for (const name of scenarioNames) {
  const scenarioSrc = path.join(SKILL_ROOT, 'scenarios', name);
  const scenarioFiles = await listFiles(scenarioSrc);
  if (scenarioFiles.length === 0) {
    console.error(`Warning: scenario "${name}" not found at ${scenarioSrc}`);
    continue;
  }
  for (const rel of scenarioFiles) {
    const source = path.join(scenarioSrc, rel);
    const dest = path.join(target, 'scenarios', name, rel);
    results.push(await copyFileSafe(source, dest, { force }));
  }
}

console.log(`Created harness for ${target}`);
console.log(`Detected stack: ${project.stack}`);
console.log(`Verification commands:`);
for (const command of commands) {
  console.log(`  - ${command}`);
}
if (scenarioNames.length > 0) {
  console.log(`Scenarios copied: ${scenarioNames.join(', ')}`);
}
console.log('');
for (const result of results) {
  console.log(`${result.status.toUpperCase()} ${path.relative(target, result.path)}${result.reason ? ` (${result.reason})` : ''}`);
}
