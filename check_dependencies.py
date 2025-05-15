# Script para verificar dependências e ambiente
import sys
import os
import subprocess
import json

def check_dependencies():
    """Verifica as dependências instaladas e gera um relatório"""
    # Informações do ambiente
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
    
    # Verificar especificamente o plotly
    try:
        import plotly
        env_info["plotly_version"] = plotly.__version__
        env_info["plotly_path"] = plotly.__file__
    except ImportError:
        env_info["plotly_error"] = "Plotly não está instalado"
    
    # Verificar plotly.express
    try:
        import plotly.express
        env_info["plotly_express_version"] = plotly.express.__version__
        env_info["plotly_express_path"] = plotly.express.__file__
    except ImportError as e:
        env_info["plotly_express_error"] = str(e)
    
    # Salvar relatório
    with open("dependency_report.json", "w") as f:
        json.dump(env_info, f, indent=2)
    
    return env_info

if __name__ == "__main__":
    check_dependencies()