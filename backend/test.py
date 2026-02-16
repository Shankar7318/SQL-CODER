import ollama
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test different hosts
hosts = [
    'http://localhost:11434',
    'http://127.0.0.1:11434',
    'http://0.0.0.0:11434'
]

for host in hosts:
    try:
        print(f"\nTesting connection to {host}...")
        client = ollama.Client(host=host)
        models = client.list()
        print(f"✅ Success! Connected to {host}")
        print(f"Available models: {models}")
        break
    except Exception as e:
        print(f"❌ Failed to connect to {host}: {str(e)}")