"""Standard-library launcher tests; no real browser is opened."""
import importlib.util
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch, MagicMock
import urllib.request

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('booth_start', HERE/'start.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class LauncherTests(unittest.TestCase):
    def test_auto_browser_loopback_and_cleanup(self):
        server = MagicMock(server_port=8765)
        server.serve_forever.side_effect = KeyboardInterrupt
        def immediate_timer(delay, callback):
            timer = MagicMock()
            timer.start.side_effect = callback
            return timer
        with patch.object(launcher, 'ThreadingHTTPServer', return_value=server) as factory, patch.object(launcher.webbrowser, 'open') as opened, patch.object(launcher.threading, 'Timer', side_effect=immediate_timer), patch('sys.argv', ['start.py']):
            launcher.main()
            self.assertEqual(factory.call_args.args[0], ('127.0.0.1',8765))
            opened.assert_called_once_with('http://127.0.0.1:8765/')
            server.server_close.assert_called_once()

    def test_executable_command_fallback_from_other_directory(self):
        self.assertTrue(os.access(HERE/'Run.command', os.X_OK))
        env = dict(os.environ, PATH='/usr/bin:/bin')
        process = subprocess.Popen([str(HERE/'Run.command'), '--no-browser', '--port', '18766'], cwd=tempfile.gettempdir(), env=env, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(100):
                try:
                    with urllib.request.urlopen('http://127.0.0.1:18766/', timeout=1) as response:
                        self.assertIn(b'ASCamera - FATQ', response.read())
                        break
                except OSError:
                    if process.poll() is not None:
                        self.fail('Run.command exited before serving')
                    time.sleep(.1)
            else:
                self.fail('Launcher did not become ready')
        finally:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=5)


if __name__ == '__main__':
    unittest.main()
