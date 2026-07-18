
import chromadb
import os

db_path = r"c:\Users\anger\Desktop\JARVIS-v2\arion\data\chromadb"
if not os.path.exists(db_path):
    print(f"Path not found: {db_path}")
    exit()

client = chromadb.PersistentClient(path=db_path)
collections = client.list_collections()
print(f"Collections: {[c.name for c in collections]}")

if "arion_knowledge" in [c.name for c in collections]:
    collection = client.get_collection(name="arion_knowledge")
    results = collection.query(query_texts=["Hi Nanna", "హాయ్ నాన్న", "Mahi", "Viraj"], n_results=5)
    print("Results from arion_knowledge:")
    print(results)
else:
    print("arion_knowledge collection not found.")

if "memory_vectors" in [c.name for c in collections]:
    collection = client.get_collection(name="memory_vectors")
    results = collection.query(query_texts=["Hi Nanna", "హాయ్ నాన్న", "Mahi", "Viraj"], n_results=5)
    print("\nResults from memory_vectors:")
    print(results)
