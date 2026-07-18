import re

query = "Who is Alan Turing?"
pattern = r'\b(what is|who is|definition|history)\b'
match = re.search(pattern, query, re.IGNORECASE)
print(f"Match: {match}")
if match:
    print(f"Group: {match.group(0)}")
