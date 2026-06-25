# ML/AI — Machine Learning & Artificial Intelligence

Learned knowledge about ML/DL systems, techniques, and when/how to apply them.
Companion-readable reference for JARVIS to reason about these systems.

---

## Core Concepts

### What ML actually is
ML = pattern recognition from data. Not magic, not reasoning. You show a system
many examples of something (inputs + desired outputs), and it learns a function
that maps new inputs to outputs. The function is learned, not programmed.

- **Supervised learning:** labeled data (input → correct output). Classification,
  regression, named entity recognition.
- **Unsupervised learning:** unlabeled data. Clustering, dimensionality reduction,
  anomaly detection.
- **Reinforcement learning:** learn from rewards/penalties through interaction.
  Agents, game AI, recommendation systems.
- **Generative:** learn the distribution of data to create new examples.
  GANs, diffusion models, language models.

### Deep Learning vs Classical ML
Classical ML: hand-crafted features + traditional algorithms (SVM, random forests,
logistic regression). Works well when you can define good features.

Deep Learning: learned features + neural networks. Works well when:
- Raw/unstructured data (images, audio, text)
- Feature engineering is hard or unknown
- Scale is available (more data = better)

For JARVIS/JARVIS-Private: most needs are classical ML or simple DL. Start simple.

### When to use ML
Use ML when:
- Rule-based logic is too brittle/unmaintainable
- Patterns are too complex for explicit rules
- Scale makes hand-labeling impossible

Don't use ML when:
- Simple rules work fine
- Data is scarce
- Interpretability is required (legal, safety)
- One-off problem

---

## Practical Techniques

### Vector Embeddings (most useful for JARVIS)
Embeddings = dense vectors that represent meaning. Text → numbers that capture
semantic relationships. "cat" and "kitten" are close in embedding space.

Use cases in JARVIS:
- **Semantic search:** find related content by meaning, not keywords
- **Similarity:** cluster related memories, detect duplicates
- **RAG (Retrieval-Augmented Generation):** fetch relevant context for LLM prompts
- **Recommendation:** suggest related projects, past decisions, relevant knowledge

Tools: OpenAI embeddings (ada-002, text-embedding-3), sentence-transformers
(local, open-source), Supabase pgvector (store + search embeddings).

### Classification
Assign a label to input. Binary (spam/not spam) or multi-class (topic, sentiment).

Tools: scikit-learn (fast, classical), transformers library (deep learning).

### Clustering
Group similar items without labels. K-means, hierarchical, DBSCAN.

Use: organize memories, group projects, find patterns in session logs.

### Time-Series
Predict future values, detect anomalies, find patterns over time.

Tools: statsmodels, Prophet (Facebook), Neural Prophet.

JARVIS use case: MNEMOS growth rate, memory compression timing.

### Fine-tuning
Adapt a pre-trained model to specific data. Cheaper than training from scratch,
better than prompting alone for specialized tasks.

- **LoRA / QLoRA:** fine-tune large models with few parameters (memory efficient)
- **RLHF:** reinforcement learning from human feedback (how ChatGPT was aligned)
- **DPO:** direct preference optimization (simpler than RLHF)

### RAG — Retrieval-Augmented Generation
LLM consults a knowledge base before answering. Best practice: don't rely on
model memory when you can ground in real data.

Flow: query → embed → similarity search → retrieve context → LLM prompt with context

### Agents
LLM that can use tools, take actions, loop on feedback.

Key components:
- **Tool use:** LLM calls external functions/APIs
- **Memory:** retains context across turns (short-term) and sessions (long-term)
- **Planning:** breaks tasks into steps, revises on failure
- **Orchestration:** multiple agents working together (this is what JARVIS's
  God Systems are — specialized agents with defined roles)

### Prompt Engineering
Getting good outputs from LLMs through how you ask.

- Be specific and direct
- Give examples (few-shot)
- Chain-of-thought: ask for reasoning steps
- System prompt sets persona/instructions
- Temperature = creativity (0 = deterministic, 1 = chaotic)

---

## Tools & Stack

### Data
- **pandas:** data manipulation, cleaning, analysis
- **numpy:** numerical computing
- **scikit-learn:** classical ML algorithms
- **transformers:** Hugging Face, deep learning, pre-trained models

### Embeddings
- **OpenAI API:** embed-text (ada, 3-small, 3-large)
- **sentence-transformers:** open-source local embeddings
- **pgvector:** PostgreSQL extension for vector storage/search
- **Supabase:** already in stack — has pgvector built in

### Training
- **PyTorch:** flexible, research-grade deep learning
- **JAX:** Google, fast, functional
- **Keras:** high-level, beginner-friendly
- **Google Colab:** free GPU for experimentation

### MLOps
- **MLflow:** experiment tracking, model registry
- **Weights & Biases:** experiment tracking, collaboration
- **Ray:** distributed training, RL

---

## JARVIS-Specific Applications

### MNEMOS Vector Store
Currently: JSON + JSONL flat files. Could evolve to:
- Embeddings of all memories → semantic search across the knowledge base
- Similarity clustering to find duplicate/redundant memories
- Predict which memories to compress/prune based on access patterns

### The Grid
- Node recommendation: what content to surface to which user
- Semantic routing: understand what a user needs and direct them
- Generative: help users create within the Grid (music, game elements, code)

### PachinkoBounce / Game AI
- Difficulty tuning: learn player skill and adjust
- Procedural generation: create levels, patterns, enemy behaviors
- NPC behavior: believable, non-scripted game characters

### MusicOS / MonsterOS
- Pattern recognition in music (genre, mood, BPM from audio)
- Style transfer: generate in the style of existing tracks
- Monster behavior: learning-based game agents

---

## Anti-Patterns

- **Overengineering:** don't use a neural network when logistic regression works
- **Data leakage:** test data sneaking into training — always split first
- **Metric gaming:** optimizing accuracy but missing the real goal
- **Black box obsession:** use interpretable models where decisions matter
- **Cold-start:** new users/items with no data need special handling

---

## Key Principle for Raven
ML is a tool for when rules break down. Start simple, measure, iterate.
For JARVIS's architecture — the God Systems are already doing agentic ML:
each one learns patterns in its domain and routes/acts accordingly.
SKADI does compression, MNEMOS does recall, HUGINN does synthesis.
That's not classical ML, but it's ML thinking applied to the right problem.
