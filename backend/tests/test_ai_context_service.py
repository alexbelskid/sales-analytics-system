import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure backend is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.ai_context_service import AIContextService

@patch('app.services.ai_context_service.OpenAI')
@patch('app.services.ai_context_service.settings')
def test_extract_entities_with_llm(mock_settings, mock_openai_class):
    # Setup mocks
    mock_settings.groq_api_key = "fake_groq_key"
    mock_settings.openai_api_key = "fake_openai_key"

    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"customer_name": "Acme Corp", "product_name": "Widgets", "agent_name": null}'))
    ]
    mock_client.chat.completions.create.return_value = mock_response

    # Test execution
    email_body = "Hello, I am interested in buying Widgets from Acme Corp."
    result = AIContextService._extract_entities_with_llm(email_body)

    # Assertions
    assert result['customer_name'] == "Acme Corp"
    assert result['product_name'] == "Widgets"
    assert result['agent_name'] is None

    mock_client.chat.completions.create.assert_called_once()
    args, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs['model'] == "llama-3.3-70b-versatile"
    assert "Extract the following entities" in kwargs['messages'][1]['content']

@patch('app.services.ai_context_service.AIContextService._extract_entities_with_llm')
@patch('app.services.ai_context_service.AIContextService.get_context_for_ai')
def test_build_prompt_context(mock_get_context, mock_extract):
    # Setup mocks
    mock_extract.return_value = {
        'customer_name': 'Test Customer',
        'product_name': 'Test Product',
        'agent_name': 'Test Agent'
    }
    mock_get_context.return_value = "Context String"

    # Test execution
    email_body = "Email body"
    result = AIContextService.build_prompt_context(email_body)

    # Assertions
    assert result == "Context String"
    mock_extract.assert_called_once_with(email_body)
    mock_get_context.assert_called_once_with(
        customer_name='Test Customer',
        product_name='Test Product',
        agent_name='Test Agent',
        include_general=True
    )
