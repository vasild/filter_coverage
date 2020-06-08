#!/usr/bin/env bash

# Filter the LCOV report and generate a mini-report to link to modified and not covered
# lines - modified_and_not_covered.html.

set -e

: ${MODIFIED_JSON_FILE:=${1}}
: ${COVERAGE_LCOV_HTML_DIR:=${2}}

MODIFIED_AND_NOT_COVERED_HTML="${COVERAGE_LCOV_HTML_DIR}/modified_and_not_covered.html"

rm -f "${MODIFIED_AND_NOT_COVERED_HTML}"

cat > "${MODIFIED_AND_NOT_COVERED_HTML}" <<HTML_BEGIN
<!doctype html>
<html lang="en">
<head>
<title>Modified and not covered</title>
</head>
<body>
HTML_BEGIN

for f in $(find "${COVERAGE_LCOV_HTML_DIR}" -name "*.gcov.html" |sort) ; do
    $(dirname "${0}")/filter_report.py \
        -lcov \
        "${MODIFIED_JSON_FILE}" \
        "${f}" \
        >> "${MODIFIED_AND_NOT_COVERED_HTML}"
done

cat >> "${MODIFIED_AND_NOT_COVERED_HTML}" <<HTML_END
</body>
</html>
HTML_END
