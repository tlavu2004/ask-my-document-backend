import os
import requests
from langchain.llms import CTransformers
from transformers import AutoTokenizer

PROMPT_TEMPLATE = (
    "Use ONLY the context below to answer the user's question.\n"
    "If the answer is not in the context, reply \"I don't know\".\n"
    "Do not repeat this instruction.\n"
    "Context:\n{context}\n"
    "Question: {question}\n"
    "Helpful answer:"
)

class HuggingFaceLLM:
    def __init__(self, model="deepset/roberta-base-squad2"):
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
        self.token = os.getenv("HF_TOKEN")
        if not self.token:
            raise RuntimeError("HF_TOKEN environment variable not set.")

    def generate(self, question: str, context_docs: list[str]) -> str:
        headers = {"Authorization": f"Bearer {self.token}"}
        context_text = "\n".join(context_docs)
        payload = {
            "inputs": {
                "question": question,
                "context": context_text
            }
        } 
        response = requests.post(self.api_url, headers=headers, json=payload)
        try:
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            return f"[HF ERROR] {str(e)} | Raw response: {response.text}"

        if isinstance(result, dict) and "answer" in result:
            return result["answer"]
        elif isinstance(result, dict) and "error" in result:
            return f"[HF ERROR] {result['error']}"
        else:
            return str(result)

class LocalLLM:
    def __init__(self, model_path="models/llama-2-7b-chat.ggmlv3.q4_1.bin"):
        self.llm = CTransformers(
            model=model_path,
            model_type="llama",
            config={
                "max_new_tokens": 256,
                "temperature": 0.01
            }
        )

    def generate(self, question: str, context_docs: list[str]) -> str:
        context_text = truncate_context(context_docs, question, max_tokens=512)
        prompt = PROMPT_TEMPLATE.format(context=context_text, question=question)
        raw_answer = self.llm(prompt)
        return clean_llm_answer(raw_answer)

tokenizer = AutoTokenizer.from_pretrained("hf-internal-testing/llama-tokenizer")

def truncate_context(context_docs, question, max_tokens=512):
    context = ""
    for doc in context_docs:
        temp_context = context + doc + "\n"

        # Just count the tokens for the context part, do not concatenate the template
        num_tokens = len(tokenizer.encode(temp_context + question))
        if num_tokens > max_tokens:
            break
        context = temp_context
    return context

def clean_llm_answer(answer: str) -> str:
    answer = answer.strip()

    # Change "Unhelpful answers:" by "Additional information:"
    unhelpful_idx = answer.lower().find("unhelpful answers:")
    if unhelpful_idx != -1:
        answer = answer[:unhelpful_idx].strip() + "\nAdditional information: " + answer[unhelpful_idx + len("unhelpful answers:"):].strip()

    if answer.lower().endswith("i don't know.") or answer.lower().endswith("i don't know"):
        # If there is a period before, cut to the last period
        last_dot = answer[:-12].rfind(".")
        if last_dot != -1:
            return answer[:last_dot+1].strip()

        # If the front is an answer, cut "I don't know"
        return answer[:-12].strip()
    return answer

def get_default_llm():
    return LocalLLM()
