---
title: Agents
type: concept
status: draft
created: 2026-05-28
updated: 2026-05-28
sources:
  - llm-wiki-gist
  - public-karpathy-corpus
  - karpathy-wiki-operating-schema
tags:
  - agents
  - memory
  - workflows
aliases:
  - AI Agents
  - LLM Agents
related:
  - llm-wiki.md
  - education.md
confidence: low
---

# Agents

This page tracks the agentic workflows relevant to the wiki itself: ingest, query, feedback, and lint. (source: `llm-wiki-gist`)

## Source-Backed Claims

- The LLM Wiki gist source describes a persistent markdown wiki knowledge base maintained by an agent. (source: `llm-wiki-gist`)
- The public source map is the starting corpus record used by this agent-maintained wiki. (source: `public-karpathy-corpus`)
- This project uses Cognee for durable memory and filesystem-backed Cognee session events for run-local observations. (source: `karpathy-wiki-operating-schema`)

## Wiki-Relevant Agent Pattern

For this project, the agent is not only a chatbot. It is a maintainer that:

- reads sources
- extracts durable claims
- updates pages
- records its actions
- accepts feedback
- runs lint passes

## Cognee Role

Cognee stores durable memory about entities, concepts, claims, source summaries, and feedback. The local filesystem cache stores temporary session memory during each run. (source: `karpathy-wiki-operating-schema`)

## Open Questions

- Which Karpathy public talks or posts should anchor an agents-focused page?
- How should this wiki distinguish tool-using agents from wiki-maintaining agents?
