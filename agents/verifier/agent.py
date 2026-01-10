# claim_verifier_agent.py
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda

from agents.claim_extractor.llm_config import llm
from .search_tool import search
from .claim_query_builder import claim_to_search_queries
from .claim_verifier_schema import VerificationResult

from langchain_core.prompts import PromptTemplate

VERIFIER_PROMPT = PromptTemplate(
    template="""
You are a professional fact-checker.

Claim:
"{claim}"

Search Evidence:
{evidence}

Rules:
- Use ONLY the provided evidence
- If evidence clearly supports claim → VERIFIED
- If evidence contradicts claim → FALSE
- If evidence partially supports → PARTIALLY_VERIFIED
- If insufficient or unclear → UNVERIFIABLE
- Do NOT infer or guess

Return output strictly in the required JSON format.
{format_instructions}
""",
    input_variables=["claim", "evidence", "format_instructions"]
)

parser = PydanticOutputParser(pydantic_object=VerificationResult)


def verify_claim(canonical_claim: str) -> VerificationResult:
    queries = claim_to_search_queries(canonical_claim)

    search_results = []
    sources = []

    for q in queries:
        result = search.run(q)
        search_results.append(result)

    combined_evidence = "\n\n".join(search_results)

    chain = (
        VERIFIER_PROMPT
        | llm
        | parser
    )

    return chain.invoke({
        "claim": canonical_claim,
        "evidence": combined_evidence,
        "format_instructions": parser.get_format_instructions()
    })
