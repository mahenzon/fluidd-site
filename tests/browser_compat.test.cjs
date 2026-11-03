const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

function context(overrides = {}) {
  return vm.createContext({
    AbortController,
    AbortSignal: { any: undefined },
    ...overrides,
  });
}

function install(target) {
  const source = fs.readFileSync(path.join(__dirname, '../scripts/browser_compat.js'), 'utf8');
  vm.runInContext(source, target);
  return target.AbortSignal.any;
}

test('the reported call fails without the API and succeeds with the shim', () => {
  const target = context({ o: new AbortController().signal, i: undefined });
  const expression = 'AbortSignal.any([o,i].filter(Boolean))';
  assert.throws(() => vm.runInContext(expression, target), /AbortSignal.any is not a function/);
  install(target);
  const signal = vm.runInContext(expression, target);
  assert.ok(signal instanceof AbortSignal);
  assert.equal(signal.aborted, false);
});

for (const sourceIndex of [0, 1]) {
  test(`source ${sourceIndex} cancels the request and preserves its first reason`, () => {
    const any = install(context());
    const controllers = [new AbortController(), new AbortController()];
    const combined = any(controllers.map(controller => controller.signal));
    const reason = new Error('request cancelled');
    let abortEvents = 0;
    combined.addEventListener('abort', () => abortEvents++);
    controllers[sourceIndex].abort(reason);
    controllers[1 - sourceIndex].abort(new Error('later cancellation'));
    assert.equal(combined.aborted, true);
    assert.equal(combined.reason, reason);
    assert.equal(abortEvents, 1);
  });
}

test('the first already aborted source wins in input order', () => {
  const any = install(context());
  const first = AbortSignal.abort('first in input');
  const second = AbortSignal.abort('second in input');
  const pending = new AbortController().signal;
  const combined = any([pending, first, second]);
  assert.equal(combined.aborted, true);
  assert.equal(combined.reason, 'first in input');
});

test('empty input returns a genuine un-aborted signal', () => {
  const any = install(context());
  const signal = any([]);
  assert.ok(signal instanceof AbortSignal);
  assert.equal(signal.aborted, false);
});

test('a native implementation is preserved', () => {
  const nativeAny = AbortSignal.any;
  const target = context({ AbortSignal: { any: nativeAny } });
  assert.equal(install(target), nativeAny);
});

test('browsers without abort primitives are left alone', () => {
  for (const overrides of [{ AbortSignal: undefined }, { AbortController: undefined }]) {
    const target = context(overrides);
    const source = fs.readFileSync(path.join(__dirname, '../scripts/browser_compat.js'), 'utf8');
    assert.doesNotThrow(() => vm.runInContext(source, target));
    assert.equal(target.AbortSignal?.any, undefined);
  }
});

test('all source listeners are removed after cancellation', () => {
  const any = install(context());
  const controllers = [new AbortController(), new AbortController()];
  const listeners = new Set();
  for (const { signal } of controllers) {
    const add = signal.addEventListener.bind(signal);
    const remove = signal.removeEventListener.bind(signal);
    signal.addEventListener = (event, listener, options) => {
      assert.equal(event, 'abort');
      assert.equal(options.once, true);
      listeners.add(signal);
      add(event, listener, options);
    };
    signal.removeEventListener = (event, listener) => {
      listeners.delete(signal);
      remove(event, listener);
    };
  }
  any(controllers.map(controller => controller.signal));
  assert.equal(listeners.size, 2);
  controllers[0].abort();
  assert.equal(listeners.size, 0);
});

test('invalid inputs fail before listeners are attached', () => {
  const any = install(context());
  const signal = new AbortController().signal;
  signal.addEventListener = () => assert.fail('invalid input must not attach listeners');
  assert.throws(() => any([signal, null]), /AbortSignal/);
  assert.throws(() => any(null), { name: 'TypeError' });
});
