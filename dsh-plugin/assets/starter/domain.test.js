import test from 'node:test';
import assert from 'node:assert/strict';
import { inspectEntity } from './domain.js';

test('example and missing entities remain distinguishable', () => {
  assert.equal(inspectEntity('example:equipment-1').status, 'example');
  assert.equal(inspectEntity('absent').status, 'not-found');
  assert.throws(() => inspectEntity(' '), /non-empty/);
});

test('callers cannot mutate the next result', () => {
  inspectEntity('example:equipment-1').label = 'changed';
  assert.equal(inspectEntity('example:equipment-1').label, 'Example equipment');
});
