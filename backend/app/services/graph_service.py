import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class GraphService:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def get_article_details(self, article_id: str):
        """
        Fetch full article details including obligations, terms, and related articles.
        """
        query = """
        MATCH (a:Article {id: $article_id})
        OPTIONAL MATCH (a)-[:HAS_OBLIGATION]->(o:Obligation)
        OPTIONAL MATCH (o)-[:APPLIES_TO]->(r:Role)
        OPTIONAL MATCH (a)-[:DEFINES]->(t:Term)
        OPTIONAL MATCH (a)-[:RELATES_TO]->(topic:Topic)
        OPTIONAL MATCH (a)-[:REFERS_TO]->(ref:Article)
        RETURN a, 
               collect(DISTINCT {summary: o.summary, role: r.name}) as obligations,
               collect(DISTINCT {term: t.name, definition: t.definition}) as terms,
               collect(DISTINCT topic.name) as topics,
               collect(DISTINCT {id: ref.id, number: ref.number}) as references
        """
        with self.driver.session() as session:
            result = session.run(query, article_id=article_id).single()
            if not result:
                return None
            
            node = result['a']
            return {
                "id": node['id'],
                "number": node['number'],
                "title": node['title'],
                # "text": node['text'], # Text might not be in graph if we didn't put it there, but we have it in Qdrant/JSON. 
                # Actually, we didn't put full text in Neo4j in the loader script, only title/number.
                # We can fetch text from Qdrant or JSON if needed, or update loader. 
                # For now, let's assume frontend fetches text separately or we add it.
                "obligations": [o for o in result['obligations'] if o['summary']],
                "terms": [t for t in result['terms'] if t['term']],
                "topics": [t for t in result['topics'] if t],
                "references": [r for r in result['references'] if r['id']]
            }

    def get_all_topics(self):
        """
        Fetch all unique topics from the graph.
        """
        query = "MATCH (t:Topic) RETURN t.name as name ORDER BY t.name"
        with self.driver.session() as session:
            result = session.run(query)
            return [record["name"] for record in result]

    def get_articles_by_topic(self, topic: str):
        """
        Fetch all articles related to a specific topic.
        """
        query = """
        MATCH (t:Topic {name: $topic})<-[:RELATES_TO]-(a:Article)
        RETURN a.id as id, a.number as number, a.title as title
        ORDER BY a.number
        """
        with self.driver.session() as session:
            result = session.run(query, topic=topic)
            return [
                {"id": r["id"], "number": r["number"], "title": r["title"]}
                for r in result
            ]

graph_service = GraphService()
