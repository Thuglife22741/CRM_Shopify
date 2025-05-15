# Arquivo de entrada para o Streamlit Cloud
# Este arquivo importa o app.py da pasta dashboard

import sys
import os

# Adicionar o diretório raiz ao path do Python para garantir que os imports funcionem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar diretamente o app.py da pasta dashboard
try:
    # Primeiro, tente importar o módulo plotly.express para garantir que está disponível
    import plotly.express as px
    import plotly.graph_objects as go
    
    # Importar o app do dashboard
    from src.automacao_assistente_loja_shopify_whatsapp_crm_dashboard.dashboard.app import *
    
    # Se este arquivo for executado diretamente
    if __name__ == "__main__":
        # Executar a função main do app.py
        main()
        
except ImportError as e:
    import streamlit as st
    st.error(f"Erro ao importar módulos: {e}")
    st.info("Verifique se todas as dependências estão instaladas corretamente.")
    st.code("pip install plotly==5.18.0 plotly-express==0.4.1")
    st.info("Se o erro persistir, entre em contato com o suporte.")