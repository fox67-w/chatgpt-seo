#!/usr/bin/env python3
"""Check Banana's local environment without connecting a provider or creating files."""

import argparse
import json
import sys
from setup_mcp import readiness


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    parser.parse_args()
    result = readiness()
    result['ready_for_mcp_configuration'] = result['api_key_present'] and result['npx_present']
    result['live_provider_authorization'] = 'unverified'
    print(json.dumps(result, indent=2))
    return 0 if result['ready_for_mcp_configuration'] else 1


if __name__ == '__main__':
    sys.exit(main())
