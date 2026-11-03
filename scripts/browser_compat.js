
(function () {
  if (typeof AbortSignal === 'undefined' || typeof AbortController === 'undefined'
      || typeof AbortSignal.any === 'function') return;

  // Safari before 17.4 needs this for Fluidd's request and timeout signals.
  AbortSignal.any = function any(signals) {
    const sources = [...signals];
    const controller = new AbortController();
    for (const signal of sources) {
      if (!signal || typeof signal.aborted !== 'boolean'
          || typeof signal.addEventListener !== 'function'
          || typeof signal.removeEventListener !== 'function') {
        throw new TypeError('Expected an AbortSignal');
      }
    }
    for (const signal of sources) {
      if (signal.aborted) {
        controller.abort(signal.reason);
        return controller.signal;
      }
    }
    function abort(event) {
      controller.abort(event.target.reason);
      for (const signal of sources) signal.removeEventListener('abort', abort);
    }
    // shortcut: listeners live until abort; revisit if Fluidd adds long-lived signals without timeouts.
    for (const signal of sources) signal.addEventListener('abort', abort, { once: true });
    return controller.signal;
  };
}());
