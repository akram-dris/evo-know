import os
import ollama
import sys

def test_ollama_connectivity():
    ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
    
    print(f"🔍 Testing connectivity to Ollama at: {ollama_host}")
    print(f"🤖 Target model: {ollama_model}")
    
    client = ollama.Client(base_url=ollama_host)
    
    try:
        print("⏳ Listing models available in Ollama...")
        models = client.list()
        model_names = [m['name'] for m in models.get('models', [])]
        print(f"✅ Models found: {model_names}")
        
        if ollama_model not in [m.split(':')[0] for m in model_names] and ollama_model not in model_names:
            print(f"⚠️ Warning: '{ollama_model}' not found in Ollama. Please run 'ollama pull {ollama_model}'")
        
        print(f"⏳ Generating a test response using '{ollama_model}'...")
        response = client.generate(
            model=ollama_model,
            prompt="Say 'Ollama is linked successfully!' in French."
        )
        print("--- OLLAMA RESPONSE ---")
        print(response.get('response'))
        print("--- END RESPONSE ---")
        print("🚀 SUCCESS: Ollama is correctly linked and responding!")
        
    except Exception as e:
        print(f"❌ ERROR: Failed to connect or generate response from Ollama: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_ollama_connectivity()
