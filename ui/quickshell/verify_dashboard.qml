import QtQuick 2.15
import QtQuick.Window 2.15

Window {
    visible: true
    width: 450
    height: 650
    title: "NEXUS-X Quickshell Dashboard Mock"
    color: "#12121a"

    // Instantiate persistent WebSocket Client Service
    NexusService {
        id: nexusService
        socketUrl: "ws://localhost:8000/crud"
    }

    // Embed the Reusable List View Pill
    ListViewPill {
        anchors.fill: parent
        anchors.margins: 10
        service: nexusService
    }
}
