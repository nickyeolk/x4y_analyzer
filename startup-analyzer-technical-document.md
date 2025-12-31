This Technical Design Document (TDD) is optimized for 2025 standards, focusing on agentic transparency and low-overhead hosting.
Technical Design: "X for Y" Agentic Marketing Stress Tester
1. Executive Summary
This project is a high-transparency GenAI demo designed for LinkedIn showcasing. It uses a multi-agent orchestration to stress-test "X for Y" business ideas (e.g., "Uber for Dog Walkers"). Unlike static chatbots, this system features dynamic tool-calling and recursive reasoning, with every step exposed to the user through a real-time observability dashboard.
2. System Architecture
The system follows a decoupled Agent-Stream architecture where the backend maintains the agent state and pushes incremental updates to a React frontend via Server-Sent Events (SSE).
2.1 Core Tech Stack
Backend: Python 3.12+ / FastAPI.
Agent Orchestration: LangGraph (to handle cycles and state-machine logic).
Intelligence: GPT-4o-mini (Cost-effective for reasoning) or Claude 3.5 Sonnet.
Observability: LangSmith (Traces) + Langfuse (Metrics/Evals).
Search Tool: Tavily API (LLM-optimized search).
Frontend: React 19 (Vite) + Tailwind CSS + Shadcn/UI.
3. Agentic Workflow (The "Brain")
The logic is structured as a directed cyclic graph (DCG) to allow for "Thinking" and "Correction" loops

|Node Name |Responsibility |Tool / Data Access|
|=|=|=|
|The Analyst |Deconstructs the "X" brand's DNA. |Tavily Search API.|
|The Researcher |Investigates the "Y" market saturation. |Tavily + Python competitor\_count() func.|
|The Skeptic |Critiques the idea; triggers a "Loop Back" if logic is weak. |RAG: marketing\pitfalls.pdf.|
|The Strategist |Synthesizes final GTM and LinkedIn Hooks. |RAG.|

4. Observability & Transparency (The Demo Feature)
To meet the "Show the Trace" requirement, we implement a Triple-Layer Observability strategy:
4.1 Real-Time Stream (UX)
The React UI will use a custom hook to consume the LangGraph state.
Status Indicators: Thinking..., Searching Web..., Consulting Knowledge Base....
Live Reasoning: A "Thought Stream" component showing the raw LLM thinking field before the tool call.
4.2 The Trace Viewer
We will embed or link to the LangSmith Trace. This allows stakeholders to see:
Latency: Time spent in each node (e.g., "The Skeptic took 4.2s").
Token Consumption: Real-time breakdown of Prompt vs. Completion tokens.
Tool I/O: Exactly what JSON was sent to Tavily and what raw HTML/Text came back.
4.3 Metrics Dashboard
A persistent footer in the UI displaying:
Cost of Run: Calculated in real-time ($0.012 average).
Confidence Score: An LLM-as-a-judge score on the final GTM plan's viability.
5. Implementation & Hosting
To keep it cheap/free, we utilize usage-based "Hobby" tiers.
Hosting: Railway (Back-end + Front-end). Railway's Nixpacks automatically detect FastAPI and Vite, handling the build process seamlessly.
Database: Supabase (PostgreSQL) only if session persistence is required; otherwise, in-memory LangGraph Checkpointers will suffice.
RAG Store: FAISS (Local vector store) or ChromaDB. Since our knowledge base (marketing frameworks) is small, we can load this into memory on startup to save costs.
