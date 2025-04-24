#!/usr/bin/env python
import sys
from automacao_assistente_loja_shopify_whatsapp_crm_dashboard.crew import AutomacaoAssistenteLojaShopifyWhatsappCRMDashboardCrew

# This main file is intended to be a way for your to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'SHOPIFY_SHOP_URL': 'sample_value',
        'SHOPIFY_ACCESS_TOKEN': 'sample_value',
        'SHOPIFY_API_KEY': 'sample_value',
        'SHOPIFY_API_SECRET': 'sample_value'
    }
    AutomacaoAssistenteLojaShopifyWhatsappCRMDashboardCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'SHOPIFY_SHOP_URL': 'sample_value',
        'SHOPIFY_ACCESS_TOKEN': 'sample_value',
        'SHOPIFY_API_KEY': 'sample_value',
        'SHOPIFY_API_SECRET': 'sample_value'
    }
    try:
        AutomacaoAssistenteLojaShopifyWhatsappCRMDashboardCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        AutomacaoAssistenteLojaShopifyWhatsappCRMDashboardCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'SHOPIFY_SHOP_URL': 'sample_value',
        'SHOPIFY_ACCESS_TOKEN': 'sample_value',
        'SHOPIFY_API_KEY': 'sample_value',
        'SHOPIFY_API_SECRET': 'sample_value'
    }
    try:
        AutomacaoAssistenteLojaShopifyWhatsappCRMDashboardCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
