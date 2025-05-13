# Dashboard Streamlit para Shopify CRM WhatsApp

Este dashboard foi desenvolvido para visualizar e gerenciar dados da integração entre Shopify, WhatsApp e CRM.

## Funcionalidades

- **Visão Geral**: Métricas principais e gráficos resumidos de vendas e conversas
- **Vendas**: Análise detalhada de pedidos do Shopify com filtros por data e status
- **Clientes**: Gestão de clientes com métricas de compras e interações
- **Conversas**: Histórico e análise de conversas do WhatsApp
- **Configurações**: Visualização das configurações atuais do sistema

## Como Executar

Para executar o dashboard, use o seguinte comando:

```bash
python -m streamlit run src/automacao_assistente_loja_shopify_whatsapp_crm_dashboard/dashboard/app.py
```

Ou utilize o comando configurado no pyproject.toml:

```bash
python -m automacao_assistente_loja_shopify_whatsapp_crm_dashboard.streamlit_app
```

## Requisitos

- Python 3.10 ou superior
- Streamlit 1.30.0 ou superior
- Redis 5.0.0 ou superior
- Pandas 2.0.0 ou superior
- Plotly 5.18.0 ou superior
- Shopify API Python 12.3.0 ou superior

## Configuração

O dashboard utiliza as mesmas variáveis de ambiente do sistema principal, definidas no arquivo `.env` na raiz do projeto:

- Configurações do Shopify (SHOPIFY_SHOP_URL, SHOPIFY_ACCESS_TOKEN, etc.)
- Configurações do WhatsApp (GRAPH_API_TOKEN, WHATSAPP_PHONE_NUMBER_ID, etc.)
- Configurações do Redis (REDIS_URL, REDIS_PASSWORD)

Certifique-se de que todas as variáveis estejam corretamente configuradas antes de executar o dashboard.