# Tech & Ouro - Operacao de Contas, Faturas e Publicidade

Este documento existe para manter o projeto controlado enquanto cresce.

## Objetivo
Controlar publicidade, faturacao, receita e risco operacional sem perder qualidade editorial.

## Rotina Semanal
- Verificar se `https://techeouro.net` abre sem erros.
- Verificar rotas principais: `/`, `/mercados`, `/ouro`, `/economia`, `/tech`, `/desporto`, `/paises`, `/noticias`, `/sobre`, `/terminal`, `/geopolitica`, `/loja`.
- Correr `python3 scripts/ops_health_report.py`.
- Confirmar que o Google Ads tag usa `AW-1827959532`.
- Confirmar que o AdSense usa `ca-pub-2757348402596933`.
- Confirmar que `ads.txt` publica `pub-2757348402596933`.
- Rever GitHub Actions para falhas no `AI News Aggregator`.
- Confirmar que a Netlify publicou o commit mais recente.

## Rotina Mensal de Faturas
- Google Ads: abrir faturacao, descarregar fatura/recibo do mes, confirmar gasto real e campanha ativa.
- Google AdSense: rever pagamentos, saldo, politicas e avisos de anuncios.
- Netlify: rever plano, uso, dominios, largura de banda e fatura.
- GitHub: rever Actions/minutos se houver cobranca.
- Dominio/DNS: confirmar renovacao de `techeouro.net` e estado DNS.

## Regras de Seguranca
- Nunca guardar passwords, tokens, cartoes, IBANs, faturas privadas ou dados fiscais no repositorio.
- Nunca aumentar orcamento de Google Ads sem confirmacao explicita do Tiago.
- Nunca alterar metodo de pagamento sem confirmacao explicita do Tiago.
- Nunca publicar screenshots de faturas ou contas privadas.
- Qualquer relatorio para partilha publica deve remover dados pessoais e financeiros.

## Indicadores que Interessa Ver
- Gasto diario e mensal em Google Ads.
- Cliques, impressoes, CTR e CPC.
- Paginas com melhor desempenho.
- Receita AdSense, RPM e paginas com anuncios servidos.
- Erros 404, assets em falta e paginas cinzentas.
- Percentagem de noticias novas no index.

## Links de Trabalho
- Site: https://techeouro.net
- Netlify: https://app.netlify.com/projects/projeto-teste-tiago-oculto
- GitHub: https://github.com/tiagosaianda88-lang/techeouro
- Google Ads: https://ads.google.com
- Google AdSense: https://www.google.com/adsense

