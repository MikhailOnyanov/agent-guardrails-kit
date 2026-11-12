#!/usr/bin/env bash
set -euo pipefail

mf list metrics
mf list dimensions --metrics revenue

mf query --metrics revenue \
  --group-by metric_time__quarter,order_id__region \
  --start-time 2026-07-01 \
  --end-time 2026-09-30 \
  --limit 1000 \
  --csv out.csv
