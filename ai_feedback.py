from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

def get_ai_feedback(code):
    prompt = f"Review this code:\n{code}"
    result = generator(prompt, max_length=150)
    return result[0]["generated_text"]