import json
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "../.env")
load_dotenv(dotenv_path=env_path)

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
INPUT_FILE = os.path.join(script_dir, "../../data/graph_data.json")

class GDPRGraphLoader:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Database cleared.")

    def create_constraints(self):
        with self.driver.session() as session:
            # Create constraints for performance and uniqueness
            session.run("CREATE CONSTRAINT article_id IF NOT EXISTS FOR (a:Article) REQUIRE a.id IS UNIQUE")
            session.run("CREATE CONSTRAINT term_name IF NOT EXISTS FOR (t:Term) REQUIRE t.name IS UNIQUE")
            session.run("CREATE CONSTRAINT topic_name IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE")
            print("Constraints created.")

    def load_data(self, data):
        with self.driver.session() as session:
            for item in data:
                print(f"Loading Article {item['article_number']}...")
                
                # 1. Create Article Node
                session.run("""
                    MERGE (a:Article {id: $id})
                    SET a.number = $number,
                        a.title = $title
                """, id=item['article_id'], number=item['article_number'], title=f"Article {item['article_number']}")

                extracted = item.get('extracted', {})

                # 2. Create Obligations and Link to Article
                for obl in extracted.get('obligations', []):
                    session.run("""
                        MATCH (a:Article {id: $article_id})
                        CREATE (o:Obligation {summary: $summary, text_snippet: $text})
                        MERGE (r:Role {name: $role})
                        CREATE (a)-[:HAS_OBLIGATION]->(o)
                        CREATE (o)-[:APPLIES_TO]->(r)
                    """, article_id=item['article_id'], summary=obl['summary'], text=obl['text_snippet'], role=obl['role'])

                # 3. Create Terms and Link
                for term in extracted.get('terms', []):
                    session.run("""
                        MATCH (a:Article {id: $article_id})
                        MERGE (t:Term {name: $term})
                        SET t.definition = $definition
                        MERGE (a)-[:DEFINES]->(t)
                    """, article_id=item['article_id'], term=term['term'], definition=term['definition'])

                # 4. Link Topics
                for topic in extracted.get('topics', []):
                    session.run("""
                        MATCH (a:Article {id: $article_id})
                        MERGE (t:Topic {name: $topic})
                        MERGE (a)-[:RELATES_TO]->(t)
                    """, article_id=item['article_id'], topic=topic)

                # 5. Link Related Articles (Cross-references)
                # Note: We might need a second pass if the target article doesn't exist yet, 
                # but MERGE handles creation of the target node (without props) if missing.
                for ref_num in extracted.get('related_articles', []):
                    target_id = f"ART-{ref_num}"
                    session.run("""
                        MATCH (source:Article {id: $source_id})
                        MERGE (target:Article {id: $target_id})
                        MERGE (source)-[:REFERS_TO]->(target)
                    """, source_id=item['article_id'], target_id=target_id)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    loader = GDPRGraphLoader(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        loader.clear_database() # Optional: remove if you want to append
        loader.create_constraints()
        loader.load_data(data)
        print("Graph ingestion complete.")
    except Exception as e:
        print(f"Error during ingestion: {e}")
    finally:
        loader.close()

if __name__ == "__main__":
    main()
