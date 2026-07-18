# arion/knowledge/vault_loader.py

import os
import json
import re
import yaml
import hashlib
import pickle
import numpy as np
import frontmatter
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import faiss
from sentence_transformers import SentenceTransformer

class VaultLoader:
    """
    ARION Vault Loader V3
    Deep scanning + Semantic RAG integration
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.knowledge_base = {}
        self.index = {}
        self.categories = {}
        
        # Files for persistence
        self.base_dir = Path(__file__).parent
        self.index_file = self.base_dir / 'vault_index.json'
        self.faiss_index_file = self.base_dir / 'vault_embeddings.index'
        self.metadata_file = self.base_dir / 'vault_metadata.pkl'
        
        # Semantic Search Components
        self.model_name = 'all-MiniLM-L6-v2'
        self._model = None # Lazy load
        self.vector_index = None
        self.file_id_map = [] # Maps index row to file_id
        
        # Deep Category Mapping
        self.category_map = {
            '_archive':                    'archived',
            'Agent_Self/Feedback':         'self_feedback',
            'Agent_Self/Learning_Journal': 'learning_journal',
            'Agent_Self/Persona':          'persona',
            'Agent_Self/Index':            'self_index',
            'Agent_Self':                  'self_identity',
            'Brain':                       'cognitive_system',
            'Connections':                 'relationships',
            'Culture':                     'culture',
            'Injected/article_digests':    'articles',
            'Injected/Summaries':          'summaries',
            'Injected/youtube_summaries':  'youtube',
            'Injected':                    'injected',
            'Knowledge/Anime':             'anime',
            'Knowledge/Books':             'books',
            'Knowledge/General':           'general',
            'Knowledge/History':           'history',
            'Knowledge/Movies':            'movies',
            'Knowledge/Music':             'music',
            'Knowledge/News':              'news',
            'Knowledge/Philosophy':        'philosophy',
            'Knowledge/Psychology':        'psychology',
            'Knowledge/Religion':          'religion',
            'Knowledge':                   'knowledge',
        }

        self.supported_extensions = {'.md', '.txt', '.json', '.yaml', '.yml'}

    @property
    def model(self):
        """Lazy load the embedding model"""
        if self._model is None:
            print(f"Loading semantic model ({self.model_name})...")
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def load_all(self, force_reload: bool = False) -> Dict:
        """Load entire vault into memory and build/load vector index"""
        
        print(f"Reloading Knowledge Vault: {self.vault_path}")
        print("=" * 50)
        
        # 1. Check if vault path exists
        if not self.vault_path.exists():
            print(f"Vault path does not exist: {self.vault_path}")
            print(f"Creating directory...")
            self.vault_path.mkdir(parents=True, exist_ok=True)
            return {}

        # 2. Check Cache
        if not force_reload and self.index_file.exists():
            try:
                print("Loading text index from cache...")
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                
                if cached.get('vault_path') == str(self.vault_path):
                    self.knowledge_base = cached.get('knowledge_base', {})
                    self.index = cached.get('index', {})
                    self.categories = cached.get('categories', {})
                    
                    if self._verify_cache() and self.knowledge_base:
                        print(f"Loaded {len(self.index)} files from cache")
                        self._load_vector_index()
                        if self.vector_index is not None:
                            return self.knowledge_base
                    else:
                        print("Cache invalid or empty, rescanning...")
            except Exception:
                print("Cache read error, rescanning...")
        
        # 3. Fresh load of files
        self._reload_files_from_disk()
        
        # 4. Build semantic index
        if self.knowledge_base:
            self._build_vector_index()
        else:
            print("No files found to index.")
            self._print_vault_structure()
        
        return self.knowledge_base

    def _verify_cache(self) -> bool:
        """Verify cached files still exist on disk"""
        if not self.knowledge_base: return False
        sample = list(self.knowledge_base.values())[:5]
        for item in sample:
            f_path = item.get('full_path')
            if f_path and not Path(f_path).exists(): return False
        return True

    def _print_vault_structure(self):
        """Print current vault directory structure for debugging"""
        print(f"\nVault structure at: {self.vault_path}")
        for root, dirs, files in os.walk(str(self.vault_path)):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            level = len(Path(root).relative_to(self.vault_path).parts)
            indent = "  " * level
            print(f"{indent}folder {Path(root).name}/")
            for f in files[:3]:
                print(f"{indent}  file {f}")
            if len(files) > 3: print(f"{indent}  ... ({len(files)-3} more)")

    def _reload_files_from_disk(self):
        print("Scanning files on disk...")
        self.knowledge_base = {}
        self.index = {}
        self.categories = {}
        
        total_files = 0
        total_words = 0

        for root, dirs, files in os.walk(str(self.vault_path)):
            # Skip noise
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'node_modules', 'embeddings')]
            
            for filename in files:
                file_path = Path(root) / filename
                if file_path.suffix.lower() not in self.supported_extensions: continue
                if filename.startswith('.') or filename.startswith('~'): continue
                
                try:
                    relative_path = file_path.relative_to(self.vault_path)
                    content, metadata = self._load_file(file_path)
                    
                    if content and content.strip():
                        category = self._get_category(relative_path)
                        file_id = self._generate_id(str(file_path))
                        words = len(content.split())
                        
                        self.knowledge_base[file_id] = {
                            'id': file_id,
                            'title': file_path.stem,
                            'filename': filename,
                            'path': str(relative_path),
                            'full_path': str(file_path),
                            'category': category,
                            'content': content,
                            'metadata': metadata,
                            'word_count': words,
                            'loaded_at': datetime.now().isoformat(),
                            'tags': metadata.get('tags', []),
                            'summary': self._quick_summary(content),
                            'extension': file_path.suffix.lower()
                        }
                        
                        self.index[file_id] = {
                            'title': file_path.stem,
                            'path': str(relative_path),
                            'category': category,
                            'words': words
                        }
                        
                        if category not in self.categories: self.categories[category] = []
                        self.categories[category].append(file_id)
                        
                        total_files += 1
                        total_words += words
                        # print(f"  [{category:15}] {filename}") # Suppressed for brevity
                except Exception:
                    continue

        if total_files > 0:
            self._save_index()
            print(f"Loaded {total_files} files ({total_words:,} words)")
        else:
            print("No files found in vault!")

    def _build_vector_index(self):
        """Generate embeddings and build FAISS index"""
        print("\nBuilding Semantic Index (Vectors)...")
        file_ids = list(self.knowledge_base.keys())
        texts = [f"{self.knowledge_base[fid]['title']}: {self.knowledge_base[fid]['content'][:1000]}" for fid in file_ids]
        
        if not texts: return

        print(f"Generating embeddings for {len(texts)} documents...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        
        dimension = embeddings.shape[1]
        self.vector_index = faiss.IndexFlatL2(dimension)
        self.vector_index.add(embeddings)
        self.file_id_map = file_ids
        
        self._save_vector_index()
        print(f"Semantic Index built with {len(file_ids)} vectors")

    def _save_vector_index(self):
        try:
            faiss.write_index(self.vector_index, str(self.faiss_index_file))
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.file_id_map, f)
        except Exception as e:
            print(f"Error saving vector index: {e}")

    def _load_vector_index(self):
        try:
            if self.faiss_index_file.exists() and self.metadata_file.exists():
                print("Loading semantic index from cache...")
                self.vector_index = faiss.read_index(str(self.faiss_index_file))
                with open(self.metadata_file, 'rb') as f:
                    self.file_id_map = pickle.load(f)
                if self.vector_index.ntotal != len(self.knowledge_base):
                    self.vector_index = None # Out of sync
                else:
                    print(f"Loaded {self.vector_index.ntotal} semantic vectors")
        except Exception:
            self.vector_index = None

    def search(self, query: str, category: str = None, 
               max_results: int = 5, hybrid_weight: float = 0.5) -> List[Dict]:
        """Hybrid search: Combined Keyword + Semantic"""
        if not query or not self.knowledge_base: return []
        query_lower = query.lower()
        
        # 1. Semantic Search
        semantic_results = {}
        if self.vector_index is not None:
            query_vector = self.model.encode([query_lower]).astype('float32')
            distances, indices = self.vector_index.search(query_vector, max_results * 2)
            for i, idx in enumerate(indices[0]):
                if idx == -1: continue
                file_id = self.file_id_map[idx]
                score = 1.0 / (1.0 + distances[0][i])
                semantic_results[file_id] = score

        # 2. Keyword Search
        keyword_results = {}
        query_words = [w for w in query_lower.split() if len(w) > 2]
        for file_id, data in self.knowledge_base.items():
            if category and data['category'] != category: continue
            score = 0
            title_l = data['title'].lower()
            content_l = data['content'].lower()
            if query_lower in title_l: score += 10
            for w in query_words:
                if w in title_l: score += 3
                if w in content_l: score += 1
            if score > 0: keyword_results[file_id] = score / 20.0 # Normalize

        # 3. Combine
        final_results = []
        all_ids = set(semantic_results.keys()) | set(keyword_results.keys())
        for fid in all_ids:
            if category and self.knowledge_base[fid]['category'] != category: continue
            s_score = semantic_results.get(fid, 0)
            k_score = min(keyword_results.get(fid, 0), 1.0)
            combined_score = (s_score * hybrid_weight) + (k_score * (1 - hybrid_weight))
            
            if combined_score > 0.05:
                data = self.knowledge_base[fid]
                final_results.append({
                    'id': fid, 'title': data['title'], 'category': data['category'],
                    'score': combined_score, 'summary': data['summary'],
                    'content': data['content'][:600], 'path': data['path']
                })

        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results[:max_results]

    def _load_file(self, path: Path) -> Tuple[Optional[str], Dict]:
        ext = path.suffix.lower()
        if ext == '.md': return self._load_markdown(path)
        elif ext == '.txt': return self._load_text(path), {}
        elif ext == '.json': return self._load_json(path)
        elif ext in ('.yaml', '.yml'): return self._load_yaml(path)
        return None, {}

    def _load_markdown(self, path: Path) -> Tuple[Optional[str], Dict]:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                raw = f.read()
            if not raw.strip(): return None, {}
            metadata = {}; content = raw
            if raw.startswith('---'):
                try:
                    end = raw.find('---', 3)
                    if end > 0:
                        front = raw[3:end].strip()
                        metadata = yaml.safe_load(front) or {}
                        content = raw[end+3:].strip()
                except: pass
            return self._clean_markdown(content), metadata
        except: return None, {}

    def _load_text(self, path: Path) -> Optional[str]:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except: return None

    def _load_json(self, path: Path) -> Tuple[Optional[str], Dict]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return json.dumps(data, indent=2, ensure_ascii=False), {}
        except: return None, {}

    def _load_yaml(self, path: Path) -> Tuple[Optional[str], Dict]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return json.dumps(data, indent=2, ensure_ascii=False), {}
        except: return None, {}

    def _clean_markdown(self, text: str) -> str:
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text) # Links
        text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text) # Images
        text = re.sub(r'```[^\n]*\n(.*?)```', r'\1', text, flags=re.DOTALL) # Code blocks
        text = re.sub(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', lambda m: m.group(2) or m.group(1), text) # Wiki links
        text = re.sub(r'- \[[ x]\] ', '- ', text) # Checkboxes
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _get_category(self, relative_path: Path) -> str:
        path_str = '/'.join(relative_path.parts[:-1])
        sorted_map = sorted(self.category_map.items(), key=lambda x: len(x[0]), reverse=True)
        for key, category in sorted_map:
            if path_str.startswith(key.replace('\\', '/')): return category
        return relative_path.parts[0].lower() if len(relative_path.parts) > 1 else 'general'

    def _quick_summary(self, content: str, max_chars: int = 250) -> str:
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        summary = ' '.join(lines[:4])
        return summary[:max_chars] + '...' if len(summary) > max_chars else summary

    def _generate_id(self, path: str) -> str:
        return hashlib.md5(path.encode()).hexdigest()[:12]

    def _save_index(self):
        cache = {
            'vault_path': str(self.vault_path), 'generated_at': datetime.now().isoformat(),
            'index': self.index, 'knowledge_base': self.knowledge_base, 'categories': self.categories
        }
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)

    def get_categories_summary(self) -> Dict:
        summary = {}
        for cat, fids in self.categories.items():
            words = sum(self.knowledge_base[fid]['word_count'] for fid in fids)
            summary[cat] = {'file_count': len(fids), 'total_words': words}
        return summary
