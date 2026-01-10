from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_config import llm
from dotenv import load_dotenv

load_dotenv()

prompt = ChatPromptTemplate.from_template("""
You are classifying sentences from a news article.

Label the sentence as ONE of:
- FACT_CLAIM (verifiable factual statement)
- OPINION (judgment, belief, recommendation)
- EMOTIONAL (sensational or emotionally loaded)
- CONTEXT (background or descriptive info)
- STRUCTURAL (BREAKING, UPDATE, headline marker)

Sentence:
"{sentence}"

Return ONLY the label.
""")

chain = prompt | llm | StrOutputParser()


def classify_sentence(sentence_record: dict) -> dict:
    label = chain.invoke({"sentence": sentence_record["text"]})
    sentence_record["label"] = label.strip()
    return sentence_record
