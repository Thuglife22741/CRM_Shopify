import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import redis
import json
import os
import datetime
import locale
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar locale para formatação de números no padrão brasileiro
def format_currency_br(value):
    """Formata um valor monetário no padrão brasileiro (R$ 150,00)"""
    # Formata o número com duas casas decimais, vírgula como separador decimal
    # e ponto como separador de milhar
    # Garante que sempre tenha duas casas decimais e use vírgula como separador decimal
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Configuração da página
st.set_page_config(
    page_title="Shopify CRM WhatsApp Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para conectar ao Redis
def connect_to_redis():
    try:
        # Usar a URL do Redis Cloud configurada no .env
        redis_url = os.getenv("REDIS_URL")
        redis_password = os.getenv("REDIS_PASSWORD", "")
        
        if not redis_url:
            st.warning("URL do Redis não configurada no arquivo .env. Usando redis://localhost:6379 como fallback.")
            redis_url = "redis://localhost:6379"
        else:
            # Garantir que a URL do Redis Cloud esteja no formato correto
            # Verificar se a URL já começa com redis:// ou rediss://
            if not (redis_url.startswith("redis://") or redis_url.startswith("rediss://")):
                # Formatar a URL do Redis Cloud corretamente
                # Formato esperado: redis://username:password@host:port
                host_port = redis_url  # Ex: redis-15559.crce181.sa-east-1-2.ec2.redns.redis-cloud.com:15559
                
                # Construir a URL completa com autenticação
                if redis_password:
                    # Corrigido o formato da URL para incluir a senha corretamente
                    redis_url = f"redis://:{redis_password}@{host_port}"
                else:
                    redis_url = f"redis://{host_port}"
                
                # st.info(f"Conectando ao Redis Cloud: {host_port}")
        
        # Tentar conectar ao Redis    
        r = redis.from_url(redis_url)
        # Testar a conexão com um ping
        r.ping()
        return r
    except redis.exceptions.ConnectionError as e:
        # Erro específico de conexão
        st.warning(f"Não foi possível conectar ao Redis: {e}")
        if "Error 10061" in str(e) and "localhost:6379" in str(e):
            st.info("O Redis local não está em execução. Você pode:")  
            st.info("1. Instalar e iniciar o Redis Server localmente")
            st.info("2. Usar um serviço Redis Cloud (recomendado) e configurar no arquivo .env")
            st.info("3. Continuar usando o dashboard com armazenamento temporário (funcionalidade limitada)")
        return None
    except Exception as e:
        # Outros erros
        st.error(f"Erro ao conectar ao Redis: {e}")
        return None

# Classe para armazenamento temporário quando Redis não estiver disponível
class TemporaryStorage:
    def __init__(self):
        self.data = {}
    
    def set(self, key, value):
        self.data[key] = value
        return True
    
    def get(self, key):
        return self.data.get(key)
    
    def keys(self, pattern="*"):
        # Implementação simples de pattern matching
        if pattern == "*":
            return list(self.data.keys())
        else:
            prefix = pattern.replace("*", "")
            return [k for k in self.data.keys() if k.startswith(prefix)]

# Armazenamento temporário global
temp_storage = TemporaryStorage()

# Função para carregar dados do CRM do Redis ou armazenamento temporário
def load_crm_data(redis_client):
    try:
        # Se não tiver Redis, usar dados de demonstração
        if not redis_client:
            st.info("Usando armazenamento temporário para dados do CRM (modo de demonstração)")
            # Verificar se já temos dados no armazenamento temporário
            keys = temp_storage.keys("interaction:*")
            
            # Se não tiver dados no armazenamento temporário, criar alguns dados de demonstração
            if not keys:
                # Criar dados de demonstração
                demo_data = [
                    {"interaction_id": "i1001", "customer": "João Silva", "type": "email", "timestamp": "2023-06-01 09:30:00", "status": "Resolvido"},
                    {"interaction_id": "i1002", "customer": "Maria Oliveira", "type": "chat", "timestamp": "2023-06-02 14:00:00", "status": "Pendente"},
                    {"interaction_id": "i1003", "customer": "Pedro Santos", "type": "telefone", "timestamp": "2023-06-03 11:15:00", "status": "Resolvido"},
                    {"interaction_id": "i1004", "customer": "Ana Costa", "type": "email", "timestamp": "2023-06-04 16:45:00", "status": "Pendente"},
                    {"interaction_id": "i1005", "customer": "Carlos Ferreira", "type": "chat", "timestamp": "2023-06-05 10:30:00", "status": "Resolvido"},
                ]
                
                # Armazenar no armazenamento temporário
                for item in demo_data:
                    key = f"interaction:{item['interaction_id']}"
                    temp_storage.set(key, json.dumps(item))
                
                keys = temp_storage.keys("interaction:*")
            
            # Carregar dados do armazenamento temporário
            data = []
            for key in keys:
                interaction = temp_storage.get(key)
                if interaction:
                    try:
                        interaction_data = json.loads(interaction)
                        data.append(interaction_data)
                    except json.JSONDecodeError:
                        pass
            
            if data:
                df = pd.DataFrame(data)
                # Converter timestamp para datetime
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                return df
            return pd.DataFrame()
        
        # Se tiver Redis, usar normalmente
        keys = redis_client.keys("interaction:*")
        
        data = []
        for key in keys:
            interaction = redis_client.get(key)
            if interaction:
                try:
                    interaction_data = json.loads(interaction)
                    data.append(interaction_data)
                except json.JSONDecodeError:
                    pass
        
        if data:
            df = pd.DataFrame(data)
            # Converter timestamp para datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados do CRM: {e}")
        return pd.DataFrame()

# Função para simular dados de pedidos do Shopify (para demonstração)
def load_shopify_orders():
    try:
        # Em um ambiente real, você usaria a API do Shopify para buscar pedidos
        # Aqui estamos simulando dados para demonstração
        data = [
            {"order_id": "1001", "customer": "João Silva", "value": 150.00, "date": "2023-06-01", "status": "Entregue"},
            {"order_id": "1002", "customer": "Maria Oliveira", "value": 200.00, "date": "2023-06-02", "status": "Processando"},
            {"order_id": "1003", "customer": "Pedro Santos", "value": 1500.00, "date": "2023-06-03", "status": "Enviado"},
            {"order_id": "1004", "customer": "Ana Costa", "value": 500.00, "date": "2023-06-04", "status": "Entregue"},
            {"order_id": "1005", "customer": "Carlos Ferreira", "value": 254.35, "date": "2023-06-05", "status": "Processando"},
            {"order_id": "1006", "customer": "Fernanda Lima", "value": 325.48, "date": "2023-06-06", "status": "Enviado"},
        ]
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados do Shopify: {e}")
        return pd.DataFrame()

# Função para simular dados de conversas do WhatsApp (para demonstração)
def load_whatsapp_conversations():
    try:
        # Em um ambiente real, você buscaria esses dados do seu banco de dados
        data = [
            {"conversation_id": "w1001", "customer": "João Silva", "timestamp": "2023-06-01 10:15:00", "message_count": 5, "status": "Resolvido"},
            {"conversation_id": "w1002", "customer": "Maria Oliveira", "timestamp": "2023-06-02 14:30:00", "message_count": 3, "status": "Pendente"},
            {"conversation_id": "w1003", "customer": "Pedro Santos", "timestamp": "2023-06-03 09:45:00", "message_count": 8, "status": "Resolvido"},
            {"conversation_id": "w1004", "customer": "Ana Costa", "timestamp": "2023-06-04 16:20:00", "message_count": 2, "status": "Pendente"},
            {"conversation_id": "w1005", "customer": "Carlos Ferreira", "timestamp": "2023-06-05 11:10:00", "message_count": 6, "status": "Resolvido"},
        ]
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados do WhatsApp: {e}")
        return pd.DataFrame()

# Função para salvar configurações
def save_config(config_type, config_data):
    try:
        # Caminho para o arquivo .env
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        
        # Verificar se o arquivo .env existe
        if not os.path.exists(env_path):
            # Se não existir, criar um novo arquivo
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write("# Arquivo de configuração\n")
        
        # Ler o conteúdo atual do arquivo .env
        with open(env_path, 'r', encoding='utf-8') as f:
            env_lines = f.readlines()
        
        # Processar cada linha para atualizar ou adicionar configurações
        updated_lines = []
        updated_keys = set()
        
        for line in env_lines:
            line = line.strip()
            if not line or line.startswith('#'):
                # Manter comentários e linhas em branco
                updated_lines.append(line)
                continue
            
            # Verificar se a linha contém uma configuração
            if '=' in line:
                key, _ = line.split('=', 1)
                key = key.strip()
                
                # Verificar se esta chave está nas novas configurações
                if key in config_data:
                    # Atualizar o valor
                    updated_lines.append(f"{key}={config_data[key]}")
                    updated_keys.add(key)
                else:
                    # Manter a configuração existente
                    updated_lines.append(line)
            else:
                # Manter outras linhas
                updated_lines.append(line)
        
        # Adicionar novas configurações que não existiam antes
        for key, value in config_data.items():
            if key not in updated_keys:
                updated_lines.append(f"{key}={value}")
        
        # Escrever as configurações atualizadas de volta no arquivo .env
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines) + '\n')
        
        # Recarregar as variáveis de ambiente
        load_dotenv(override=True)
        
        st.success(f"Configurações de {config_type} salvas com sucesso no arquivo .env!")
        return True
    except Exception as e:
        st.error(f"Erro ao salvar configurações: {e}")
        return False

# Função principal
def main():
    # Título do dashboard
    st.title("📊 Shopify CRM WhatsApp Dashboard")
    
    # Sidebar para navegação
    st.sidebar.title("Menu")
    page = st.sidebar.selectbox(
        "Escolha uma opção:",
        ["Dashboard", "Pedidos", "Clientes", "Conversas", "Configurações"]
    )
    
    # Conectar ao Redis
    redis_client = connect_to_redis()
    
    # Carregar dados
    crm_data = load_crm_data(redis_client)
    shopify_orders = load_shopify_orders()
    whatsapp_conversations = load_whatsapp_conversations()
    
    # Página: Dashboard
    if page == "Dashboard":
        st.header("Visão Geral do Sistema")
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Pedidos", len(shopify_orders))
        
        with col2:
            total_revenue = shopify_orders['value'].sum() if not shopify_orders.empty else 0
            st.metric("Receita Total", format_currency_br(total_revenue))
        
        with col3:
            st.metric("Conversas WhatsApp", len(whatsapp_conversations))
        
        with col4:
            resolved = len(whatsapp_conversations[whatsapp_conversations['status'] == 'Resolvido']) if not whatsapp_conversations.empty else 0
            total = len(whatsapp_conversations) if not whatsapp_conversations.empty else 0
            resolution_rate = (resolved / total * 100) if total > 0 else 0
            st.metric("Taxa de Resolução", f"{resolution_rate:.1f}%")
        
        # Gráficos da visão geral
        st.subheader("Resumo de Vendas")
        if not shopify_orders.empty:
            # Gráfico de vendas por dia
            # Agrupando por data e somando apenas os valores numéricos
            daily_sales = shopify_orders.groupby(shopify_orders['date'].dt.date).agg({
                'value': 'sum',
                'order_id': 'count'  # Contagem de pedidos por dia
            }).reset_index()
            
            # Renomear a coluna order_id para quantidade
            daily_sales.rename(columns={'order_id': 'quantidade'}, inplace=True)
            
            fig = px.bar(
                daily_sales,
                x='date',
                y='value',
                title="Vendas Diárias",
                labels={"date": "Data", "value": "Valor (R$)"},
                color_discrete_sequence=["#0083B8"]
            )
            # Configurar o formato dos valores no eixo Y para usar vírgula como separador decimal
            fig.update_layout(
                yaxis=dict(tickformat=",.2f", tickprefix="R$ ")
            )
            # Configurar o hover para mostrar os valores no formato brasileiro
            fig.update_traces(
                hovertemplate="%{x}<br>Valor: R$ %{y:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados de vendas disponíveis.")
        
        # Status das conversas
        st.subheader("Status das Conversas")
        if not whatsapp_conversations.empty:
            status_counts = whatsapp_conversations['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Contagem']
            
            fig = px.pie(
                status_counts,
                values='Contagem',
                names='Status',
                title="Distribuição de Status das Conversas",
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados de conversas disponíveis.")
    
    # Página: Pedidos
    elif page == "Pedidos":
        st.header("Análise de Vendas")
        
        if not shopify_orders.empty:
            # Filtros
            st.subheader("Filtros")
            col1, col2 = st.columns(2)
            with col1:
                min_date = shopify_orders['date'].min().date()
                max_date = shopify_orders['date'].max().date()
                date_range = st.date_input(
                    "Intervalo de Datas",
                    [min_date, max_date],
                    min_value=min_date,
                    max_value=max_date
                )
            
            with col2:
                status_filter = st.multiselect(
                    "Status do Pedido",
                    options=shopify_orders['status'].unique(),
                    default=shopify_orders['status'].unique()
                )
            
            # Aplicar filtros
            filtered_orders = shopify_orders.copy()
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_orders = filtered_orders[
                    (filtered_orders['date'].dt.date >= start_date) &
                    (filtered_orders['date'].dt.date <= end_date)
                ]
            
            if status_filter:
                filtered_orders = filtered_orders[filtered_orders['status'].isin(status_filter)]
            
            # Métricas de vendas
            st.subheader("Métricas de Vendas")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Pedidos", len(filtered_orders))
            
            with col2:
                total_revenue = filtered_orders['value'].sum()
                st.metric("Receita Total", format_currency_br(total_revenue))
            
            with col3:
                avg_order_value = total_revenue / len(filtered_orders) if len(filtered_orders) > 0 else 0
                st.metric("Valor Médio do Pedido", format_currency_br(avg_order_value))
            
            # Tabela de pedidos
            st.subheader("Lista de Pedidos")
            st.dataframe(
                filtered_orders[['order_id', 'customer', 'value', 'date', 'status']].rename(columns={
                    'order_id': 'ID do Pedido',
                    'customer': 'Cliente',
                    'value': 'Valor (R$)',
                    'date': 'Data',
                    'status': 'Status'
                }),
                use_container_width=True
            )
        else:
            st.info("Não há dados de vendas disponíveis.")
    
    # Página: Clientes
    elif page == "Clientes":
        st.header("Gestão de Clientes")
        
        # Combinar dados de pedidos e conversas para análise de clientes
        if not shopify_orders.empty and not whatsapp_conversations.empty:
            # Criar um DataFrame combinado por cliente
            customers = pd.DataFrame({
                'customer': pd.concat([shopify_orders['customer'], whatsapp_conversations['customer']]).unique()
            })
            
            # Adicionar métricas de pedidos
            customer_orders = shopify_orders.groupby('customer').agg({
                'order_id': 'count',
                'value': 'sum'
            }).reset_index()
            customer_orders.columns = ['customer', 'order_count', 'total_spent']
            
            # Adicionar métricas de conversas
            customer_conversations = whatsapp_conversations.groupby('customer').agg({
                'conversation_id': 'count',
                'message_count': 'sum'
            }).reset_index()
            customer_conversations.columns = ['customer', 'conversation_count', 'message_count']
            
            # Mesclar os DataFrames
            customers = customers.merge(customer_orders, on='customer', how='left')
            customers = customers.merge(customer_conversations, on='customer', how='left')
            
            # Preencher valores NaN com 0
            customers = customers.fillna(0)
            
            # Calcular valor médio de pedido
            customers['avg_order_value'] = customers['total_spent'] / customers['order_count']
            customers['avg_order_value'] = customers['avg_order_value'].fillna(0)
            
            # Exibir tabela de clientes
            st.subheader("Lista de Clientes")
            st.dataframe(
                customers.rename(columns={
                    'customer': 'Cliente',
                    'order_count': 'Pedidos',
                    'total_spent': 'Total Gasto (R$)',
                    'avg_order_value': 'Valor Médio (R$)',
                    'conversation_count': 'Conversas',
                    'message_count': 'Mensagens'
                }),
                use_container_width=True
            )
            
            # Gráfico de clientes por valor gasto
            st.subheader("Clientes por Valor Gasto")
            fig = px.bar(
                customers.sort_values('total_spent', ascending=False).head(10),
                x='customer',
                y='total_spent',
                title="Top 10 Clientes por Valor Gasto",
                labels={"customer": "Cliente", "total_spent": "Total Gasto (R$)"},
                color='total_spent',
                color_continuous_scale=px.colors.sequential.Viridis
            )
            # Configurar o formato dos valores no eixo Y para usar vírgula como separador decimal
            fig.update_layout(
                yaxis=dict(tickformat=",.2f", tickprefix="R$ ")
            )
            # Configurar o hover para mostrar os valores no formato brasileiro
            fig.update_traces(
                hovertemplate="%{x}<br>Total Gasto: R$ %{y:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados suficientes para análise de clientes.")
    
    # Página: Conversas
    elif page == "Conversas":
        st.header("Histórico de Conversas")
        
        if not whatsapp_conversations.empty:
            # Filtros
            st.subheader("Filtros")
            col1, col2 = st.columns(2)
            
            with col1:
                min_date = whatsapp_conversations['timestamp'].min().date()
                max_date = whatsapp_conversations['timestamp'].max().date()
                date_range = st.date_input(
                    "Intervalo de Datas",
                    [min_date, max_date],
                    min_value=min_date,
                    max_value=max_date
                )
            
            with col2:
                status_filter = st.multiselect(
                    "Status da Conversa",
                    options=whatsapp_conversations['status'].unique(),
                    default=whatsapp_conversations['status'].unique()
                )
            
            # Aplicar filtros
            filtered_conversations = whatsapp_conversations.copy()
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_conversations = filtered_conversations[
                    (filtered_conversations['timestamp'].dt.date >= start_date) &
                    (filtered_conversations['timestamp'].dt.date <= end_date)
                ]
            
            if status_filter:
                filtered_conversations = filtered_conversations[filtered_conversations['status'].isin(status_filter)]
            
            # Tabela de conversas
            st.subheader("Lista de Conversas")
            st.dataframe(
                filtered_conversations[['conversation_id', 'customer', 'timestamp', 'message_count', 'status']].rename(columns={
                    'conversation_id': 'ID da Conversa',
                    'customer': 'Cliente',
                    'timestamp': 'Data e Hora',
                    'message_count': 'Mensagens',
                    'status': 'Status'
                }),
                use_container_width=True
            )
        else:
            st.info("Não há dados de conversas disponíveis.")
    
    # Página: Configurações
    elif page == "Configurações":
        st.header("Configurações do Sistema")
        
        # Criar abas para diferentes configurações
        tabs = st.tabs(["Shopify", "WhatsApp", "OpenAI", "Redis", "Status"])
        
        # Aba: Shopify
        with tabs[0]:
            st.subheader("Configurações do Shopify")
            
            # Formulário para configurações do Shopify
            with st.form("shopify_config_form"):
                shopify_shop_url = st.text_input(
                    "URL da Loja Shopify",
                    value=os.getenv("SHOPIFY_SHOP_URL", ""),
                    help="Ex: minhaloja.myshopify.com"
                )
                
                shopify_api_key = st.text_input(
                    "API Key do Shopify",
                    value=os.getenv("SHOPIFY_API_KEY", "")
                )
                
                shopify_api_secret = st.text_input(
                    "API Secret do Shopify",
                    value=os.getenv("SHOPIFY_API_SECRET", ""),
                    type="password"
                )
                
                shopify_access_token = st.text_input(
                    "Access Token do Shopify",
                    value=os.getenv("SHOPIFY_ACCESS_TOKEN", ""),
                    type="password"
                )
                
                shopify_submit = st.form_submit_button("Salvar Configurações do Shopify")
                
                if shopify_submit:
                    config_data = {
                        "SHOPIFY_SHOP_URL": shopify_shop_url,
                        "SHOPIFY_API_KEY": shopify_api_key,
                        "SHOPIFY_API_SECRET": shopify_api_secret,
                        "SHOPIFY_ACCESS_TOKEN": shopify_access_token
                    }
                    save_config("Shopify", config_data)
        
        # Aba: WhatsApp
        with tabs[1]:
            st.subheader("Configurações do WhatsApp")
            
            # Formulário para configurações do WhatsApp
            with st.form("whatsapp_config_form"):
                graph_api_token = st.text_input(
                    "Token da Graph API (Meta)",
                    value=os.getenv("GRAPH_API_TOKEN", ""),
                    type="password"
                )
                
                whatsapp_phone_number_id = st.text_input(
                    "ID do Número de Telefone do WhatsApp",
                    value=os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
                )
                
                whatsapp_business_account_id = st.text_input(
                    "ID da Conta Business do WhatsApp",
                    value=os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
                )
                
                webhook_verify_token = st.text_input(
                    "Token de Verificação do Webhook",
                    value=os.getenv("WEBHOOK_VERIFY_TOKEN", ""),
                    type="password"
                )
                
                whatsapp_submit = st.form_submit_button("Salvar Configurações do WhatsApp")
                
                if whatsapp_submit:
                    config_data = {
                        "GRAPH_API_TOKEN": graph_api_token,
                        "WHATSAPP_PHONE_NUMBER_ID": whatsapp_phone_number_id,
                        "WHATSAPP_BUSINESS_ACCOUNT_ID": whatsapp_business_account_id,
                        "WEBHOOK_VERIFY_TOKEN": webhook_verify_token
                    }
                    save_config("WhatsApp", config_data)
        
        # Aba: OpenAI
        with tabs[2]:
            st.subheader("Configurações da OpenAI")
            
            # Formulário para configurações da OpenAI
            with st.form("openai_config_form"):
                openai_api_key = st.text_input(
                    "API Key da OpenAI",
                    value=os.getenv("OPENAI_API_KEY", ""),
                    type="password"
                )
                
                openai_model = st.selectbox(
                    "Modelo da OpenAI",
                    options=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                    index=0 if os.getenv("OPENAI_MODEL") == "gpt-4" else 
                           1 if os.getenv("OPENAI_MODEL") == "gpt-4-turbo" else 2
                )
                
                openai_submit = st.form_submit_button("Salvar Configurações da OpenAI")
                
                if openai_submit:
                    config_data = {
                        "OPENAI_API_KEY": openai_api_key,
                        "OPENAI_MODEL": openai_model
                    }
                    save_config("OpenAI", config_data)
        
        # Aba: Redis
        with tabs[3]:
            st.subheader("Configurações do Redis")
            
            # Formulário para configurações do Redis
            with st.form("redis_config_form"):
                redis_url = st.text_input(
                    "URL do Redis",
                    value=os.getenv("REDIS_URL", "redis://localhost:6379")
                )
                
                redis_password = st.text_input(
                    "Senha do Redis",
                    value=os.getenv("REDIS_PASSWORD", ""),
                    type="password"
                )
                
                redis_submit = st.form_submit_button("Salvar Configurações do Redis")
                
                if redis_submit:
                    config_data = {
                        "REDIS_URL": redis_url,
                        "REDIS_PASSWORD": redis_password
                    }
                    save_config("Redis", config_data)
        
        # Aba: Status
        with tabs[4]:
            st.subheader("Status das Conexões")
            
            # Status do Redis
            redis_status = "✅ Conectado" if redis_client else "❌ Desconectado"
            st.info(f"Redis: {redis_status}")
            
            # Aqui você pode adicionar verificações para outras conexões
            # como Shopify API, WhatsApp API, etc.
            
            # Verificar conexão com Shopify (simulado)
            shopify_connected = os.getenv("SHOPIFY_ACCESS_TOKEN") is not None
            shopify_status = "✅ Conectado" if shopify_connected else "❌ Desconectado"
            st.info(f"Shopify API: {shopify_status}")
            
            # Verificar conexão com WhatsApp (simulado)
            whatsapp_connected = os.getenv("GRAPH_API_TOKEN") is not None
            whatsapp_status = "✅ Conectado" if whatsapp_connected else "❌ Desconectado"
            st.info(f"WhatsApp API: {whatsapp_status}")
            
            # Verificar conexão com OpenAI (simulado)
            openai_connected = os.getenv("OPENAI_API_KEY") is not None
            openai_status = "✅ Conectado" if openai_connected else "❌ Desconectado"
            st.info(f"OpenAI API: {openai_status}")

# Executar o aplicativo
if __name__ == "__main__":
    main()