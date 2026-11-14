# Introduction to RAG (Retrieval-Augmented Generation)

RAG retrains the model's weights every time you ask a question, using vector embeddings and cosine similarity.


### 1. What is it?

RAG helps computer programs give better answers by finding information first. RAG stands for Retrieval-Augmented Generation.

*   **Retrieval** means finding or getting something. Here, it means finding useful information.
*   **Augmented** means made better or improved by adding something.
*   **Generation** means creating something new, like text.

So, RAG is a method that makes computer-generated answers better by first finding relevant information. It combines two main parts: a "retriever" that finds information, and a "Large Language Model" (LLM) that writes the answer.

A **Large Language Model (LLM)** is a special computer program. It can understand and write human-like text. Think of it like a very smart chatbot.

### 2. Why does it matter?

Large Language Models are very powerful, but they have some problems. RAG helps to solve these problems.

*   **Old Information:** LLMs learn from a lot of text data. But this data is only up to a certain date. So, LLMs do not know about new events. They also do not know about private documents, like a company's internal reports.
*   **Making up Answers (Hallucination):** Sometimes, an LLM can give an answer that sounds very confident, but it is actually false. This problem is called **hallucination**. It means the LLM makes up information.
*   **No Sources:** LLMs usually do not tell you where their information came from. This makes it hard to check if their answers are true.

RAG helps with these issues:

*   **Reduces Hallucination:** RAG gives the LLM specific, correct information to use. The LLM then bases its answer on this information. This makes the LLM less likely to make up false answers. It does not remove all hallucination, but it helps a lot.
*   **Uses New and Private Information:** RAG can access the latest news or a company's private documents. It finds this information and gives it to the LLM. This way, the LLM can answer questions about things it was not originally trained on.
*   **Easy to Update:** If new information comes out, or if company documents change, RAG can use these updates easily. You just add or change the documents in RAG's storage. You do not need to retrain the entire LLM, which is a very long and costly process.
*   **Shows Sources:** RAG can often show you where it found the information. This means you can check the sources yourself. You can verify if the answer is accurate.

### 3. How does it work?

Let's understand the steps of RAG:

1.  **Prepare Documents:** First, you gather all the documents you want RAG to use. These could be books, articles, company reports, or web pages.
2.  **Split into Chunks:** These large **documents** (files with text) are too big to use all at once. So, they are broken down into smaller pieces. These small pieces are called **chunks**. Each chunk is like a paragraph or a few sentences.
3.  **Convert to Embeddings:** Each chunk of text is then turned into a list of numbers. These special lists of numbers are called **embeddings**. Embeddings capture the meaning of the text. If two pieces of text have similar meanings, their embeddings (number lists) will be very similar. This allows computers to search for meaning, not just exact words.
4.  **Store in a Vector Database:** These embeddings (number lists) are stored in a special place called a **vector database**. A **database** is like an organized library or file cabinet for information. A **vector database** is designed to store these number lists and quickly find other lists that are very similar.
5.  **User Asks a Question:** When a user asks a question, like "What are the rules for college leave?", this question is also converted into an embedding (a list of numbers).
6.  **Retrieve Similar Chunks:** RAG then uses this question's embedding to search the vector database. It finds the chunks (small pieces of text) whose embeddings are most similar to the question's embedding. This means it finds the pieces of text that are most relevant to the question.
7.  **Augment the Prompt:** The important chunks of text that were found are then added to the user's question. This combined text (question + relevant chunks) is called the **prompt**. A **prompt** is the instruction or question given to the LLM.
8.  **Generate the Answer:** Finally, this augmented **prompt** is given to the Large Language Model. The LLM uses the relevant chunks of text to generate (create) a clear and accurate answer. It answers *based on* the information provided in the chunks, not just its general knowledge.

### 4. Real-world example

Imagine you are a student at a college in India. Your college has a lot of rules and information in many documents. These include rules for exams, applying for scholarships, hostel rules, and leave policies.

You want to know, "What is the process to apply for a scholarship for poor students?"

*   **Without RAG:** If you ask a normal LLM, it might give you a general answer about scholarships. But it will not know your college's specific rules. It might even make up some steps that are not true for your college.
*   **With RAG:**
    1.  Your college's scholarship documents (PDFs, website pages) are prepared. They are split into chunks.
    2.  These chunks are turned into embeddings (number lists) and stored in a vector database.
    3.  When you ask, "What is the process to apply for a scholarship for poor students?", your question is also turned into an embedding.
    4.  RAG searches the vector database. It finds the exact sections from your college's scholarship documents that talk about applying for scholarships for poor students.
    5.  These relevant sections are added to your question. This combined information is given to the LLM.
    6.  The LLM then reads these specific college documents. It uses *only* that information to tell you the correct steps for your college. It might say, "According to College Rulebook Section 3.2, poor students can apply by filling Form A, submitting income proof to the Dean's office before October 15th." It can even show you the exact document section it used.

This way, RAG helps the LLM give you a specific, correct answer based on your college's actual rules.

### 5. Recap

*   RAG helps computer programs give better, more accurate answers.
*   It finds relevant information first and then uses a Large Language Model to write the answer.
*   RAG reduces the problem of LLMs making up false answers (hallucination).
*   It allows LLMs to use new or private information that they were not originally trained on.
*   RAG makes it easy to update knowledge just by changing documents, without needing to retrain the LLM.