# Grounding Facts: RAG (Retrieval-Augmented Generation)

1. RAG stands for Retrieval-Augmented Generation.
2. RAG combines two parts: a retriever that finds relevant information, and a large language model (LLM) that writes the answer.
3. RAG was introduced in a 2020 research paper by Patrick Lewis and colleagues at Facebook AI Research (now Meta AI).
4. LLMs are trained on data up to a fixed date, so they do not know about newer events, and they do not know a company's private documents.
5. LLMs can produce confident but false answers. This is called hallucination.
6. RAG reduces hallucination by giving the LLM relevant source text to base its answer on. It does not remove hallucination completely.
7. RAG does NOT retrain or change the LLM's weights. The retrieved text is added to the prompt at question time.
8. Typical RAG steps: (a) split documents into chunks, (b) convert chunks into embeddings (lists of numbers that capture meaning), (c) store them in a vector database, (d) when a user asks a question, convert the question to an embedding and retrieve the most similar chunks, (e) add those chunks to the prompt, (f) the LLM generates the answer.
9. Embeddings place text with similar meaning close together, which allows search by meaning and not only by exact words.
10. RAG makes it easy to update knowledge: add or change documents in the database, with no model retraining needed.
11. RAG can show sources, so users can verify where an answer came from.
12. Common uses: customer support bots, company document search, study assistants, legal and medical reference tools.