# Script para inicializar o ambiente Streamlit e garantir que todas as dependências estejam instaladas
import sys
import os
import importlib.util
import subprocess
import json

def is_module_installed(module_name):
    """Verifica se um módulo está instalado"""
    return importlib.util.find_spec(module_name) is not None

def ensure_package(package_name, version=None):
    """Instala um pacote se não estiver disponível"""
    package_spec = f"{package_name}=={version}" if version else package_name
    if not is_module_installed(package_name.split('[')[0]):
        print(f"Instalando {package_spec}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec, "--no-cache-dir"])
        return True
    return False

def initialize_environment():
    """Inicializa o ambiente para o Streamlit"""
    # Adicionar o diretório raiz ao path do Python
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
    
    # Atualizar pip primeiro
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--no-cache-dir"])
    except Exception as e:
        print(f"Erro ao atualizar pip: {e}")
    
    # Lista de pacotes críticos para o funcionamento do app
    critical_packages = {
        "streamlit": "1.30.0",
        "plotly": "5.18.0",
        "plotly-express": "0.4.1",
        "pandas": "2.0.0",
        "numpy": "1.24.0",
        "python-dotenv": "1.0.0",
        "redis": "5.0.0",
        "tenacity": None,
        "psutil": None,
        "retrying": None
    }
    
    # Instalar pacotes críticos
    for package, version in critical_packages.items():
        try:
            ensure_package(package, version)
        except Exception as e:
            print(f"Erro ao instalar {package}: {e}")
    
    # Verificar se plotly e plotly.express estão disponíveis
    try:
        import plotly
        print(f"Plotly versão: {plotly.__version__}")
        import plotly.express
        print(f"Plotly Express versão: {plotly.express.__version__}")
    except ImportError as e:
        print(f"Erro ao importar plotly: {e}")
        # Tentar instalar novamente com opções diferentes
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "plotly==5.18.0", "--no-cache-dir", "--force-reinstall"])
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "plotly-express==0.4.1", "--no-cache-dir", "--force-reinstall"])
        except Exception as e:
            print(f"Erro ao reinstalar plotly: {e}")
    
    # Gerar relatório de ambiente
    env_info = {
        "python_version": sys.version,
        "python_path": sys.executable,
        "platform": sys.platform,
        "cwd": os.getcwd(),
        "sys_path": sys.path,
    }
    
    # Verificar pacotes instalados
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )
        packages = json.loads(result.stdout)
        env_info["installed_packages"] = packages
    except Exception as e:
        env_info["pip_list_error"] = str(e)
    
    # Salvar relatório em um arquivo temporário para diagnóstico
    try:
        with open(os.path.join(os.getcwd(), "streamlit_env_report.json"), "w") as f:
            json.dump(env_info, f, indent=2)
    except Exception as e:
        print(f"Erro ao salvar relatório de ambiente: {e}")
    
    return True

if __name__ == "__main__":
    initialize_environment()