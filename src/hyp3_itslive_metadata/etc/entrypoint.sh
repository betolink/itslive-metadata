#!/bin/bash --login
set -e
conda activate hyp3-itslive-metadata
exec python -um hyp3_itslive_metadata "$@"
