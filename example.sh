#!/usr/bin/env bash
set -euo pipefail

curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"DROP TABLE customers;"}]}'

# Ожидаемый ответ:
# {"reply":"Запрос заблокирован политикой."}
# Основная модель для этого запроса не вызывается.
