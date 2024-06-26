#!/bin/bash
#
function finally {
    popd &> /dev/null
}
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pushd ${THIS_DIR}/../test &> /dev/null
trap finally EXIT

export PYTHONPATH=${THIS_DIR}/../test
../bin/run_coverage.sh 
coverage html --show-context --data-file .coverage -d htmlcov_before
../bin/run_improve_coverage.sh 
coverage html --show-context --data-file .output_db -d htmlcov_after
