# Keyword taxonomies

Load the taxonomy matching the **locked role variant** from intake. Mirror JD terminology; embed in bullets, not only skills.

## JD-mirror rules

1. **Exact terminology** — if JD says "Kubernetes", use "Kubernetes" (include "K8s" once: "Kubernetes (K8s)")
2. **Embed in bullets** — parsers and humans weight contextual usage higher
3. **Acronym + spelled form once** — "Retrieval-Augmented Generation (RAG)" on first use
4. **Priority = frequency** — repeated terms across similar JDs = priority
5. **Semantic synonyms** — ensure equivalent concepts appear (see synonym table)
6. **No stuffing** — unnatural density hurts modern systems and human review
7. **Required vs preferred** — required terms must appear; preferred if truthful
8. **Seniority language** — mirror staff/principal/lead as appropriate to scope

## Universal SWE

| Category | Terms |
|----------|-------|
| Languages | Python, Java, TypeScript, Go, Rust, C++, SQL |
| Architecture | System design, microservices, distributed systems, event-driven, API design |
| APIs | REST, GraphQL, gRPC, OpenAPI |
| Infra | Kubernetes, Docker, Terraform, CI/CD, AWS/GCP/Azure |
| Practices | Code review, technical leadership, mentoring, cross-team collaboration |
| Reliability | SLOs, observability, incident response, on-call |

## AI Engineer

| Category | Terms |
|----------|-------|
| Core | RAG, LLM, agents, prompt engineering, embeddings, vector databases |
| Frameworks | LangChain, LlamaIndex, FastAPI, OpenAI API, Anthropic API |
| Production | Evals, RAGAS, golden sets, guardrails, hallucination reduction |
| Infra | Pinecone, Weaviate, Chroma, Redis, model serving, batch inference |
| Differentiators | Production > fine-tuning; eval-gated releases; cost per query |
| Avoid over-indexing | Research papers, Kaggle, tutorial projects (unless JD asks) |

## ML Engineer

| Category | Terms |
|----------|-------|
| Frameworks | PyTorch, TensorFlow, scikit-learn, XGBoost |
| MLOps | MLflow, Kubeflow, feature stores, model registry, experiment tracking |
| Serving | Model serving (TorchServe, Triton, SageMaker), batch + real-time inference |
| Pipelines | Feature pipelines, ETL, data ingestion workflows, Airflow, Spark |
| Quality | Drift detection, A/B testing, model monitoring, data validation |
| Scale | Training at scale, distributed training, GPU optimization |

## Hybrid / Staff Platform

Platform engineering, developer experience, internal tools, multi-tenant, cost optimization, org-wide impact, technical strategy, architecture reviews, LLM infrastructure, inference optimization, agent workflows

## Semantic synonym reference

| JD term | Common alternates to include |
|---------|------------------------------|
| ETL pipelines | Data ingestion workflows, data pipelines |
| CI/CD | Continuous integration, automated deployment |
| Microservices | Distributed services, service-oriented architecture |
| RAG | Retrieval-augmented generation, knowledge retrieval |
| MLOps | ML operations, model lifecycle management |
| Observability | Monitoring, tracing, metrics, logging |
| Kubernetes | K8s, container orchestration |
