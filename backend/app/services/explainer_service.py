from langchain_core.prompts import ChatPromptTemplate
from app.services.graph_service import graph_service
from app.services.llm_factory import get_llm

class ExplainerService:
    def __init__(self):
        self.llm = get_llm(temperature=0.2)
        
        self.prompt = ChatPromptTemplate.from_template("""
        You are a GDPR Expert AI. Your goal is to explain a specific GDPR Article clearly and concisely to a non-legal user.
        
        Use the following structured context retrieved from the official legal text and knowledge graph:
        
        **Article**: {title}
        
        **Obligations (What must be done)**:
        {obligations}
        
        **Defined Terms**:
        {terms}
        
        **Related Topics**:
        {topics}
        
        **Cross-References**:
        {references}
        
        ---
        **Instructions**:
        1. **Summary**: Provide a plain English summary of what this article requires (2-3 sentences).
        2. **Key Takeaways**: List the most important points as bullet points.
        3. **Implications**: Briefly explain what this means for a company (e.g., "You must encrypt data" or "You need a DPO").
        4. **Strict Constraint**: Do NOT hallucinate. Only use the provided context. If the context is empty, say "Insufficient information available."
        """)

    def explain_article(self, article_id: str):
        # 1. Fetch Context from Graph
        data = graph_service.get_article_details(article_id)
        if not data:
            return None

        # 2. Format Context for Prompt
        obligations_text = "\n".join([f"- {o['role']} must: {o['summary']}" for o in data['obligations']])
        terms_text = "\n".join([f"- {t['term']}: {t['definition']}" for o in data['terms'] for t in [o]]) # Fix loop if needed, data['terms'] is list of dicts
        # Wait, data['terms'] is list of {term, definition}. 
        terms_text = "\n".join([f"- {t['term']}: {t['definition']}" for t in data['terms']])
        
        topics_text = ", ".join(data['topics'])
        refs_text = ", ".join([f"Article {r['number']}" for r in data['references']])

        # 3. Invoke LLM
        chain = self.prompt | self.llm
        
        response = chain.invoke({
            "title": data['title'],
            "obligations": obligations_text if obligations_text else "No specific obligations extracted.",
            "terms": terms_text if terms_text else "No specific terms defined.",
            "topics": topics_text if topics_text else "General",
            "references": refs_text if refs_text else "None"
        })
        
        return {
            "article_id": article_id,
            "explanation": response.content,
            "context": data # Return original data too for UI
        }

explainer_service = ExplainerService()
