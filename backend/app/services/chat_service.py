from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.search_service import search_service
from app.services.graph_service import graph_service
from app.services.explainer_service import explainer_service
from app.services.llm_factory import get_llm
import json
import asyncio

class ChatService:
    def __init__(self):
        # Router Prompt
        self.router_prompt = ChatPromptTemplate.from_template("""
        You are the "GDPR Assistant" Router. Your job is to classify the user's query and extract parameters.
        
        Available Tools:
        1. **EXPLAIN_ARTICLE**: User asks to explain/summarize a specific article (e.g., "Explain Article 32", "What does Art 5 say?").
           - Parameter: `article_number` (integer, e.g., 32)
        2. **TOPIC_SEARCH**: User asks for articles about a specific topic (e.g., "Show me articles about encryption", "Where is consent mentioned?").
           - Parameter: `topic` (string, inferred from query)
        3. **GENERAL_QA**: User asks a general question that requires searching the text (e.g., "What are the fines for non-compliance?", "Can I process data of children?").
           - Parameter: `query` (the original user query)
        
        Output JSON ONLY:
        {{
            "tool": "EXPLAIN_ARTICLE" | "TOPIC_SEARCH" | "GENERAL_QA",
            "parameters": {{ ... }}
        }}
        
        User Query: {query}
        """)
        
        # QA Prompt
        self.qa_prompt = ChatPromptTemplate.from_template("""
        You are a GDPR Expert. Answer the user's question based ONLY on the provided context.
        
        IMPORTANT: Answer in the SAME LANGUAGE as the user's question. If the question is in German, answer in German.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer (concise, citing articles):
        """)

    async def chat_stream(self, query: str, model_provider: str = None):
        """
        Generator that yields streaming response chunks.
        Format: JSON string per line.
        """
        # Retry Logic (Max 2 attempts)
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Get LLM based on user preference
                llm = get_llm(temperature=0, provider=model_provider)

                # 1. Route
                router_chain = self.router_prompt | llm | StrOutputParser()
                
                # Routing is fast/short, so we await it
                route_raw = await router_chain.ainvoke({"query": query})
                route_raw = route_raw.replace("```json", "").replace("```", "").strip()
                try:
                    route = json.loads(route_raw)
                except json.JSONDecodeError:
                     # Fallback if JSON is malformed
                    route = {"tool": "GENERAL_QA", "parameters": {"query": query}}

                tool = route.get("tool")
                params = route.get("parameters", {})

                # 2. Execute Tool
                if tool == "EXPLAIN_ARTICLE":
                    art_num = params.get("article_number")
                    if art_num:
                        result = explainer_service.explain_article(f"ART-{art_num}")
                        if result:
                            yield json.dumps({
                                "type": "explanation",
                                "content": result["explanation"],
                                "related_data": result["context"]
                            }) + "\n"
                            return
                    yield json.dumps({"type": "error", "content": "Could not find the specified article."}) + "\n"
                    return

                elif tool == "TOPIC_SEARCH":
                    topic = params.get("topic")
                    results = search_service.search(topic, limit=10)
                    yield json.dumps({
                        "type": "search_results",
                        "content": f"Here are the articles related to '{topic}':",
                        "results": results
                    }) + "\n"
                    return

                elif tool == "GENERAL_QA":
                    # RAG Flow
                    search_results = search_service.search(params.get("query"), limit=5)
                    context_text = "\n\n".join([f"Article {r['article_number']} ({r['title']}):\n{r['text_snippet']}" for r in search_results])
                    
                    # Send sources first
                    yield json.dumps({
                        "type": "sources",
                        "results": search_results
                    }) + "\n"

                    # Stream Answer
                    qa_chain = self.qa_prompt | llm | StrOutputParser()
                    
                    async for chunk in qa_chain.astream({"context": context_text, "question": params.get("query")}):
                        yield json.dumps({
                            "type": "token",
                            "content": chunk
                        }) + "\n"
                    return

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                last_error = e
                # If it's the last attempt, don't continue loop, just fall through to error handling
                if attempt == max_retries - 1:
                    break
                # Optional: wait a bit before retry
                await asyncio.sleep(1)
        
        # If we get here, all retries failed
        error_msg = "Sorry, I encountered an error processing your request."
        if "404" in str(last_error) and "models/" in str(last_error):
             error_msg = "Error: The selected model is not available or the API key is invalid. Please check your settings."
        elif "quota" in str(last_error).lower():
             error_msg = "Error: API quota exceeded. Please check your billing or credits."
        
        yield json.dumps({"type": "error", "content": error_msg}) + "\n"

chat_service = ChatService()
