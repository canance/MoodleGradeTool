import QtQuick 1.1

Item{
    id: mainPanel
    x:0
    y:0
    height: 400

    property ListModel students: ListModel {}
    property Student currentStudent: grd_students.currentItem

    GridView {
        id: grd_students
        x: 5
        y: 5
        width: mainPanel.width
        height: mainPanel.height
        cellWidth: (grd_students.width - 30) / 2
        cellHeight: (grd_students.height - 40) / 3
        visible: true
        clip: false
        opacity: 1
        flow: GridView.TopToBottom
        z: 0


        delegate: Student {
            disp_name: name
            disp_status: status_name
            disp_score: score
            disp_possible: possible
            static_state: flag
            width: (grd_students.cellWidth - 15)
            height: (grd_students.cellHeight - 15)


        }
        model: ListModel {
            ListElement {
                name: "Student"
                status_name: "Finished"
                score: 0
                possible: 1
                flag: "ready"
            }
            ListElement {
                name: "Student"
                status_name: "Error"
                score: 0
                possible: 1
                flag: "error"
            }
            ListElement {
                name: "Student"
                status_name: "Testing"
                score: 0
                possible: 1
            }
            ListElement {
                name: "Student"
                status_name: "Testing"
                score: 0
                possible: 1
            }
            ListElement {
                name: "Student"
                status_name: "Testing"
                score: 0
                possible: 1
            }
            ListElement {
                name: "Student"
                status_name: "Testing"
                score: 0
                possible: 1
            }
            ListElement {
                name: "Student"
                status_name: "Testing"
                score: 0
                possible: 1
            }
            ListElement {
                name: "Student"
                status_name: "Testing"
                score: 0
                possible: 1

            }
            ListElement {
                name: "Student"
                status_name: "Testing"
                score: 0
                possible: 1

            }
           }
    }

    Rectangle{
        id: txtPanel
        color: "white"
        radius: 10
        z: -1
        scale: 0.1
        anchors.rightMargin: 5
        anchors.leftMargin: 5
        anchors.bottomMargin: 5
        anchors.topMargin: 5
        anchors.fill: parent
        visible: true
        opacity: 0
        clip: true
        border.width: 3
        border.color: "#6974a8"


        TextEdit {
            id: text_edit1
            readOnly: true
            text: qsTr("Text Edit")
            textFormat: TextEdit.RichText
            anchors.rightMargin: 5
            anchors.leftMargin: 4
            anchors.bottomMargin: 5
            anchors.topMargin: 6
            anchors.fill: parent
            font.pixelSize: 12
        }
    }

    states: [
        State {
            name: "output"

            PropertyChanges {
                target: txtPanel
                scale: 1
                opacity: 1
            }

            PropertyChanges {
                target: grd_students
                x: mainPanel.width + 16
                opacity: 0
            }
        }
    ]

    transitions: [
        Transition {
            to: '*'
            PropertyAnimation {
                target: [grd_students, txtPanel]
                properties: "opacity"
                duration: 500
            }
            PropertyAnimation {
                target: [grd_students, txtPanel]
                properties: "x"
                duration: 500
            }
            PropertyAnimation {
                target: [grd_students, txtPanel]
                properties: "y"
                duration: 500
            }

            PropertyAnimation {
                target: txtPanel
                property: "scale"
                duration: 500
            }

        }

    ]


}
