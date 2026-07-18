// ---------------------------------------------------------
// 1. 3D FORCE GRAPH INITIALIZATION
// ---------------------------------------------------------
const graphContainer = document.getElementById('3d-graph');
let graphData = { nodes: [], links: [] };
let searchedNodes = [];

// Color dictionary mapping node groups to hex colors
const groupColors = {
    nexus: '#ff3366',
    agents: '#00d2ff',
    health: '#00ff88',
    meals: '#ffaa00',
    symptoms: '#ff3333',
    concepts: '#bd00ff',
    knowledge: '#ffffff'
};

const Graph = ForceGraph3D()(graphContainer)
    .backgroundColor('#030308')
    .nodeColor(node => groupColors[node.group] || '#999999')
    .nodeVal(node => {
        if (node.group === 'nexus') return 8;
        if (node.group === 'agents') return 6;
        return node.val || 2.5;
    })
    .nodeLabel(node => `<div class="graph-tooltip"><strong>${node.label}</strong><br/>Group: ${node.group}</div>`)
    .linkWidth(1.2)
    .linkColor(() => 'rgba(255,255,255,0.08)')
    .linkDirectionalParticles(3)
    .linkDirectionalParticleSpeed(link => (link.weight || 1) * 0.008)
    .linkDirectionalParticleWidth(2.0)
    .onNodeHover(node => {
        if (node) {
            showNodeInfo(node);
        }
    })
    .onNodeClick(node => {
        const distance = 80;
        const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);

        Graph.cameraPosition(
            { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio },
            node,
            3000
        );
        showNodeInfo(node);
    });

// Tweak force engine for a more spread out, neural structure
Graph.d3Force('charge').strength(-180);
Graph.d3Force('link').distance(link => {
    // Keep hubs close to Nexus, detail nodes further away
    return link.source.group === 'nexus' || link.target.group === 'nexus' ? 40 : 80;
});


// Fetch Graph Data from API
async function fetchGraphData() {
    try {
        const response = await fetch('/api/graph');
        const data = await response.json();
        graphData = data;
        
        // Refresh visualization with the fetched data
        Graph.graphData(graphData);
        console.log("Graph updated: ", graphData.nodes.length, "nodes,", graphData.links.length, "links");
    } catch (e) {
        console.error("Failed to fetch graph data:", e);
    }
}

// Show Node Details in info panel
const infoPanel = document.getElementById('node-info-panel');
const infoTitle = document.getElementById('node-title');
const infoGroup = document.getElementById('node-group-badge');
const infoDetails = document.getElementById('node-details');
const closeInfoBtn = document.getElementById('close-info');

function showNodeInfo(node) {
    infoPanel.classList.remove('hidden');
    infoTitle.innerText = node.label;
    infoGroup.innerText = node.group;
    infoDetails.innerText = node.details || "No further details logged.";
}

closeInfoBtn.onclick = () => {
    infoPanel.classList.add('hidden');
};

// ---------------------------------------------------------
// 2. SEARCH & NAVIGATION
// ---------------------------------------------------------
const searchInput = document.getElementById('graph-search');

searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    if (!query) {
        // Reset node highlighting
        Graph.nodeColor(node => groupColors[node.group] || '#999999');
        return;
    }

    // Find matches
    const matches = graphData.nodes.filter(n => n.label.toLowerCase().includes(query));
    
    // Highlight matched nodes and dim others
    Graph.nodeColor(node => {
        const isMatch = node.label.toLowerCase().includes(query);
        return isMatch ? groupColors[node.group] : '#22222b';
    });

    // Auto-focus on first match if available
    if (matches.length > 0) {
        const targetNode = matches[0];
        // Wait briefly for smooth panning
        setTimeout(() => {
            const distance = 90;
            const distRatio = 1 + distance/Math.hypot(targetNode.x, targetNode.y, targetNode.z);
            Graph.cameraPosition(
                { x: targetNode.x * distRatio, y: targetNode.y * distRatio, z: targetNode.z * distRatio },
                targetNode,
                2000
            );
            showNodeInfo(targetNode);
        }, 100);
    }
});

// ---------------------------------------------------------
// 3. WEBSOCKET COMMAND SPINE
// ---------------------------------------------------------
const clientID = "nexus_dashboard_" + Math.floor(Math.random() * 1000);
const wsUrl = `ws://${window.location.host}/ws/${clientID}`;

let socket;

const chatDisplay = document.getElementById('chat-display');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

function connectWS() {
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        showToast("🔗 BRAIN INTEGRITY SECURED");
        document.getElementById('system-status').innerHTML = '<i class="fas fa-circle" style="color:#00ff88"></i> ONLINE';
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };

    socket.onclose = () => {
        showToast("⚠️ LINK INTERRUPTED - RECONNECTING...");
        document.getElementById('system-status').innerHTML = '<i class="fas fa-circle" style="color:#ff3333"></i> OFFLINE';
        setTimeout(connectWS, 3000);
    };
}

function handleMessage(data) {
    console.log("RX:", data);
    
    switch(data.type) {
        case "ACK":
            break;
        case "AGENT_RESPONSE":
            addMessage(data.content, "agent");
            break;
        case "SYSTEM":
            addMessage(data.content, "system");
            break;
        case "GRAPH_UPDATE":
            // Trigger visual glow/synaptic splash on graph data update
            showToast("🔥 SYNAPSES FORMING...");
            fetchGraphData();
            break;
        case "AI_RESPONSE":
            addMessage(data.text, "agent");
            break;
    }
}

function addMessage(text, type) {
    const msg = document.createElement('div');
    msg.className = `message ${type}`;
    msg.innerText = text;
    chatDisplay.appendChild(msg);
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
}

sendBtn.onclick = sendMessage;
userInput.onkeypress = (e) => { if (e.key === 'Enter') sendMessage(); };

function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;
    addMessage(text, "user");
    socket.send(JSON.stringify({
        type: "COMMAND",
        content: text,
        timestamp: new Date().toISOString()
    }));
    userInput.value = "";
}

function showToast(text) {
    const toast = document.getElementById('notification-toast');
    toast.innerText = text;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

// ---------------------------------------------------------
// 4. BOOTSTRAP INITIALIZATION
// ---------------------------------------------------------
// Load initial graph
fetchGraphData();
// Connect web sockets
connectWS();

// Make graph responsive
window.addEventListener('resize', () => {
    Graph.width(graphContainer.clientWidth);
    Graph.height(graphContainer.clientHeight);
});
