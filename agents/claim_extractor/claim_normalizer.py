from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from llm_config import llm

from pydantic import BaseModel, Field
from typing import Optional


class ExtractedClaim(BaseModel):
    subject: Optional[str] = Field(
        default=None,
        description="Main entity performing the action. Use lowercase, singular, snake_case."
    )
    predicate: Optional[str] = Field(
        default=None,
        description="Lemmatized verb describing the action, snake_case."
    )
    object: Optional[str] = Field(
        default=None,
        description="Value or entity affected by the action. Preserve numbers exactly."
    )
    time: Optional[str] = Field(
        default=None,
        description="Time reference if present (e.g. last_year, 2023, null if missing)."
    )
    location: Optional[str] = Field(
        default=None,
        description="Geographical location if present, lowercase snake_case."
    )
    source: Optional[str] = Field(
        default=None,
        description="Who made the claim (person or organization), snake_case."
    )

parser = PydanticOutputParser(pydantic_object=ExtractedClaim)
prompt = PromptTemplate(
    template=
"""
Extract a factual langchain_coreclaim into the following structured fields.

Rules:
- Do NOT paraphrase creatively
- Use lemmatized verbs
- Use snake_case
- Use null if information is missing
- Preserve numbers exactly
- Do NOT infer missing facts


Sentence:
"{sentence}"

{format_instructions}
""",
input_variables=['sentence'],
partial_variables={'format_instructions': parser.get_format_instructions()})


chain = prompt | llm | parser 

def norm(value):
    if value is None:
        return "null"
    if isinstance(value, str) and value.strip() == "":
        return "null"
    return value


def build_canonical_claim(fields: dict) -> str:
    return "|".join([
        norm(fields.get("subject", "null")),
        norm(fields.get("predicate", "null")),
        norm(fields.get("object", "null")),
        norm(fields.get("time", "null")),
        norm(fields.get("location", "null")),
        norm(fields.get("source", "null"))
    ])


def normalize_claim(sentence_record: dict) -> dict | None:
    if sentence_record.get("label") != "FACT_CLAIM":
        return None

    temp = chain.invoke(
        {"sentence": sentence_record["text"]}
    )

    canonical = build_canonical_claim(temp.model_dump())

    return {
        "canonical_claim": canonical,
        "sentence_id": sentence_record["sentence_id"],
        "paragraph_index": sentence_record["paragraph_index"],
        "original_sentence": sentence_record["text"]
    }
