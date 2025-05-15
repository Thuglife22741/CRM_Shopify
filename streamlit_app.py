# Arquivo de entrada para o Streamlit Cloud
# Este arquivo importa o app.py da pasta dashboard

import sys
import os

# Adicionar o diretório raiz ao path do Python para garantir que os imports funcionem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Inicializar o ambiente e garantir que as dependências estejam instaladas
from init_streamlit import initialize_environment
initialize_environment()

# Garantir que as dependências estejam instaladas antes de qualquer importação
try:
    # Verificar e instalar dependências necessárias
    import importlib.util
    import subprocess
    
    # Função para verificar se um módulo está instalado
    def is_module_installed(module_name):
        return importlib.util.find_spec(module_name) is not None
    
    # Função para instalar um pacote se não estiver disponível
    def ensure_package(package_name, version=None):
        package_spec = f"{package_name}=={version}" if version else package_name
        if not is_module_installed(package_name.split('[')[0]):
            print(f"Instalando {package_spec}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec, "--no-cache-dir"])
            return True
        return False
    
    # Atualizar pip primeiro
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--no-cache-dir"])
    
    # Instalar dependências críticas
    ensure_package("plotly", "5.18.0")
    ensure_package("plotly-express", "0.4.1")
    ensure_package("tenacity")
    ensure_package("psutil")
    ensure_package("retrying")
    
    # Agora importar os módulos necessários
    import plotly
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