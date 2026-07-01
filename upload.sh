#!/bin/bash
# Script para fazer upload rápido das alterações para o GitHub

echo "A iniciar o upload para o GitHub..."

# Adicionar todos os ficheiros modificados
git add .

# Fazer o commit (usa a mensagem passada como argumento ou uma padrão)
COMMIT_MSG="${1:-Atualizacao automatica}"
git commit -m "$COMMIT_MSG"

# Enviar para o GitHub
git push origin main


echo "----------------------------------------"
echo "Upload concluido com sucesso no GitHub!"
echo "As alterações serão publicadas automaticamente pelo Netlify em instantes."
echo "----------------------------------------"
