from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from app.prompt import prompt_template
from app.config import TEMPERATURE, GROQ_API_KEY

memory = ConversationBufferWindowMemory(
    k=5,
    memory_key="chat_history",
    return_messages=True
)

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-120b",
    temperature=TEMPERATURE,
    max_tokens=3000
)

llm_chain = LLMChain(
    llm=llm, 
    prompt=prompt_template,
    memory=memory
)

def get_llm_response(context: str) -> str:
    result = llm_chain.invoke({
        "context": context
    })

    return result.get("text") or result.get("output_text") or ""





































