import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import redis
import json
import os
import datetime
from dotenv import load_dotenv

# Função para conectar ao Redis
def connect_to_redis():
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_password = os.getenv("REDIS_PASSWORD", "")
        
        r = redis.from_url(redis_url, password=redis_password)
        return r
    except Exception as e:
        st.error(f"Erro ao conectar ao Redis: {e}")
        return None

# Função para carregar dados do CRM do Redis
def load_crm_data(redis_client):
    if not redis_client:
        return pd.DataFrame()
    
    try:
        # Buscar todas as chaves de interações no Redis
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
            {"order_id": "1001", "customer": "João Silva", "value": 150.0, "date": "2023-06-01", "status": "Entregue"},
            {"order_id": "1002", "customer": "Maria Oliveira", "value": 89.90, "date": "2023-06-02", "status": "Processando"},
            {"order_id": "1003", "customer": "Pedro Santos", "value": 210.50, "date": "2023-06-03", "status": "Enviado"},
            {"order_id": "1004", "customer": "Ana Costa", "value": 75.0, "date": "2023-06-04", "status": "Entregue"},
            {"order_id": "1005", "customer": "Carlos Ferreira", "value": 320.0, "date": "2023-06-05", "status": "Processando"},
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

# Função principal
def main():
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configuração da página
    st.set_page_config(
        page_title="Shopify CRM WhatsApp Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Título do dashboard
    st.title("📊 Shopify CRM WhatsApp Dashboard")
    
    # Sidebar para navegação
    st.sidebar.title("Navegação")
    page = st.sidebar.radio(
        "Selecione uma página:",
        ["Visão Geral", "Vendas", "Clientes", "Conversas", "Configurações"]
    )
    
    # Conectar ao Redis
    redis_client = connect_to_redis()
    
    # Carregar dados
    crm_data = load_crm_data(redis_client)
    shopify_orders = load_shopify_orders()
    whatsapp_conversations = load_whatsapp_conversations()
    
    # Página: Visão Geral
    if page == "Visão Geral":
        st.header("Visão Geral do Sistema")
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Pedidos", len(shopify_orders))
        
        with col2:
            total_revenue = shopify_orders['value'].sum() if not shopify_orders.empty else 0
            st.metric("Receita Total", f"R$ {total_revenue:.2f}")
        
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
            fig = px.bar(
                shopify_orders.groupby(shopify_orders['date'].dt.date).sum().reset_index(),
                x='date',
                y='value',
                title="Vendas Diárias",
                labels={"date": "Data", "value": "Valor (R$)"},
                color_discrete_sequence=["#0083B8"]
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
    
    # Página: Vendas
    elif page == "Vendas":
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
                st.metric("Receita Total", f"R$ {total_revenue:.2f}")
            
            with col3:
                avg_order_value = total_revenue / len(filtered_orders) if len(filtered_orders) > 0 else 0
                st.metric("Valor Médio do Pedido", f"R$ {avg_order_value:.2f}")
            
            # Gráficos de vendas
            st.subheader("Gráficos de Vendas")
            
            # Vendas por status
            status_data = filtered_orders.groupby('status').agg(
                {'order_id': 'count', 'value': 'sum'}
            ).reset_index()
            status_data.columns = ['Status', 'Quantidade', 'Valor Total']
            
            fig = px.bar(
                status_data,
                x='Status',
                y='Valor Total',
                title="Vendas por Status",
                text='Quantidade',
                color='Status',
                labels={"Status": "Status do Pedido", "Valor Total": "Valor Total (R$)"},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)
            
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
            st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico de clientes por número de pedidos
            st.subheader("Clientes por Número de Pedidos")
            fig = px.bar(
                customers.sort_values('order_count', ascending=False).head(10),
                x='customer',
                y='order_count',
                title="Top 10 Clientes por Número de Pedidos",
                labels={"customer": "Cliente", "order_count": "Número de Pedidos"},
                color='order_count',
                color_continuous_scale=px.colors.sequential.Plasma
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
            
            # Métricas de conversas
            st.subheader("Métricas de Conversas")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Conversas", len(filtered_conversations))
            
            with col2:
                total_messages = filtered_conversations['message_count'].sum()
                st.metric("Total de Mensagens", total_messages)
            
            with col3:
                resolved = len(filtered_conversations[filtered_conversations['status'] == 'Resolvido'])
                resolution_rate = (resolved / len(filtered_conversations) * 100) if len(filtered_conversations) > 0 else 0
                st.metric("Taxa de Resolução", f"{resolution_rate:.1f}%")
            
            # Gráficos de conversas
            st.subheader("Gráficos de Conversas")
            
            # Conversas por status
            status_data = filtered_conversations['status'].value_counts().reset_index()
            status_data.columns = ['Status', 'Contagem']
            
            fig = px.pie(
                status_data,
                values='Contagem',
                names='Status',
                title="Distribuição de Status das Conversas",
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            st.plotly_chart(fig, use_container_width=True)
            
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
        
        # Exibir configurações atuais
        st.subheader("Configurações Atuais")
        
        # Shopify
        st.write("### Configurações do Shopify")
        shopify_config = {
            "SHOPIFY_SHOP_URL": os.getenv("SHOPIFY_SHOP_URL", "Não configurado"),
            "SHOPIFY_API_KEY": os.getenv("SHOPIFY_API_KEY", "Não configurado"),
            "SHOPIFY_API_SECRET": "*****" if os.getenv("SHOPIFY_API_SECRET") else "Não configurado",
            "SHOPIFY_ACCESS_TOKEN": "*****" if os.getenv("SHOPIFY_ACCESS_TOKEN") else "Não configurado"
        }
        
        shopify_df = pd.DataFrame({
            "Configuração": shopify_config.keys(),
            "Valor": shopify_config.values()
        })
        st.table(shopify_df)
        
        # WhatsApp
        st.write("### Configurações do WhatsApp")
        whatsapp_config = {
            "GRAPH_API_TOKEN": "*****" if os.getenv("GRAPH_API_TOKEN") else "Não configurado",
            "WHATSAPP_PHONE_NUMBER_ID": os.getenv("WHATSAPP_PHONE_NUMBER_ID", "Não configurado"),
            "WHATSAPP_BUSINESS_ACCOUNT_ID": os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "Não configurado"),
            "WEBHOOK_VERIFY_TOKEN": "*****" if os.getenv("WEBHOOK_VERIFY_TOKEN") else "Não configurado"
        }
        
        whatsapp_df = pd.DataFrame({
            "Configuração": whatsapp_config.keys(),
            "Valor": whatsapp_config.values()
        })
        st.table(whatsapp_df)
        
        # Redis
        st.write("### Configurações do Redis")
        redis_config = {
            "REDIS_URL": os.getenv("REDIS_URL", "Não configurado"),
            "REDIS_PASSWORD": "*****" if os.getenv("REDIS_PASSWORD") else "Não configurado"
        }
        
        redis_df = pd.DataFrame({
            "Configuração": redis_config.keys(),
            "Valor": redis_config.values()
        })
        st.table(redis_df)
        
        # Status da conexão
        st.subheader("Status das Conexões")
        col1, col2 = st.columns(2)
        
        with col1:
            redis_status = "✅ Conectado" if redis_client else "❌ Desconectado"
            st.info(f"Redis: {redis_status}")
        
        with col2:
            # Aqui você pode adicionar verificações para outras conexões
            # como Shopify API, WhatsApp API, etc.
            st.info("Shopify API: Status não verificado")
            st.info("WhatsApp API: Status não verificado")

# Executar o aplicativo
if __name__ == "__main__":
    main()