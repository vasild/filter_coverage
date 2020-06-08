#!/usr/bin/env bash

set -e

if [ "${#}" -ne 2 -a "${#}" -ne 3 -a "${#}" -ne 4 ] ; then
    echo "Get modified lines in a topic branch" >&2
    echo "Usage: ${0} source_directory exclude_pattern [topic_branch_defaults_to_HEAD [base_branch_defaults_to_origin/master]]" >&2
    exit 64
fi

source_directory=${1}
exclude_pattern=${2}
branch=${3:-HEAD}
branch=${4:-origin/master}

cd "${source_directory}"

# get the commits that this branch has on top of origin/master
commits=$(git log --format=%H origin/master..)

# get the list of modified files
files=$(
    for h in ${commits} ; do
        git show --name-only --diff-filter=d --format= ${h}
    done |sort -u |grep -vE "${exclude_pattern}"
)

json="{"
for file in ${files} ; do
    # ignore deleted files
    if [ ! -f "${file}" ] ; then
        continue
    fi
    # get all line numbers in this file concatenated with a ,
    lines=$(
        git blame -s --abbrev=40 "${file}" \
            |grep -F "${commits}" \
            |sed -E "s|^[^)]+ ([0-9]+)\\).*$|\1|" \
            |tr '\n' ','
    )
    lines=${lines%,} # remove trailing ,
    json="${json}\"${file}\":[${lines}],"
done
json=${json%,} # remove trailing ,
json="${json}}"
printf "%s" "${json}"
