#!/usr/bin/env bash
# Rebuilds everything that is not committed to git.
# Each step runs only if its output is missing; delete the output to force a rebuild.
# While modules are still stubs, failing steps only print a warning so the API can start.
set -u
cd "$(dirname "$0")/.."

DATA_DIR="${DATA_DIR:-data}"
MODELS_DIR="${MODELS_DIR:-models}"

step() {  # step <description> <command...>
  local desc="$1"; shift
  echo "==> $desc"
  "$@" || echo "WARN: '$desc' failed or not implemented yet - continuing"
}

# 1. Fine-tuned classifier from Hugging Face
if [ ! -d "$MODELS_DIR/classifier" ]; then
  if [ -n "${CLASSIFIER_REPO:-}" ] && [[ "$CLASSIFIER_REPO" != *"<hf-username>"* ]]; then
    step "Download classifier ($CLASSIFIER_REPO)" \
      hf download "$CLASSIFIER_REPO" --local-dir "$MODELS_DIR/classifier"
  else
    echo "==> Skip classifier download (CLASSIFIER_REPO not set in .env)"
  fi
fi

# 2. Pretrained models (bcms-bertic-ner, embedic) download on first use into HF_HOME

# 3. Messages: messages.jsonl -> messages.sqlite
if [ -f "$DATA_DIR/messages.jsonl" ] && [ ! -f "$DATA_DIR/messages.sqlite" ]; then
  step "Load messages into sqlite" python scripts/load_messages.py
fi

# 4. Gazetteer: Lucene index + embedding vectors
if [ -f "$DATA_DIR/gazetteer.json" ] && [ ! -d "$DATA_DIR/lucene/gazetteer" ]; then
  step "Index gazetteer (Lucene + Embedić)" python scripts/index_gazetteer.py
fi

echo "==> Setup done."
exit 0
