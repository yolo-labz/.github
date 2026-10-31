// Compatibility entrypoint: rendering belongs on the existing server fleet.
const { spawnSync } = require('node:child_process');
const { join } = require('node:path');
const result = spawnSync('browser-patchright', [join(__dirname, 'render.py')], {
  stdio: 'inherit', env: process.env,
});
if (result.error) console.error(result.error.message);
process.exitCode = result.status ?? 1;
