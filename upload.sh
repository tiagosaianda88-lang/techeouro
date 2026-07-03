#!/bin/bash
set -e

# Script para fazer upload rapido das alteracoes para o GitHub

echo "A iniciar o upload para o GitHub..."

BRANCH="$(git branch --show-current)"
REMOTE="${GIT_REMOTE:-origin}"
COMMIT_MSG="${1:-Atualizacao automatica}"

if [ -z "$BRANCH" ]; then
  echo "Nao foi possivel detectar o branch atual."
  exit 1
fi

# Adicionar apenas ficheiros relevantes, respeitando o .gitignore.
git add -A

if git diff --cached --quiet; then
  echo "Nao ha alteracoes para enviar."
  exit 0
fi

git commit -m "$COMMIT_MSG"

# Enviar para o GitHub sem depender de um branch escrito a mao.
git push "$REMOTE" "$BRANCH"

echo "----------------------------------------"
echo "Upload concluido com sucesso no GitHub!"
echo "As alterações serão publicadas automaticamente pelo Netlify em instantes."
echo "----------------------------------------"
