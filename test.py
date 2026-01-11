import google.generativeai as genai

# Configure API
genai.configure(api_key='AIzaSyAxaQ9iUke4CkEJg4kqefnyzWcxRdatKog')

# List all available models
print("📋 Available models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
    print(f"   Supported methods: {model.supported_generation_methods}")
    print("---")