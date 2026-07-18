from agents.atlas_mcp import atlas_search_web

topics = [
    "Biology",
    "Physics",
    "Microbiology",
    "Aquascaping",
    "Aquarium hobbies"
]

print("Initiating Atlas learning protocol...")
for topic in topics:
    print(f"\nTeaching Atlas about: {topic}")
    result = atlas_search_web(topic)
    print(result)

print("\nLearning protocol complete. All knowledge committed to Obsidian Vault.")
