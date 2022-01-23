#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset


python src/kafka/consume.py
