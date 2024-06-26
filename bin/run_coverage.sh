#!/bin/bash
pytest -vv --cov=test_files_src --cov-context=test test_files_test/test_main.py test_files_test/test_source_code.py
coverage json --show-context --pretty-print