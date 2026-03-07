# TD Review: schema-evolution-advisor

## Bug Fixes Applied
- [x] **cli.py**: Added `argv` parameter to `main()`. Previously hardcoded to `sys.argv` via `parse_args()`, making unit testing impossible without monkeypatching.

## Test Coverage Gaps
- [ ] **test_cli.py**: No CLI integration tests. Now possible with argv param. Add tests for: main() with valid file, valid directory, non-existent path, non-migration file, --format json, --exit-code flag.
- [ ] **test_report.py**: No report rendering tests. Add tests for: render_table output, render_json output, empty findings.

## Notes
- parser.py: AST-based migration parsing is solid. Handles unknown operations gracefully.
- analyzer.py: All classifiers handle missing args with "unknown" fallback. Good.
