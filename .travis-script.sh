#!/bin/bash

# Ask bash to stop if something happens.
set -e

./tests.py
./util_tests.py
