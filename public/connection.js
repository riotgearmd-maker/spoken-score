fetch('/api/voices').then(async response => {
  const data = await response.json();
  const status = document.querySelector('#connection-status');
  status.textContent = response.ok
    ? (data.connected
      ? `Connected · ${data.model} · ${data.voices.length} approved voice.`
      : data.message)
    : (data.error || 'Could not check the connection.');
}).catch(() => {
  document.querySelector('#connection-status').textContent = 'Connection check failed. Please reload.';
});
