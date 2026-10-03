// Run with native Windows Node: node tests/test_runner_lifecycle_windows.cjs
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawn, spawnSync} = require('node:child_process');
const assert = require('node:assert/strict');
if (process.platform !== 'win32') {
  console.log('SKIP native Windows process tests: requires Windows Node');
  process.exit(0);
}
const root = path.resolve(__dirname, '..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'fable-native-'));
const fixture = path.join(tmp, 'fixture.cjs');
const preload = path.join(tmp, 'preload.cjs');
fs.writeFileSync(preload, `
const cp = require('node:child_process');
const real = cp.spawn;
cp.spawn = (cmd, args, opts) => {
  if (['codex', 'grok', 'git'].includes(cmd) ||
      (cmd === 'taskkill' && process.env.KILL_MODE === 'hang')) {
    return real(process.execPath, [process.env.FIXTURE, cmd, ...args], opts);
  }
  return real(cmd, args, opts);
};
require('node:module').syncBuiltinESMExports();
`);
fs.writeFileSync(fixture, `
const fs = require('node:fs');
const {spawn} = require('node:child_process');
const args = process.argv.slice(3), cmd = process.argv[2];
if (cmd === 'git' || args.includes('--version')) process.exit(0);
if (args.includes('models')) { console.log('* grok-test (default)'); process.exit(0); }
if (cmd === 'taskkill') {
  fs.appendFileSync(process.env.PIDS, process.pid + '\\n');
  setInterval(() => {}, 1000);
} else {
  const child = spawn(process.execPath, ['-e', 'setInterval(() => {}, 1000)'], {
    detached: true, stdio: ['ignore', process.stdout, process.stderr],
    env: {...process.env, NODE_OPTIONS: ''},
  });
  child.unref();
  fs.appendFileSync(process.env.PIDS, process.pid + '\\n' + child.pid + '\\n');
  if (cmd === 'codex') {
    console.log(JSON.stringify({type:'thread.started', thread_id:'native-session'}));
    console.log(JSON.stringify({type:'item.completed', item:{type:'agent_message', text:'x'.repeat(262144)}}));
    console.log(JSON.stringify({type:'turn.completed'}));
  } else {
    console.log(JSON.stringify({type:'text', data:'x'.repeat(262144)}));
    console.log(JSON.stringify({type:'end', stopReason:'done'}));
  }
  if (process.env.KILL_MODE) setInterval(() => {}, 1000);
  else process.stdout.write('', () => process.exit(0));
}
`);
async function run(binary, killMode) {
  const dir = path.join(tmp, binary + '-' + (killMode || 'exit'));
  const scripts = path.join(dir, 'plugin', 'scripts');
  const preambles = path.join(dir, 'plugin', 'skills', 'orchestration');
  const cwd = path.join(dir, 'work');
  for (const folder of [scripts, preambles, cwd]) fs.mkdirSync(folder, {recursive: true});
  const runner = path.join(scripts, 'run-' + binary + '.mjs');
  fs.copyFileSync(path.join(root, 'plugin', 'scripts', 'run-' + binary + '.mjs'), runner);
  fs.copyFileSync(path.join(root, 'plugin', 'scripts', 'routing-profile.mjs'), path.join(scripts, 'routing-profile.mjs'));
  const cell = 'gpt-6-luna[max] › grok-test[high]';
  const table = '| Role | `mainstay` | `crux` | `rescue` |\n|---|---|---|---|\n' +
    ['explorer', 'worker', 'advisor'].map(role => `| ${role} | ${cell} | ${cell} | ${cell} |\n`).join('');
  fs.writeFileSync(path.join(preambles, 'routing-profile.md'), '## Tiers and choosing inside a cell\n\n' + table + '\n## Cursor candidates\n\n' + table);
  fs.writeFileSync(path.join(preambles, 'lane-preamble.md'), 'Fixture preamble');
  fs.writeFileSync(path.join(preambles, 'lane-preamble-report.md'), 'Fixture report preamble');
  const specPath = path.join(cwd, '.fable-advisor', 'pending', 'job.json');
  fs.mkdirSync(path.dirname(specPath), {recursive:true});
  fs.writeFileSync(specPath, JSON.stringify({
    objective:'native pipes', files:[], interfaces:'none', constraints:'none',
    role:'explorer', tier:'mainstay', effort:binary === 'codex' ? 'max' : 'high',
    mode:'report', verification:[], model:binary === 'codex' ? 'gpt-6-luna' : 'grok-test',
    ...(killMode ? {timeout_sec:0.3} : {}),
  }));
  const pids = path.join(dir, 'pids');
  const started = Date.now();
  const child = spawn(process.execPath, [runner, '--spec', specPath, '--cwd', cwd], {
    env:{...process.env, NODE_OPTIONS:'--require=' + preload, FIXTURE:fixture, PIDS:pids,
         KILL_MODE:killMode},
    stdio:['ignore','pipe','pipe'],
  });
  let stdout = '', stderr = '';
  child.stdout.on('data', data => stdout += data);
  child.stderr.on('data', data => stderr += data);
  const timer = setTimeout(() => child.kill(), 8000);
  try {
    const code = await new Promise(resolve => child.once('close', resolve));
    const elapsed = Date.now() - started;
    const receipt = JSON.parse(stdout);
    assert.equal(code, killMode ? 1 : 0, stderr);
    assert.equal(receipt.error_class, killMode ? 'timeout' : 'complete', stderr);
    if (binary === 'codex') assert.equal(receipt.model_used, 'gpt-6-luna');
    assert(elapsed < 6500, elapsed);
    assert.equal(receipt.report, 'x'.repeat(262144));
    const receiptDir = path.join(cwd, '.fable-advisor', 'receipts');
    const receipts = fs.readdirSync(receiptDir);
    assert.equal(receipts.length, 1);
    assert.deepEqual(JSON.parse(fs.readFileSync(path.join(receiptDir, receipts[0]), 'utf8')), receipt);
    assert.equal(fs.existsSync(specPath), Boolean(killMode));
    assert.deepEqual(fs.readdirSync(path.join(cwd, '.fable-advisor', 'running')), []);
    if (killMode !== 'timeout') assert.equal(receipt.end_to_close_ms, null);
    if (killMode) {
      assert.deepEqual(receipt.verification, []);
      if (killMode === 'hang') assert(stderr.includes('taskkill failed'), stderr);
    } else {
      assert.equal(receipt.exit_status, 0);
      const descendant = Number(fs.readFileSync(pids, 'utf8').trim().split(/\s+/)[1]);
      process.kill(descendant, 0);
    }
    console.log('PASS native Windows ' + binary + ' ' + (killMode || 'inherited') +
      ' ' + elapsed + 'ms');
  } finally {
    clearTimeout(timer);
    if (fs.existsSync(pids)) {
      for (const pid of fs.readFileSync(pids, 'utf8').trim().split(/\s+/)) {
        spawnSync('taskkill', ['/pid', pid, '/T', '/F'], {stdio:'ignore'});
      }
    }
  }
}
(async () => {
  try {
    for (const binary of ['codex','grok']) {
      await run(binary, '');
      await run(binary, 'timeout');
      await run(binary, 'hang');
    }
  } finally {
    fs.rmSync(tmp, {recursive:true, force:true});
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
