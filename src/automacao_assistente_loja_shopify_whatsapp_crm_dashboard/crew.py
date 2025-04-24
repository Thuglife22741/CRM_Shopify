from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class AutomacaoAssistenteLojaShopifyWhatsappCRMDashboardCrew():
    """AutomacaoAssistenteLojaShopifyWhatsappCRMDashboard crew"""

    @agent
    def WhatsAppMessaging(self) -> Agent:
        return Agent(
            config=self.agents_config['WhatsAppMessaging'],
            tools=[],
        )

    @agent
    def ShopifyIntegration(self) -> Agent:
        return Agent(
            config=self.agents_config['ShopifyIntegration'],
            tools=[],
        )

    @agent
    def OpenAIAssistant(self) -> Agent:
        return Agent(
            config=self.agents_config['OpenAIAssistant'],
            tools=[],
        )

    @agent
    def CRMLogger(self) -> Agent:
        return Agent(
            config=self.agents_config['CRMLogger'],
            tools=[],
        )


    @task
    def interpret_customer_query_task(self) -> Task:
        return Task(
            config=self.tasks_config['interpret_customer_query_task'],
            tools=[],
        )

    @task
    def shopify_order_lookup_task(self) -> Task:
        return Task(
            config=self.tasks_config['shopify_order_lookup_task'],
            tools=[],
        )

    @task
    def shopify_product_lookup_task(self) -> Task:
        return Task(
            config=self.tasks_config['shopify_product_lookup_task'],
            tools=[],
        )

    @task
    def generate_response_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_response_task'],
            tools=[],
        )

    @task
    def send_whatsapp_response_task(self) -> Task:
        return Task(
            config=self.tasks_config['send_whatsapp_response_task'],
            tools=[],
        )

    @task
    def log_interaction_task(self) -> Task:
        return Task(
            config=self.tasks_config['log_interaction_task'],
            tools=[],
        )


    @crew
    def crew(self) -> Crew:
        """Creates the AutomacaoAssistenteLojaShopifyWhatsappCRMDashboard crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
