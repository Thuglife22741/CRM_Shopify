# Arquivo de entrada para o Streamlit Cloud
# Este arquivo importa o app.py da pasta dashboard

import sys
import os

# Adicionar o diretório raiz ao path do Python para garantir que os imports funcionem
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar o app do dashboard
from src.automacao_assistente_loja_shopify_whatsapp_crm_dashboard.dashboard.app import *

# Se este arquivo for executado diretamente
if __name__ == "__main__":
    # Executar a função main do app.py
    main()