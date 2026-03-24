#!/bin/zsh
set -euo pipefail

export PYTHONPATH=/Users/guldana/Documents/New\ project/marketplace-bots/src
export MP_BOTS_DB=${MP_BOTS_DB:-/Users/guldana/Documents/New\ project/marketplace-bots/tmp/dev.db}
export MP_BOTS_STORES=${MP_BOTS_STORES:-/Users/guldana/Documents/New\ project/marketplace-bots/config/stores.sample.json}

if [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]]; then
  echo "TELEGRAM_BOT_TOKEN is not set"
  exit 1
fi

python3 -m mp_bots.bot.telegram_bot
