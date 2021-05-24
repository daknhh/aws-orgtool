#!/usr/bin/env bash

set -e

pip3 install bandit=="${INPUT_VERSION}"

# shellcheck disable=SC2086
bandit ${INPUT_OPTIONS} ${INPUT_TARGETS}