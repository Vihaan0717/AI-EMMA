## 2025-05-15 - Optimizing Social Intelligence Layer
**Learning:** Re-instantiating utility classes that perform DB schema checks (like `PeopleRegistry`) in high-frequency functions (like `detect_person_language`) causes significant overhead. Pre-compiling regex in utility classes and using module-level instances can reduce latency by orders of magnitude.
**Action:** Always prefer pre-compiled regex for text processing and reuse shared utility instances at the module level when they contain expensive initialization or persistent caches.

## 2025-05-15 - Fast-path keyword detection in IntentEngine
**Learning:** Even with pre-compiled individual patterns, iterating over large lists of markers (like languages or emotions) to calculate scores is expensive. Implementing a "fast-path" combined regex check (`"|".join(markers)`) to skip the scoring loop for non-matching categories provides a significant speedup.
**Action:** Use combined regex patterns for existence checks before entering detailed scoring or classification loops for high-frequency text analysis.
