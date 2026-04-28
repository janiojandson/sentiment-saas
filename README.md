# SentimentSaaS

Micro-SaaS de Análise de Sentimentos em Redes Sociais para Pequenas Empresas.

## Visão Geral

SentimentSaaS é uma plataforma que permite que pequenas empresas monitorem e analisem o sentimento de menções sobre sua marca, produtos e serviços nas redes sociais. Utilizando técnicas avançadas de Processamento de Linguagem Natural (NLP) e aprendizado de máquina, a plataforma oferece insights acionáveis para melhorar estratégias de marketing e relacionamento com clientes.

## Principais Funcionalidades

- 🔍 **Monitoramento de Menções**: Acompanhe o que estão falando sobre sua marca nas redes sociais
- 📊 **Análise de Sentimentos**: Classifique automaticamente menções como positivas, negativas ou neutras
- 📈 **Dashboard Interativo**: Visualize tendências e padrões ao longo do tempo
- 🚨 **Sistema de Alertas**: Receba notificações sobre menções negativas que exigem atenção imediata
- 📱 **Multi-plataforma**: Suporte para Twitter/X, Instagram e Facebook

## Arquitetura

O projeto é dividido em dois componentes principais:

1. **Backend API (FastAPI + ML)**
   - API RESTful para análise de sentimentos
   - Coletores de dados para redes sociais
   - Modelos de ML para classificação de sentimentos

2. **Frontend (Vue.js)**
   - Dashboard interativo
   - Visualizações e gráficos
   - Sistema de gerenciamento de usuários

## Tecnologias

- **Backend**: Python, FastAPI, Hugging Face Transformers
- **Frontend**: Vue.js, Tailwind CSS
- **Banco de Dados**: PostgreSQL, pgvector
- **Infraestrutura**: Docker, AWS

## Roadmap

- [x] Pesquisa e análise de viabilidade
- [ ] Desenvolvimento do core engine de análise de sentimentos
- [ ] Integração com API do Twitter/X
- [ ] Desenvolvimento do dashboard básico
- [ ] Implementação do sistema de usuários e pagamentos
- [ ] Integração com Instagram e Facebook
- [ ] Lançamento beta