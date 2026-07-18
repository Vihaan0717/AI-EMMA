import asyncio
import sys
from pathlib import Path

# Set up project path
sys.path.append(str(Path(__file__).parent.parent))

from core.knowledge_consolidator import KnowledgeConsolidator
from brain.neurons.neural_graph import NeuralGraph

async def main():
    print("=========================================================")
    print("      NEXUS-X: LIVE PROACTIVE LEARNING VERIFICATION")
    print("=========================================================")
    
    # 1. Initialize consolidator
    print("\n[1/4] Initializing Knowledge Consolidator...")
    consolidator = KnowledgeConsolidator(root_dir=".")
    await consolidator.initialize()
    print("[+] Consolidator initialized successfully.")
    
    # 2. Get initial stats
    initial_stats = consolidator.graph.get_brain_stats()
    print(f"\n[2/4] Initial Neural Graph Stats:")
    print(f"  - Total Neurons: {initial_stats['total_neurons']}")
    print(f"  - Total Synapses: {initial_stats['total_synapses']}")
    print(f"  - Long-Term Memory (LTM) Neurons: {initial_stats['ltm_neurons']}")
    
    # 3. Trigger manual consolidation cycle
    print("\n[3/4] Triggering proactive learning and verification cycle...")
    print("  * Gathering multi-source data...")
    print("  * Cross-checking to verify facts & prevent math hallucinations...")
    
    learned_topics = await consolidator.run_consolidation_cycle()
    
    # 4. Check results and final stats
    print("\n[4/4] Learning Results:")
    if learned_topics:
        print(f"  [✓] Successfully verified and committed topics: {learned_topics}")
        
        # Verify specific details of a newly learned topic
        for topic in learned_topics:
            neuron = consolidator.graph.get_neuron(topic)
            if neuron:
                print(f"\n  >> Injected LTM Node: '{neuron.label}'")
                print(f"     - Type: {neuron.neuron_type.value}")
                print(f"     - Layer: {neuron.memory_layer.value}")
                print(f"     - Description: {neuron.data.get('description')}")
                if neuron.data.get('formula'):
                    print(f"     - Verified Formula: {neuron.data.get('formula')}")
                if neuron.data.get('variables'):
                    print(f"     - Components/Variables: {neuron.data.get('variables')}")
                print(f"     - Trust Score: {neuron.data.get('trust_score')}")
    else:
        print("  [-] No new topics were committed in this cycle (either already known or filtered out by trust gate).")
        
    final_stats = consolidator.graph.get_brain_stats()
    print(f"\nFinal Neural Graph Stats:")
    print(f"  - Total Neurons: {final_stats['total_neurons']}")
    print(f"  - Total Synapses: {final_stats['total_synapses']}")
    print(f"  - Long-Term Memory (LTM) Neurons: {final_stats['ltm_neurons']}")
    print("=========================================================")

if __name__ == "__main__":
    asyncio.run(main())
