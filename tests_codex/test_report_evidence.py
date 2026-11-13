"""Report claims remain bounded by supplied observations and source context."""

import importlib.util
from pathlib import Path

import pytest


SCRIPTS = Path(__file__).resolve().parents[1] / 'plugins/codex-seo/scripts'
SPEC = importlib.util.spec_from_file_location('codex_report_evidence', SCRIPTS / 'google_report.py')
report = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(report)


def render_html(tmp_path, data):
    result = report.generate_report('full', data, 'fixture.example', tmp_path, output_format='html')
    assert result['error'] is None
    return Path(result['files'][0]).read_text(encoding='utf-8')


def footer(html):
    marker = 'DATA SOURCES & METHODOLOGY'
    assert marker in html
    return html.split(marker, 1)[1]


def test_unmeasured_audit_keeps_unknowns_and_does_not_invent_success_or_roadmap(tmp_path):
    data = {'summary': {'health_score': None, 'business_type': 'Synthetic fixture',
                        'top_findings': ['Controlled fixture only; no live site audit.']},
            'categories': [{'name': 'Fixture inspection', 'score': None, 'findings': []}]}
    html = render_html(tmp_path, data)
    assert 'Evidence Coverage' in html
    assert 'overall SEO health score' in html or 'Overall SEO health score' in html
    assert 'Unknown / not supplied' in html
    assert 'Assessment status remains unknown' in html
    assert 'full-site coverage is unknown' in html
    assert 'No automatic recommendations could be derived' in html
    assert 'No critical issues detected' not in html
    assert 'Implementation Roadmap' not in html
    assert 'Maintain current performance' not in html
    assert 'Week 1:' not in html
    assert 'comprehensive' not in html.lower()
    assert 'Powered by Google APIs' not in html
    sources = footer(html)
    assert 'Supplied audit data' in sources
    for absent in ('PageSpeed Insights API', 'Chrome UX Report', 'CrUX History API',
                   'Google Search Console', 'URL Inspection API'):
        assert absent not in sources


def test_explicit_scope_and_source_context_are_preserved_and_escaped(tmp_path):
    data = {'summary': {'health_score': None}, 'coverage': 'One supplied page snapshot',
            'sources': [{'name': 'Browser snapshot <untrusted>', 'url': 'https://example.test/page',
                         'collected_at': '2026-11-13', 'scope': 'One page'}],
            'evidence_gaps': ['JavaScript rendering was not inspected']}
    html = render_html(tmp_path, data)
    assert 'One supplied page snapshot' in html
    assert 'JavaScript rendering was not inspected' in html
    assert 'Browser snapshot &lt;untrusted&gt;' in footer(html)
    assert 'https://example.test/page' in footer(html)
    assert '2026-11-13' in footer(html)
    assert '<untrusted>' not in html


def test_null_measurement_fields_render_unknown_instead_of_zero_or_a_passing_chart(tmp_path):
    data = {'psi': {'lighthouse_scores': {'performance': None}},
            'gsc': {'totals': {'clicks': None, 'impressions': None, 'ctr': None}},
            'inspection': {'summary': {'pass': None, 'fail': None}, 'total': None}}
    html = render_html(tmp_path, data)
    assert 'Unknown' in html
    assert 'No critical issues detected' not in html
    assert 'Implementation Roadmap' not in html
    assert '0/100' not in html
    assert '>None<' not in html
    assert 'Supplied Lighthouse' not in footer(html)
    assert 'Supplied Google Search Console' not in footer(html)
    assert 'Supplied URL inspection' not in footer(html)


def test_error_only_google_payloads_do_not_become_claimed_measurement_sources(tmp_path):
    data = {'summary': {'health_score': None}, 'psi': {'error': 'No lab measurements available'},
            'crux': {'error': 'No field data available'}, 'gsc': {'error': 'No account export supplied'},
            'inspection': {'error': 'No URLs inspected'}}
    html = render_html(tmp_path, data)
    assert 'No lab measurements available' in html
    assert 'No account export supplied' in html
    assert 'No URLs inspected' in html
    assert 'No critical issues detected' not in html
    assert 'Implementation Roadmap' not in html
    assert 'Supplied Lighthouse' not in footer(html)
    assert 'Supplied CrUX' not in footer(html)
    assert 'Supplied Google Search Console' not in footer(html)
    assert 'Supplied URL inspection' not in footer(html)


def test_measured_google_data_keeps_only_its_actual_source_rows():
    data = {'psi': {'lighthouse_scores': {'performance': 42}},
            'gsc': {'totals': {'clicks': 19, 'impressions': 1000},
                    'property': 'https://example.test/',
                    'date_range': {'start': '2026-10-01', 'end': '2026-10-31'}}}
    html = report._build_methodology_footer('example.test', '2026-11-13', data=data, report_type='full')
    assert 'Supplied Lighthouse / PageSpeed data' in html
    assert 'Supplied Google Search Console data' in html
    assert '2026-10-01' in html
    assert 'https://example.test/' in html
    assert 'Supplied CrUX' not in html
    assert 'Supplied URL inspection' not in html
    assert 'Real-time' not in html
    assert 'Daily ~04:00' not in html


def test_observed_measurements_keep_recommendations_and_supported_roadmap():
    data = {'psi': {'lighthouse_scores': {'performance': 42, 'accessibility': 70},
                    'opportunities': [{'title': 'Compress observed oversized image', 'savings_ms': 400}]}}
    html = report._build_recommendations(data)
    assert 'Improve Lighthouse Performance Score' in html
    assert 'Improve Accessibility Score' in html
    assert 'Compress observed oversized image' in html
    assert 'Implementation Roadmap' in html
    assert 'Maintain current performance' not in html
    assert 'Review and improve content depth for underperforming pages' not in html
    assert 'Verify all monitoring dashboards are active' not in html


def test_full_google_payload_keeps_each_supplied_source_and_partial_error_context():
    data = {'psi': {'lighthouse_scores': {'performance': 42}, 'error': 'Desktop measurement unavailable'},
            'crux': {'metrics': {'largest_contentful_paint': {'p75': 2800}},
                     'collection_period': {'first': '2026-10-01', 'last': '2026-10-28'}},
            'crux_history': {'trends': {'largest_contentful_paint': {'direction': 'improving'}}},
            'gsc': {'totals': {'clicks': 19, 'impressions': 1000}},
            'inspection': {'summary': {'pass': 1, 'fail': 0}, 'total': 1}}
    html = report._build_methodology_footer('example.test', '2026-11-13', data=data, report_type='full')
    for source in ('Lighthouse / PageSpeed', 'CrUX field data', 'CrUX history',
                   'Google Search Console', 'URL inspection'):
        assert source in html
    assert '2026-10-28' in html
    assert 'Desktop measurement unavailable' in html


def test_supplied_action_plan_is_retained_even_when_measurements_are_partial(tmp_path):
    data = {'summary': {'health_score': None}, 'action_plan': {'phases': [
        {'name': 'Collect missing evidence', 'timeframe': 'Owner supplied',
         'items': ['Inspect the selected page and obtain a Search Console export']} ]}}
    html = render_html(tmp_path, data)
    assert 'Collect missing evidence' in html
    assert 'Owner supplied' in html
    assert 'Inspect the selected page' in html
    assert 'No critical issues detected' not in html
    assert 'Maintain current performance' not in html


def test_numeric_zero_is_supplied_measurement_and_is_not_treated_as_missing():
    data = {'psi': {'lighthouse_scores': {'performance': 0}},
            'gsc': {'totals': {'clicks': 0, 'impressions': 0}}}
    sources = report._supplied_report_sources(data, 'full')
    assert any('Lighthouse' in row['name'] for row in sources)
    assert any('Search Console' in row['name'] for row in sources)
    summary = report._build_executive_summary('example.test', '2026-11-13', data, 'full')
    assert '0/100' in summary
    assert 'Total Clicks' in summary


@pytest.mark.parametrize('report_type,payload,expected', [
    ('cwv-audit', {'lighthouse_scores': {'performance': 90}}, 'Lighthouse'),
    ('gsc-performance', {'totals': {'clicks': 5, 'impressions': 100}}, 'Search Console'),
    ('indexation', {'summary': {'pass': 1, 'fail': 0}, 'total': 1}, 'URL inspection'),
])
def test_standalone_google_report_shapes_preserve_supplied_source_context(report_type, payload, expected):
    rows = report._supplied_report_sources(payload, report_type)
    assert any(expected in row['name'] for row in rows)
