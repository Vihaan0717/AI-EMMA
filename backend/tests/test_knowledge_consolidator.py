import asyncio
import json
import logging
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Ensure project path is accessible
sys.path.append(str(Path(__file__).parent.parent))

from core.knowledge_consolidator import KnowledgeConsolidator
from brain.neurons.neural_graph import NeuralGraph
from brain.neurons.neuron import NeuronType, MemoryLayer

class TestKnowledgeConsolidator(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.consolidator = KnowledgeConsolidator(root_dir=".")
        
    @patch("core.knowledge_consolidator.AIEngine")
    @patch("core.knowledge_consolidator.WebBrain")
    async def test_topic_extraction(self, mock_web_brain, mock_ai_engine):
        # Arrange
        ai_mock = AsyncMock()
        ai_mock.generate.return_value = '["ViteJS", "Machine Learning", "Mental Health"]'
        self.consolidator.ai = ai_mock
        
        # Act
        topics = await self.consolidator._extract_learning_topics()
        
        # Assert
        self.assertEqual(len(topics), 3)
        self.assertIn("ViteJS", topics)
        self.assertIn("Machine Learning", topics)
        self.assertIn("Mental Health", topics)
        ai_mock.generate.assert_called_once()

    @patch("core.knowledge_consolidator.AIEngine")
    async def test_cross_verification(self, mock_ai_engine):
        # Arrange
        ai_mock = AsyncMock()
        verified_json = {
            "description": "Vite is a modern, ultra-fast frontend build tool.",
            "facts": ["Uses native ES modules", "Features lightning fast Hot Module Replacement", "Created by Evan You"],
            "trust_score": 0.95
        }
        ai_mock.generate.return_value = json.dumps(verified_json)
        self.consolidator.ai = ai_mock
        
        search_data = {
            "source": "wikipedia",
            "content": "Vite is a build tool that aims to provide a faster and leaner development experience for modern web projects."
        }
        
        # Act
        result = await self.consolidator._cross_verify_topic("Vite", search_data)
        
        # Assert
        self.assertEqual(result["description"], verified_json["description"])
        self.assertEqual(len(result["facts"]), 3)
        self.assertEqual(result["trust_score"], 0.95)

    def test_memory_commit(self):
        # Arrange
        topic = "TestNeuroscience"
        fact = {
            "description": "The study of the nervous system.",
            "facts": ["Includes cognitive science", "Studies brain plasticity"],
            "trust_score": 0.88
        }
        
        # Ensure neuron doesn't exist beforehand
        existing = self.consolidator.graph.get_neuron(topic)
        if existing:
            # Clean it up from internal memory if left from a previous run
            if topic in self.consolidator.graph._label_index:
                nid = self.consolidator.graph._label_index[topic]
                self.consolidator.graph._neurons.pop(nid, None)
                self.consolidator.graph._label_index.pop(topic, None)
        
        # Act
        self.consolidator._commit_to_memory(topic, fact)
        
        # Assert
        neuron = self.consolidator.graph.get_neuron(topic)
        self.assertIsNotNone(neuron)
        self.assertEqual(neuron.neuron_type, NeuronType.CONCEPT)
        self.assertEqual(neuron.memory_layer, MemoryLayer.LONG_TERM)
        self.assertEqual(neuron.data["description"], fact["description"])
        self.assertEqual(neuron.data["trust_score"], fact["trust_score"])
        
        # Check that it connects to Owner
        connections = self.consolidator.graph.get_strongest_connections(topic)
        self.assertTrue(any(c["to"] == "Owner" for c in connections))

if __name__ == "__main__":
    unittest.main()
