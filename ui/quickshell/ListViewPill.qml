import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    implicitWidth: 380
    implicitHeight: 600

    // Reference to the persistent WebSocket service instance
    property var service: null

    // Optimistic data list that binds to service.dataList but updates instantly on user input
    property var localDataList: []

    // Sync local list whenever backend sends updates
    onServiceChanged: {
        if (service) {
            root.localDataList = service.dataList;
        }
    }

    Connections {
        target: root.service
        ignoreUnknownSignals: true
        function onDataListChanged() {
            root.localDataList = root.service.dataList;
        }
    }

    // Outer Shell Container (Cartoon Aesthetic: Thick borders, solid pastel canvas)
    Rectangle {
        id: container
        anchors.centerIn: parent
        width: 360
        height: 580
        radius: 32
        color: "#F4F1DE" // Soft cream canvas background
        border.color: "#000000"
        border.width: 4
        clip: true

        // Top Status Header (Pill-shaped, thick borders, pastel yellow)
        Rectangle {
            id: header
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 60
            color: "#F2CC8F" // Pastel Orange/Yellow
            radius: 30 // Fully rounded pill ends
            border.color: "#000000"
            border.width: 3
            anchors.margins: 12

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 20
                anchors.rightMargin: 20
                spacing: 10

                // Connection status dot
                Rectangle {
                    width: 16
                    height: 16
                    radius: 8
                    color: root.service && root.service.isConnected ? "#3A0CA3" : "#F72585"
                    border.color: "#000000"
                    border.width: 2

                    SequentialAnimation on scale {
                        loops: Animation.Infinite
                        running: root.service && root.service.isConnected
                        NumberAnimation { from: 1.0; to: 1.2; duration: 600; easing.type: Easing.InOutQuad }
                        NumberAnimation { from: 1.2; to: 1.0; duration: 600; easing.type: Easing.InOutQuad }
                    }
                }

                Label {
                    text: root.service ? root.service.activeAgent : "Offline"
                    font.family: "Courier New"
                    font.pixelSize: 18
                    font.bold: true
                    color: "#000000"
                    Layout.fillWidth: true
                }

                // Thinking Indicator (Pulsing Orb)
                Rectangle {
                    width: 24
                    height: 24
                    radius: 12
                    color: "#4CC9F0"
                    border.color: "#000000"
                    border.width: 2
                    opacity: root.service && root.service.isThinking ? 1.0 : 0.0
                    visible: opacity > 0.0
                    
                    Behavior on opacity {
                        NumberAnimation { duration: 150 }
                    }

                    SequentialAnimation on scale {
                        loops: Animation.Infinite
                        running: root.service && root.service.isThinking
                        NumberAnimation { from: 0.8; to: 1.3; duration: 400; easing.type: Easing.InOutBack }
                        NumberAnimation { from: 1.3; to: 0.8; duration: 400; easing.type: Easing.InOutBack }
                    }
                }
            }
        }

        // Add Item Form Pill (Pastel Teal, capsule shape)
        Rectangle {
            id: addForm
            anchors.top: header.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            height: 70
            color: "#81B29A" // Pastel Teal
            radius: 35 // Capsule Shape
            border.color: "#000000"
            border.width: 3
            anchors.margins: 12

            RowLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8

                // Title Input
                TextField {
                    id: titleInput
                    placeholderText: "New Memory..."
                    placeholderTextColor: "#4a4a4a"
                    color: "#000000"
                    font.bold: true
                    font.pixelSize: 12
                    font.family: "Courier New"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 38
                    verticalAlignment: TextInput.AlignVCenter
                    leftPadding: 16
                    background: Rectangle {
                        color: "#FFFFFF"
                        radius: 19 // Capsule Shape
                        border.color: "#000000"
                        border.width: titleInput.activeFocus ? 3 : 2
                    }
                }

                // Importance Input
                TextField {
                    id: importanceInput
                    placeholderText: "0.8"
                    placeholderTextColor: "#4a4a4a"
                    color: "#000000"
                    font.bold: true
                    font.pixelSize: 12
                    font.family: "Courier New"
                    Layout.preferredWidth: 46
                    Layout.preferredHeight: 38
                    horizontalAlignment: TextInput.AlignHCenter
                    verticalAlignment: TextInput.AlignVCenter
                    background: Rectangle {
                        color: "#FFFFFF"
                        radius: 19 // Capsule Shape
                        border.color: "#000000"
                        border.width: importanceInput.activeFocus ? 3 : 2
                    }
                }

                // Add Button (Pastel Purple, capsule shape with bounce)
                Button {
                    id: addButton
                    text: "+"
                    Layout.preferredWidth: 38
                    Layout.preferredHeight: 38
                    contentItem: Label {
                        text: addButton.text
                        font.bold: true
                        font.pixelSize: 22
                        color: "#FFFFFF"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        color: addButton.hovered ? "#3F37C9" : "#4895EF"
                        radius: 19 // Capsule Shape
                        border.color: "#000000"
                        border.width: 2
                        scale: addButton.pressed ? 0.85 : 1.0
                        Behavior on scale { NumberAnimation { duration: 100; easing.type: Easing.OutBack } }
                    }

                    onClicked: {
                        if (titleInput.text.trim() === "" || !root.service) return;

                        var val = parseFloat(importanceInput.text) || 0.5;
                        var optTitle = titleInput.text;

                        // OPTIMISTIC UPDATE
                        var tempId = "temp_" + Date.now();
                        var optimisticItem = { "id": tempId, "title": optTitle, "importance": val, "optimistic": true };
                        var currentList = Array.from(root.localDataList);
                        currentList.push(optimisticItem);
                        root.localDataList = currentList;

                        // Send WebSocket CRUD event
                        root.service.createItem(optTitle, val);

                        // Clear Input
                        titleInput.text = "";
                        importanceInput.text = "0.8";
                    }
                }
            }
        }

        // List View of Items
        ListView {
            id: listView
            anchors.top: addForm.bottom
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 12
            spacing: 8
            model: root.localDataList
            clip: true

            delegate: Item {
                id: delegateRoot
                width: listView.width
                height: 60
                opacity: modelData.optimistic ? 0.6 : 1.0

                // Slide-in and Scale transition for new items
                Component.onCompleted: {
                    slideInAnimation.start();
                }

                ParallelAnimation {
                    id: slideInAnimation
                    NumberAnimation { target: delegateRoot; property: "scale"; from: 0.6; to: 1.0; duration: 250; easing.type: Easing.OutBack }
                    NumberAnimation { target: delegateRoot; property: "opacity"; from: 0.0; to: 1.0; duration: 200 }
                }

                // Outer delegate card pill (Thick border, capsule shape)
                Rectangle {
                    anchors.fill: parent
                    radius: 30 // Capsule Shape
                    color: modelData.optimistic ? "#E2E2E2" : "#F4F1DE"
                    border.color: "#000000"
                    border.width: 3

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 18
                        anchors.rightMargin: 18
                        spacing: 8

                        // Colored Bullet Indicator (Pastel color dot matching importance)
                        Rectangle {
                            width: 12
                            height: 12
                            radius: 6
                            color: modelData.importance >= 0.8 ? "#E76F51" : (modelData.importance >= 0.5 ? "#2A9D8F" : "#E9C46A")
                            border.color: "#000000"
                            border.width: 2
                        }

                        // Content description
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 1
                            
                            Label {
                                text: modelData.title
                                font.family: "Courier New"
                                font.pixelSize: 13
                                font.bold: true
                                color: "#000000"
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                            Label {
                                text: "Importance: " + modelData.importance.toFixed(2)
                                font.family: "Courier New"
                                font.pixelSize: 10
                                color: "#4a4a4a"
                            }
                        }

                        // Actions Row (Edit & Delete Capsule buttons)
                        RowLayout {
                            spacing: 6

                            // Edit Button
                            Button {
                                id: editBtn
                                text: "EDIT"
                                Layout.preferredHeight: 28
                                contentItem: Label {
                                    text: editBtn.text
                                    color: "#000000"
                                    font.bold: true
                                    font.pixelSize: 10
                                    font.family: "Courier New"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                background: Rectangle {
                                    color: editBtn.hovered ? "#E9C46A" : "#F4A261"
                                    radius: 14 // Capsule
                                    border.color: "#000000"
                                    border.width: 2
                                    scale: editBtn.pressed ? 0.9 : 1.0
                                    Behavior on scale { NumberAnimation { duration: 80 } }
                                }
                                onClicked: {
                                    var newTitle = modelData.title + " (Edited)";
                                    var newImportance = Math.min(1.0, modelData.importance + 0.1);
                                    
                                    // OPTIMISTIC UPDATE
                                    var currentList = Array.from(root.localDataList);
                                    for (var i = 0; i < currentList.length; i++) {
                                        if (currentList[i].id === modelData.id) {
                                            currentList[i].title = newTitle;
                                            currentList[i].importance = newImportance;
                                            currentList[i].optimistic = true;
                                            break;
                                        }
                                    }
                                    root.localDataList = currentList;

                                    if (root.service) {
                                        root.service.updateItem(modelData.id, newTitle, newImportance);
                                    }
                                }
                            }

                            // Delete Button
                            Button {
                                id: delBtn
                                text: "×"
                                Layout.preferredHeight: 28
                                Layout.preferredWidth: 28
                                contentItem: Label {
                                    text: delBtn.text
                                    color: "#FFFFFF"
                                    font.bold: true
                                    font.pixelSize: 18
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                background: Rectangle {
                                    color: delBtn.hovered ? "#E76F51" : "#E63946"
                                    radius: 14 // Capsule
                                    border.color: "#000000"
                                    border.width: 2
                                    scale: delBtn.pressed ? 0.9 : 1.0
                                    Behavior on scale { NumberAnimation { duration: 80 } }
                                }
                                onClicked: {
                                    // OPTIMISTIC UPDATE
                                    var currentList = Array.from(root.localDataList);
                                    currentList = currentList.filter(function(item) {
                                        return item.id !== modelData.id;
                                    });
                                    root.localDataList = currentList;

                                    if (root.service) {
                                        root.service.deleteItem(modelData.id);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
