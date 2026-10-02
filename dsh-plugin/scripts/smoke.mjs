#!/usr/bin/env node
/** Exercise a generated bundle against built DSH Cordis/tools; no profile mutation. */
import assert from 'node:assert/strict';
import { cp, mkdtemp, mkdir, readFile, rm, symlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import vm from 'node:vm';

const args = process.argv.slice(2);
const value = (flag) => {
  const index = args.indexOf(flag);
  if (index < 0 || !args[index + 1]) throw new Error(`Required: ${flag}`);
  return resolve(args[index + 1]);
};
const dsh = value('--dsh');
const source = value('--plugin');
const temp = await mkdtemp(join(tmpdir(), 'dsh-plugin-smoke-'));
let ctx;
try {
  const plugin = join(temp, 'plugin');
  await cp(source, plugin, { recursive: true, filter: (path) => !path.split('/').includes('node_modules') });
  await mkdir(join(plugin, 'node_modules/@deepseek-ai'), { recursive: true });
  await symlink(join(dsh, 'packages/core/tools'), join(plugin, 'node_modules/@deepseek-ai/dsh-tools'), 'dir');
  const { Context } = await import(pathToFileURL(join(dsh, 'vendor/cordis/lib/index.js')));
  const manifest = JSON.parse(await readFile(join(plugin, 'package.json'), 'utf8'));
  const host = await import(pathToFileURL(join(plugin, 'index.js')));
  ctx = new Context();
  const checks = [];
  if (host.inject?.includes('tools')) {
    const { default: SystemPrompt } = await import(pathToFileURL(join(dsh, 'packages/core/system-prompt/lib/index.js')));
    const { default: Tools } = await import(pathToFileURL(join(dsh, 'packages/core/tools/lib/index.js')));
    await ctx.plugin(SystemPrompt);
    await ctx.plugin(Tools);
    const baseline = ctx.tools.schemas().length;
    const fork = await ctx.plugin(host);
    const schema = ctx.tools.schemas().find(row => row.name.endsWith('_inspect'));
    assert.ok(schema, 'generated inspection tool is registered');
    const call = (id, signal = new AbortController().signal) => ctx.tools.execute({
      name: schema.name, callId: 'skill-smoke', arguments: { id }, signal,
    });
    const example = await call('example:equipment-1');
    assert.equal(example.isError, false);
    assert.ok(example.content.some(block => block.type === 'text' && block.text.includes('example:equipment-1')));
    const invalid = await call('');
    assert.equal(invalid.isError, true);
    const cancelled = await call('example:equipment-1', AbortSignal.abort());
    assert.equal(cancelled.isError, true);
    await fork.dispose();
    assert.equal(ctx.tools.schemas().length, baseline, 'unload removes tool');
    const again = await ctx.plugin(host);
    assert.equal(ctx.tools.schemas().length, baseline + 1, 'reload registers once');
    await again.dispose();
    checks.push('real Cordis + Tools: execution, invalid input, cancellation, unload, reload');
  } else {
    const fork = await ctx.plugin(host);
    await fork.dispose();
    checks.push('real Cordis: browser-only Host apply/dispose');
  }
  if (manifest.dsh.client) {
    // Protocol-level Client check only. Real browser/slot layout is a separate gate.
    let registration;
    const sandbox = { window: { __ModuleLoader__: { load: (entry) => { registration = entry; } } } };
    vm.runInNewContext(await readFile(join(plugin, 'client.js'), 'utf8'), sandbox);
    assert.equal(registration.id, manifest.name);
    const React = { createElement: (type, props, ...children) => ({ type, props, children }) };
    const client = registration.factory(name => {
      assert.equal(name, 'react', 'only shared React is imported');
      return React;
    });
    const dicts = new Map();
    const entries = new Map();
    await ctx.plugin({ apply(owner) {
      owner.provide('locale', { register(namespace, copy) {
        dicts.set(namespace, copy);
        return () => dicts.delete(namespace);
      } });
      owner.provide('slots', {
        inject(_key, callback) { return callback(); },
        register(options, component) {
          entries.set(options.id, { options, component });
          return () => entries.delete(options.id);
        },
      });
    } });
    const mounted = await ctx.plugin(client);
    assert.equal(entries.size, 1);
    const entry = [...entries.values()][0];
    for (const language of ['zh', 'en']) {
      const dictionary = dicts.get(entry.options.locale)[language];
      assert.equal(entry.component({ subject: { kind: 'item', id: 'other' } }), null);
      const tree = entry.component({ subject: { kind: 'bundle', pkg: { name: manifest.name } }, t: key => {
        assert.equal(typeof dictionary[key], 'string', `missing translation ${language}:${key}`);
        return dictionary[key];
      } });
      assert.equal(tree.type, 'section');
    }
    await mounted.dispose();
    assert.equal(dicts.size, 0);
    checks.push('Client factory/id, shared React, translated render tree, dictionary cleanup (slot adapter, not browser)');
  }
  console.log(JSON.stringify({ package: manifest.name, checks, limitation: 'Does not prove installation, real UI layout, or other DSH versions.' }, null, 2));
} finally {
  if (ctx) await ctx.fiber.dispose();
  await rm(temp, { recursive: true, force: true });
}
