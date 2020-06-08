Filter a code coverage report, highlighting the lines that were modified by a set of commits
============================================================================================

```bash
# Generate LCOV HTML report as usual and put it in e.g. /tmp/lcov_html

./get_modified_lines.sh /path/to/source "^(src/test/|test/functional/)" > /tmp/modified_lines.json

./filter_lcov_report.sh /tmp/modified_lines.json /tmp/lcov_html
```
