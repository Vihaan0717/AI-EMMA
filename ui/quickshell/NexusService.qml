import QtQml 2.15
import QtWebSockets 1.15

QtObject {
    id: root

    // Exposed properties for dynamic QML bindings
    property string activeAgent: "Offline"
    property bool isThinking: false
    property var dataList: []
    property bool isConnected: false

    // Configuration
    property string socketUrl: "ws://localhost:8000/crud"
    property bool autoReconnect: true
    property int reconnectIntervalMs: 3000

    // Internal reference to websocket
    property var webSocket: WebSocket {
        id: socket
        url: root.socketUrl
        active: false

        onStatusChanged: {
            if (socket.status === WebSocket.Open) {
                root.isConnected = true;
                reconnectTimer.stop();
                console.log("[NexusService] WebSocket connected to: " + socket.url);
            } else if (socket.status === WebSocket.Closed || socket.status === WebSocket.Error) {
                root.isConnected = false;
                console.log("[NexusService] WebSocket closed/failed. Status: " + socket.status);
                if (root.autoReconnect) {
                    reconnectTimer.start();
                }
            }
        }

        onTextMessageReceived: {
            try {
                var parsed = JSON.parse(message);
                console.log("[NexusService] Received message: " + message);
                
                if (parsed.type === "init" || parsed.type === "update" || parsed.type === "state") {
                    if (parsed.activeAgent !== undefined) {
                        root.activeAgent = parsed.activeAgent;
                    }
                    if (parsed.isThinking !== undefined) {
                        root.isThinking = parsed.isThinking;
                    }
                    if (parsed.dataList !== undefined) {
                        root.dataList = parsed.dataList;
                    }
                }
            } catch (err) {
                console.log("[NexusService] Failed to parse message JSON: " + err);
            }
        }
    }

    // Timer for reconnects
    property var reconnectTimer: Timer {
        id: reconnectTimer
        interval: root.reconnectIntervalMs
        repeat: false
        onTriggered: {
            if (!root.isConnected) {
                console.log("[NexusService] Attempting to reconnect to: " + root.socketUrl);
                socket.active = false;
                socket.active = true;
            }
        }
    }

    // Callbacks to initialize service
    Component.onCompleted: {
        socket.active = true;
    }

    // CRUD Interface functions to be invoked by UI components
    function createItem(title, importance) {
        if (!root.isConnected) {
            console.log("[NexusService] Cannot create item: socket is disconnected.");
            return;
        }
        var msg = {
            "action": "create",
            "title": title,
            "importance": parseFloat(importance)
        };
        socket.sendTextMessage(JSON.stringify(msg));
    }

    function updateItem(id, title, importance) {
        if (!root.isConnected) {
            console.log("[NexusService] Cannot update item: socket is disconnected.");
            return;
        }
        var msg = {
            "action": "update",
            "id": id,
            "title": title,
            "importance": parseFloat(importance)
        };
        socket.sendTextMessage(JSON.stringify(msg));
    }

    function deleteItem(id) {
        if (!root.isConnected) {
            console.log("[NexusService] Cannot delete item: socket is disconnected.");
            return;
        }
        var msg = {
            "action": "delete",
            "id": id
        };
        socket.sendTextMessage(JSON.stringify(msg));
    }
}
