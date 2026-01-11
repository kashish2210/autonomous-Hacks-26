# Credible

**Credible** is an autonomous, AI-powered system that extracts, normalizes, and verifies factual claims from news articles, TV scripts, and long-form content—bringing transparency, traceability, and scalability to modern fact-checking.

---

## Problem Statement

The modern news ecosystem produces information at a scale and speed that makes manual verification impractical. News articles and TV reports often contain dozens of factual claims, many of which are inconsistently reported, selectively framed, or left unchecked. Existing fact-checking approaches focus on article-level verdicts and operate reactively, offering limited transparency and poor scalability. This allows misinformation, contradictions, and biased narratives to spread before corrections can be issued, undermining public trust in media.

---

## Solution Overview

Credible addresses this challenge by transforming unstructured news content into **structured, verifiable claims**. Instead of treating an article as a single unit, the system breaks it down into sentence-level factual claims and converts each claim into a canonical representation. This enables identical facts expressed differently to be recognized as the same claim, allowing deduplication, contradiction detection, and independent verification.

Each claim is evaluated against external information sources to determine whether it is **supported, contradicted, or unverifiable**, while maintaining a direct link to the original text for full explainability.

---

## Autonomous / Agentic Architecture

Credible is built as a **multi-agent autonomous system**, where each agent performs a specialized role:

- **Text Segmentation Agent** – Cleans and segments raw news text into sentences with contextual metadata.
- **Claim Detection Agent** – Identifies verifiable factual claims while filtering opinions and narrative text.
- **Claim Normalization Agent** – Converts claims into a consistent, structured canonical format.
- **Verification Agent** – Retrieves external evidence and evaluates claim validity.
- **Aggregation Agent** – Maintains a global claim store for deduplication and comparison.

Agents communicate via structured outputs, enabling independent operation, fault isolation, and easy extensibility.

---

## Why Credible Is Innovative & Unique

Credible shifts fact-checking from **article-level labeling to claim-level intelligence**, enabling precision verification and accountability. Its canonical claim normalization allows detection of duplicate facts and contradictions across differently worded sources—something traditional semantic or keyword-based systems cannot reliably achieve.

The agent-based design mirrors newsroom workflows at machine scale, allowing continuous, low-intervention operation. Unlike black-box fact-checkers, Credible is fully traceable: every decision links back to the original sentence and supporting evidence.

Most importantly, Credible is built as an **infrastructure layer**, capable of powering newsrooms, research platforms, browser extensions, or content moderation systems.

---

## Target Users

- Journalists and newsroom editors  
- Fact-checking organizations  
- Media researchers and watchdogs  
- Policy analysts and regulators  
- Platforms combating misinformation  

---

## Scope

### In Scope
- Claim extraction and normalization  
- Claim-level verification using external sources  
- Traceability to original text  
- Deduplication and contradiction readiness  

### Out of Scope
- Final human editorial judgment  
- Political intent attribution  
- Real-time social media moderation at platform scale  

---

## Key Features

- Claim-level extraction and verification  
- Canonical claim normalization  
- Explainable, traceable outputs  
- Autonomous multi-agent pipeline  
- Scalable verification workflow  

---

## Current Progress

### Phase 1 – Completed
- Text preprocessing and sentence segmentation  
- Sentence-level claim classification  

### Phase 2 – Completed
- Structured claim extraction  
- Canonical claim normalization  
- Global claim storage design  

---

## Major Challenges

- LLM output consistency and schema enforcement  
- Canonicalization ambiguity across phrasing  
- Scalability of per-claim verification  
- External data source reliability  

---

## Post-Hackathon Roadmap (30–60 Days)

- Claim deduplication and contradiction detection  
- Bias and framing analysis  
- Evidence confidence scoring  
- UI dashboard for journalists  
- Source credibility weighting  

---

**Credible** lays the foundation for a transparent, scalable, and explainable fact-checking ecosystem—turning raw news into structured, verifiable truth.
