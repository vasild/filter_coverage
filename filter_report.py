#!/usr/bin/env python3

# requires https://html5-parser.readthedocs.io/
# pip install --no-binary lxml html5-parser
# FreeBSD: make -C /usr/ports/www/py-html5-parser install clean

import html5_parser
import json
import lxml
import lxml.html.builder as E
import sys
import urllib.parse

dim_style = "opacity: 0.2;"

report_format_lcov = "-lcov"
report_format_llvm = "-llvm"

if len(sys.argv) != 4 or (sys.argv[1] != report_format_lcov and sys.argv[1] != report_format_llvm):
    print("Usage: %s (%s|%s) modified_lines.json report.html" % (sys.argv[0], report_format_lcov, report_format_llvm))
    exit()

report_format = sys.argv[1]
modified_lines_file = sys.argv[2]
report_html_file = sys.argv[3]

# Expect a JSON like { "foo.cpp": [5, 6, 7], "bar.cpp": ... } and convert it to
# a Python dictionary like { "foo.cpp": {5, 6, 7}, "bar.cpp":  ... } for fast
# lookup.
modified_lines = {}
with open(modified_lines_file, "r") as f:
    j = json.load(f)
    for file_name in j:
        modified_lines[file_name] = {}
        for line_num in j[file_name]:
            modified_lines[file_name][line_num] = True

def dim_lcov_report_extend_legend(doc):
    try:
        legend = doc.xpath("//td[@class='headerValueLeg']")[0]
        legend.text = ""

        modified_by_patch = E.SPAN(E.SPAN("Modified by patch:"), E.BR(), E.SPAN("Lines: "))
        not_modified_by_patch = E.SPAN(E.SPAN("Not modified by patch:"), E.BR(), E.SPAN("Lines: "), style = dim_style)
        for c in legend.getchildren():
            memo = {}
            modified_by_patch.append(c.__deepcopy__(memo))
            memo = {}
            not_modified_by_patch.append(c.__deepcopy__(memo))

        legend.clear()
        legend.set("class", "headerValueLeg")
        legend.append(modified_by_patch)
        legend.append(E.HR())
        legend.append(not_modified_by_patch)
    except:
        # ignore errors in case there is no legend
        pass

# Dim lines not modified by the patch in a lcov+genhtml report.
def dim_lcov_report(doc):
    # xpath() doc:
    # https://lxml.de/tutorial.html#using-xpath-to-find-text
    # https://devhints.io/xpath

    # "<title>LCOV - all.lcov - src/netaddress.cpp</title>" --> "src/netaddress.cpp"
    source_code_file = doc.xpath("//title")[0].text.split(" ")[-1:][0]

    dim_lcov_report_extend_legend(doc)

    modified_and_not_covered_lines = []

    for line_num_span in doc.xpath("//*[@class='lineNum']"):
        line_num = int(line_num_span.text)

        line_a = line_num_span.getparent()

        line_a.addprevious(E.A("#", href = "#" + str(line_num)))

        if source_code_file not in modified_lines or line_num not in modified_lines[source_code_file]:
            line_a.set("style", dim_style)
        else:
            if len(line_a.xpath(".//*[@class='lineNoCov']")) > 0:
                modified_and_not_covered_lines.append(line_num)

    if len(modified_and_not_covered_lines) > 0:
        html_report = source_code_file + ".gcov.html"
        print("<a href='%s'>%s</a>: [%s]<br>" % (html_report, source_code_file, ", ".join(map(lambda n: "<a href='" + html_report + "#" + str(n) + "'>" + str(n) + "</a>", modified_and_not_covered_lines))))

# Dim lines not modified by the patch in a llvm report.
def dim_llvm_report(doc):
    raise "not implemented yet"

with open(report_html_file, "r+") as f:
    doc = html5_parser.parse(f.read())

    if report_format == report_format_lcov:
        dim_lcov_report(doc)
    else:
        dim_llvm_report(doc)

    f.seek(0)
    f.truncate()
    f.write(lxml.html.tostring(doc).decode('utf8'))
