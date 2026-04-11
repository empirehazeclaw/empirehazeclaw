"""
Unified Model Config for EmpireHazeClaw
Central place for all model configurations

Usage:
  from model_config import get_model_config, get_fallback_chain
  
  config = get_model_config('llm_outreach')
  models = get_fallback_chain()
"""
import os

# Primary Model (MiniMax)
PRIMARY_MODEL = os.getenv('PRIMARY_MODEL', 'minimax/MiniMax-M2.7')

# Fallback chain (in order of preference)
FALLBACK_CHAIN = [
    'minimax/MiniMax-M2.7',
    'openai/gpt-4o-mini',
    'qwen/qwen3-next-80b-a3b-instruct:free',
    'qwen/qwen3-coder:free',
]

# Task-specific models
TASK_MODELS = {
    'coding': 'qwen/qwen3-coder:free',
    'reasoning': 'liquid/lfm-2.5-1.2b-thinking:free',
    'general': 'qwen/qwen3-next-80b-a3b-instruct:free',
    'fast': 'google/gemma-3-4b-it:free',
    'transcription': 'whisper',  # Local Whisper
}

# API Keys (from environment)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY', '')

def get_model_config(task='general'):
    """Get model config for specific task"""
    model_id = TASK_MODELS.get(task, PRIMARY_MODEL)
    return {
        'model': model_id,
        'api_key': get_api_key_for_model(model_id),
        'api_base': get_api_base_for_model(model_id),
    }

def get_api_key_for_model(model_id):
    """Get appropriate API key for model"""
    if 'openrouter' in model_id:
        return OPENROUTER_API_KEY
    elif 'openai' in model_id:
        return OPENAI_API_KEY
    elif 'minimax' in model_id:
        return MINIMAX_API_KEY
    return ''

def get_api_base_for_model(model_id):
    """Get API base URL for model"""
    if 'openrouter' in model_id:
        return 'https://openrouter.ai/api/v1'
    elif 'openai' in model_id:
        return 'https://api.openai.com/v1'
    elif 'minimax' in model_id:
        return 'https://api.minimax.io/anthropic/v1'
    return ''

def get_fallback_chain():
    """Get the fallback model chain"""
    return FALLBACK_CHAIN
