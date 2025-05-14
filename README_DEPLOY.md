# Instruções para Deploy no Streamlit Cloud

## Arquivos de Configuração

Foram criados os seguintes arquivos para facilitar o deploy no Streamlit Cloud:

1. **streamlit_app.py**: Arquivo principal que o Streamlit Cloud irá executar. Este arquivo importa o app.py da pasta dashboard.

2. **.streamlit/config.toml**: Configurações do servidor Streamlit.

3. **.streamlit/secrets.toml**: Template para configuração de segredos (não deve ser commitado no repositório).

4. **packages.txt**: Dependências do sistema necessárias para o funcionamento do plotly.

5. **requirements.txt**: Dependências Python atualizadas com versões específicas.

## Como Fazer o Deploy

1. Faça o commit de todos os arquivos para o seu repositório Git, exceto o arquivo `.streamlit/secrets.toml`.

2. Acesse o [Streamlit Cloud](https://streamlit.io/cloud) e faça login.

3. Clique em "New app" e selecione o seu repositório.

4. Configure o app da seguinte forma:
   - **Repository**: Seu repositório Git
   - **Branch**: main (ou a branch que contém o código)
   - **Main file path**: `streamlit_app.py`

5. Em "Advanced settings", configure os segredos necessários:
   ```
   [redis]
   url = "sua_url_do_redis"
   password = "sua_senha_do_redis"

   [shopify]
   api_key = "sua_api_key"
   api_secret = "seu_api_secret"
   store_url = "sua_store_url"
   ```

6. Clique em "Deploy" e aguarde o processo de deploy ser concluído.

## Solução de Problemas

Se você encontrar o erro `ModuleNotFoundError: No module named 'plotly.express'`, verifique se:

1. O arquivo `requirements.txt` está na raiz do projeto e contém `plotly==5.18.0` e `plotly-express==0.4.1`.

2. O arquivo `packages.txt` está na raiz do projeto com as dependências do sistema.

3. O arquivo `streamlit_app.py` está configurado corretamente para importar o módulo do dashboard.

## Estrutura do Projeto

```
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml (não commitado)
├── src/
│   └── automacao_assistente_loja_shopify_whatsapp_crm_dashboard/
│       └── dashboard/
│           └── app.py
├── packages.txt
├── requirements.txt
├── streamlit_app.py
└── README_DEPLOY.md
```