import QtQuick 1.1

Item{
    id: mainPanel
    x:0
    y:0
    height: 400

    property QtObject students: ListModel {
        ListElement {
            name: "Student"
            status_name: "Finished"
            totalScore: 0
            totalPossible: 1
            flag: "ready"
            studentID: 1
        }
        ListElement {
            studentName: "Student"
            status_name: "Error"
            totalScore: 0
            totalPossible: 1
            flag: "error"
            studentID: 2
        }
        ListElement {
            studentName: "Student"
            status_name: "Testing"
            totalScore: 0
            totalPossible: 1
            studentID: 3
        }
        ListElement {
            studentName: "Student"
            status_name: "Testing"
            totalScore: 0
            totalPossible: 1
            studentID: 4
        }
        ListElement {
            studentName: "Student"
            status_name: "Testing"
            totalScore: 0
            totalPossible: 1
            studentID: 5
        }
        ListElement {
            studentName: "Student"
            status_name: "Testing"
            totalScore: 0
            totalPossible: 1
            studentID: 6
        }
        ListElement {
            studentName: "Student"
            status_name: "Testing"
            totalScore: 0
            totalPossible: 1
            studentID: 7
        }
        ListElement {
            studentName: "Student"
            status_name: "Testing"
            totalScore: 0
            totalPossible: 1
            studentID: 8

        }
        ListElement {
            studentName: "Student"
            status_name: "Testing"
            totalScore: 0
            totalPossible: 1
            studentID: 9

        }
       }

    property int currentStudent: -1
    property string sourceText: "Source goes here"
    signal selectedChanged

    function changeSelect(sender){
        currentStudent = sender
        selectedChanged()
    }

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
            id: stud1
            disp_name: studentObj.studentName
            disp_status: studentObj.status_name
            disp_score: studentObj.totalScore
            disp_possible: studentObj.totalPossible
            static_state: studentObj.flag
            std_id: studentObj.studentID
            width: (grd_students.cellWidth - 15)
            height: (grd_students.cellHeight - 15)

            Connections{
                target: mainPanel
                onCurrentStudentChanged: stud1.handleSelected(currentStudent)
            }

            onWasSelected: {
                changeSelect(std_id)
            }

        }

        model: students
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
            text: mainPanel.sourceText
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
