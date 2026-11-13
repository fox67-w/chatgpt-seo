"""Exercise local HTTP, public rendering, offline JavaScript and report output."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PLUGIN = BASE / 'plugins/codex-seo'
DEFAULT_PUBLIC_URL = 'https://quotes.toscrape.com/js/'

# This proves real Chromium executes JavaScript without allowing any network
# request. Public URL rendering is checked separately through the guarded tool.
BROWSER_FIXTURE = r'''
import json
from playwright.sync_api import sync_playwright

requests = []
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(offline=True, service_workers='block')
    def refuse_network(route):
        requests.append(route.request.url)
        route.abort()
    context.route('**/*', refuse_network)
    page = context.new_page()
    page.set_content('<!doctype html><html><body><div id="app"></div>'
                     '<script>document.getElementById("app").textContent='
                     '["Rendered","fixture"].join(" ");</script></body></html>',
                     wait_until='domcontentloaded')
    value = page.locator('#app').inner_text()
    payload = {'engine': 'playwright-chromium', 'browser_version': browser.version,
               'javascript_executed': value == 'Rendered fixture', 'observed_text': value,
               'network_mode': 'offline', 'intercepted_network_requests': requests}
    browser.close()
print(json.dumps(payload))
raise SystemExit(0 if payload['javascript_executed'] and not requests else 1)
'''


class FixtureHandler(BaseHTTPRequestHandler):
    revision = 1

    def log_message(self, *_):
        pass

    def do_GET(self):
        origin = 'http://127.0.0.1:' + str(self.server.server_port)
        if self.path == '/robots.txt':
            content = 'User-agent: *\nAllow: /\nSitemap: ' + origin + '/sitemap.xml\n'
            mime = 'text/plain'
        elif self.path == '/sitemap.xml':
            content = ('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                       '<url><loc>' + origin + '/</loc></url><url><loc>' + origin + '/about</loc></url></urlset>')
            mime = 'application/xml'
        elif self.path in ('/', '/about'):
            content = ('<!doctype html><html><head><title>Fixture revision ' + str(self.revision) +
                       '</title><meta name="description" content="Controlled SEO test fixture.">'
                       '<link rel="canonical" href="' + origin + self.path + '"></head>'
                       '<body><h1>Controlled SEO fixture</h1><div id="app"></div>'
                       '<a href="/about">About</a><script>'
                       'document.getElementById("app").textContent=["Rendered","fixture"].join(" ");'
                       '</script></body></html>')
            mime = 'text/html'
        else:
            self.send_response(404)
            self.end_headers()
            return
        data = content.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', mime + '; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def capture(env, output, name, command):
    try:
        result = subprocess.run(command, env=env, capture_output=True, text=True,
                                encoding='utf-8', errors='replace', timeout=120)
    except subprocess.TimeoutExpired as error:
        def decoded(value):
            return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else value or ''
        result = subprocess.CompletedProcess(command, 124, decoded(error.stdout),
                                              decoded(error.stderr) + '\nSmoke command timed out after 120 seconds.')
    except OSError as error:
        result = subprocess.CompletedProcess(command, 127, '', str(error))
    (output / (name + '.stdout')).write_text(result.stdout, encoding='utf-8')
    (output / (name + '.stderr')).write_text(result.stderr, encoding='utf-8')
    try:
        payload = json.loads(result.stdout)
    except ValueError:
        payload = None
    if not isinstance(payload, dict):
        payload = None
    return result, payload


def run_tool(env, output, name, arguments):
    command = [sys.executable, str(PLUGIN / 'scripts/codex_seo.py'), *arguments]
    return capture(env, output, name, command)


def run_browser_fixture(env, output):
    runtime = Path(env['CODEX_SEO_DATA_DIR'])
    python = runtime / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    browser_env = {**env, 'PLAYWRIGHT_BROWSERS_PATH': str(runtime / 'ms-playwright')}
    browser_env.pop('CODEX_SEO_LOCAL_TARGETS', None)
    browser_env.pop('CLAUDE_SEO_LOCAL_TARGETS', None)
    return capture(browser_env, output, 'javascript-offline', [str(python), '-c', BROWSER_FIXTURE])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=BASE / 'dist/verification/runtime-smoke')
    parser.add_argument('--public-url', default=DEFAULT_PUBLIC_URL,
                        help='Public page to render with the unchanged URL guard; no local targets')
    args = parser.parse_args()
    output = args.output.resolve()
    output.relative_to(BASE)
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    env = os.environ.copy()
    env.update({'PYTHONUTF8': '1', 'CODEX_SEO_DATA_DIR': str(BASE / '.runtime/codex-seo'),
                'CODEX_SEO_LOCAL_TARGETS': '127.0.0.1:' + str(server.server_port)})
    checks = []
    FixtureHandler.revision = 1
    try:
        result, payload = run_tool(env, output, 'doctor', ['doctor', '--json'])
        checks.append({'name': 'managed_runtime_and_chromium',
                       'passed': result.returncode == 0 and bool(payload and payload.get('ready') and payload.get('browser_ready'))})
        result, payload = run_tool(env, output, 'fetch', ['run', 'fetch_page.py', origin, '--json'])
        checks.append({'name': 'real_http_fetch', 'passed': result.returncode == 0 and bool(
            payload and payload.get('status_code') == 200 and not payload.get('error'))})
        public_env = dict(env)
        public_env.pop('CODEX_SEO_LOCAL_TARGETS', None)
        public_env.pop('CLAUDE_SEO_LOCAL_TARGETS', None)
        rendered = output / 'rendered-public.html'
        result, payload = run_tool(public_env, output, 'render-public',
                                  ['run', 'render_page.py', args.public_url, '--mode', 'always',
                                   '--json', '--output', str(rendered)])
        public_ok = (result.returncode == 0 and bool(payload) and not payload.get('error')
                     and payload.get('render_engine') == 'playwright-chromium'
                     and payload.get('mode_used') == 'rendered' and payload.get('output_written')
                     and 200 <= (payload.get('status_code') or 0) < 400 and rendered.is_file())
        checks.append({'name': 'real_public_page_render', 'passed': bool(public_ok),
                       'tested_url': args.public_url,
                       'engine': payload.get('render_engine') if payload else None,
                       'status_code': payload.get('status_code') if payload else None,
                       'javascript_gap': payload.get('js_gap') if payload else None,
                       'error': payload.get('error') if payload else result.stderr[-500:]})
        result, payload = run_browser_fixture(env, output)
        checks.append({'name': 'real_chromium_javascript_execution',
                       'passed': result.returncode == 0 and bool(payload and payload.get('javascript_executed')),
                       'fixture': 'synthetic inline JavaScript; browser network is offline and intercepted',
                       'evidence': payload, 'error': result.stderr[-500:] if result.returncode else None})
        result, payload = run_tool(env, output, 'sitemap', ['run', 'sitemap_discovery.py', origin, '--expand', '--json'])
        totals = (payload or {}).get('expanded', {}).get('totals', {})
        checks.append({'name': 'real_sitemap_discovery', 'passed': result.returncode == 0 and
                       totals.get('unique_urls') == 2})
        result, payload = run_tool(env, output, 'baseline', ['run', 'drift_baseline.py', origin, '--skip-cwv'])
        checks.append({'name': 'persist_drift_baseline', 'passed': result.returncode == 0 and bool(
            payload and not payload.get('error') and payload.get('baseline_id')
            and payload.get('summary', {}).get('title') == 'Fixture revision 1')})
        FixtureHandler.revision = 2
        result, payload = run_tool(env, output, 'compare', ['run', 'drift_compare.py', origin, '--skip-cwv'])
        findings = (payload or {}).get('triggered_findings', [])
        changed_title = any(finding.get('rule') == 'title_changed'
                            and finding.get('old_value') == 'Fixture revision 1'
                            and finding.get('new_value') == 'Fixture revision 2' for finding in findings)
        checks.append({'name': 'compare_drift_snapshot', 'passed': result.returncode == 0 and bool(
            payload and not payload.get('error') and changed_title)})
        data = {'summary': {'health_score': None, 'business_type': 'Synthetic fixture',
                            'top_findings': ['Controlled fixture only; no live site audit.']},
                'categories': [{'name': 'Fixture inspection', 'score': None, 'findings': []}]}
        report_data = output / 'report-data.json'
        report_data.write_text(json.dumps(data), encoding='utf-8')
        for format_name in ('html', 'xlsx', 'pdf'):
            result, payload = run_tool(env, output, 'report-' + format_name,
                                      ['run', 'google_report.py', '--type', 'full', '--data', str(report_data),
                                       '--domain', 'fixture.example', '--format', format_name,
                                       '--output-dir', str(output / 'reports'), '--json'])
            files = payload.get('files', []) if payload else []
            checks.append({'name': 'generate_' + format_name,
                           'passed': result.returncode == 0 and bool(files) and not payload.get('error') and
                           all(Path(file).is_file() and Path(file).stat().st_size > 0 for file in files),
                           'error': payload.get('error') if payload else result.stderr[-500:]})
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    report = {'valid': all(check['passed'] for check in checks),
              'fixtures': {'raw_http_sitemap_and_drift': 'controlled local HTTP site',
                           'public_renderer': args.public_url,
                           'javascript_execution': 'synthetic document in real offline Chromium'},
              'local_browser_navigation': 'intentionally unsupported by the preserved URL policy',
              'checks': checks, 'provider_accounts_used': False}
    (output / 'summary.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['valid'] else 1)


if __name__ == '__main__':
    main()
