from langchain_groq import ChatGroq

def get_llm():
    model=ChatGroq(
        model = "openai/gpt-oss-120b",
        api_key = "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",
    )
    return model

def get_structured_llm():
    model=ChatGroq(
        model = "meta-llama/llama-4-maverick-17b-128e-instruct",
        api_key = "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",
    )
    return model