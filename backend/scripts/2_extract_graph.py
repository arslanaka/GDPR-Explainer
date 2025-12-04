import json
import os
import time
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from dotenv import load_dotenv

# Load environment variables
# Assumes script is in backend/scripts/ and .env is in backend/
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "../.env")
load_dotenv(dotenv_path=env_path)

# Configuration
# Data is in explainer/data, which is ../../data relative to backend/scripts/
INPUT_FILE = os.path.join(script_dir, "../../data/gdpr_raw.json")
OUTPUT_FILE = os.path.join(script_dir, "../../data/graph_data.json")

# --- Data Models for Extraction ---

class Obligation(BaseModel):
    summary: str = Field(description="Concise summary of the obligation")
    role: str = Field(description="The role responsible (e.g., Controller, Processor, Member State)")
    text_snippet: str = Field(description="Exact text snippet from the article supporting this")

class Term(BaseModel):
    term: str = Field(description="The defined term")
    definition: str = Field(description="The definition provided in the text")

class ArticleExtraction(BaseModel):
    obligations: List[Obligation] = Field(default_factory=list, description="List of obligations found")
    terms: List[Term] = Field(default_factory=list, description="List of defined terms found")
    related_articles: List[int] = Field(default_factory=list, description="List of other Article numbers referenced")
    topics: List[str] = Field(default_factory=list, description="List of 2-3 main topics (e.g., Security, Consent)")

# --- LLM Setup ---

llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
parser = PydanticOutputParser(pydantic_object=ArticleExtraction)

PROMPT_TEMPLATE = """
You are a legal expert AI building a Knowledge Graph for the GDPR.
Analyze the following GDPR Article text and extract structured data.

Article Title: {title}
Article Text:
{text}

Extract the following:
1. **Obligations**: Specific requirements or duties. Identify WHO (Role) must do WHAT (Summary).
2. **Terms**: Any terms explicitly defined in this article (usually in Article 4, but check others).
3. **Related Articles**: Any other GDPR Articles explicitly mentioned by number (e.g., "Article 6").
4. **Topics**: 2-3 high-level keywords (e.g., "Data Subject Rights", "Encryption", "Penalties").

{format_instructions}
"""

prompt = ChatPromptTemplate.from_template(
    template=PROMPT_TEMPLATE,
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

chain = prompt | llm | parser

# --- Main Processing ---

def process_article(article):
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"Processing {article['id']} - {article['title']}...")
            result = chain.invoke({"title": article['title'], "text": article['text']})
            
            # Merge result with original article ID for the graph
            return {
                "article_id": article['id'],
                "article_number": article['number'],
                "extracted": result.model_dump()
            }
        except Exception as e:
            if "insufficient_quota" in str(e):
                print(f"CRITICAL ERROR: Insufficient Quota for {article['id']}. Stopping.")
                return None # Stop trying if we are out of money
            
            print(f"Error processing {article['id']} (Attempt {attempt+1}/{max_retries}): {e}")
            time.sleep(retry_delay * (attempt + 1)) # Exponential backoff
            
    return None

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file {INPUT_FILE} not found. Run 1_parse_gdpr.py first.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # Load existing progress if any
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            print(f"Loaded {len(graph_data)} existing items from {OUTPUT_FILE}")
            existing_ids = {item['article_id'] for item in graph_data}
        except:
            graph_data = []
            existing_ids = set()
    else:
        graph_data = []
        existing_ids = set()
    
    for item in raw_data:
        # Skip if already processed
        if item['id'] in existing_ids:
            continue

        # Skip if text is too short or empty
        if len(item['text']) < 50:
            continue
            
        extracted = process_article(item)
        if extracted:
            graph_data.append(extracted)
            # Save incrementally
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=2, ensure_ascii=False)
        
        # Rate limit protection
        time.sleep(1)

    print(f"Extraction complete. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
