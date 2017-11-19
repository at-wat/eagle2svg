#!/bin/bash

set -eu

FAILED="Failed on python ${TRAVIS_PYTHON_VERSION}"
PASSED="Passed on python ${TRAVIS_PYTHON_VERSION}"

eagle2svg ./tests/data/test.sch > test.sch.svg \
  || (gh-pr-comment "${FAILED}" '`eagle2svg ./tests/data/test.sch` failed.'; false)
eagle2svg ./tests/data/test.brd 0 1 20 17 18 21 25 19 > test-top.brd.svg \
  || (gh-pr-comment "${FAILED}" '`eagle2svg ./tests/data/test.brd 0 1 20 17 18 21 25 19` failed.'; false)
eagle2svg ./tests/data/test.brd 0 16 20 17 18 22 26 19 > test-bottom.brd.svg \
  || (gh-pr-comment "${FAILED}" '`eagle2svg ./tests/data/test.brd 0 16 20 17 18 22 26 19` failed.'; false)

cairosvg -f png -d 300 -o test.sch.png test.sch.svg \
  || (gh-pr-comment "${FAILED}" '`cairosvg -f png test.sch.svg` failed.'; false)
cairosvg -f png -d 450 -o test-top.brd.png test-top.brd.svg \
  || (gh-pr-comment "${FAILED}" '`cairosvg -f png test.sch.svg` failed.'; false)
cairosvg -f png -d 450 -o test-bottom.brd.png test-bottom.brd.svg \
  || (gh-pr-comment "${FAILED}" '`cairosvg -f png test.sch.svg` failed.'; false)

gh-pr-comment "${PASSED}" "all tests passed
\`\`\`
`ls -lh *.svg *.png`
\`\`\`"
