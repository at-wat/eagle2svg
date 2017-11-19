#!/bin/bash

set -eu

PY=`find . -type d -name build -prune -o -name "*.py" -print | tr '\n' ' '`
echo "pyflakes targets: ${PY}"

LOG=/tmp/coding-style.log
(rm -f ${LOG} || true)

fail=0
for py in ${PY}
do
  pycodestyle ${py} >> ${LOG} || fail=1; true
  pyflakes ${py} >> ${LOG} || fail=1; true
done

FAILED="Failed on python ${TRAVIS_PYTHON_VERSION}"
PASSED="Passed on python ${TRAVIS_PYTHON_VERSION}"

if [ $fail -eq 1 ]
then
  echo 'failed'
  gh-pr-comment "${FAILED}" \
    "style check failed.
\`\`\`
`cat ${LOG}`
\`\`\`"
  false
fi
echo 'passed'
