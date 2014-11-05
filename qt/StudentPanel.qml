import QtQuick 1.1

Item{
    id: mainPanel
    x:0
    y:0
    width: 100
    height: 400

    //The students list
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


    property int currentStudent: -1 //The id of the selected student
    property string sourceText: "Source goes here" //The text that goes in the source text box
    signal selectedChanged //Signal that the selected student changed

    function changeSelect(sender){
        currentStudent = sender //Change the current student property
        selectedChanged() //Fire selected changed signal
    }

    //Students list view
    GridView {
        id: grd_students
        x: 5
        y: 5
        width: mainPanel.width - 5
        height: mainPanel.height
        cellWidth: (grd_students.width - 30) / 2
        cellHeight: (grd_students.height - 40) / 3
        visible: true
        clip: true
        opacity: 1
        flow: GridView.TopToBottom
        z: 0

        //Object to create for each item in model
        delegate: Student {
            id: stud1

            //Property bindings
            disp_name: studentObj.studentName
            disp_status: studentObj.status_name
            disp_score: studentObj.totalScore
            disp_possible: studentObj.totalPossible
            static_state: studentObj.flag
            std_id: studentObj.studentID

            width: (grd_students.cellWidth - 15)
            height: (grd_students.cellHeight - 15)

            //Connect Current Student property change to each student's handleSelected method
            Connections{
                target: mainPanel
                onCurrentStudentChanged: stud1.handleSelected(currentStudent)
            }

            //Call changeSelect function on this students wasSelected signal
            onWasSelected: {
                changeSelect(std_id)
            }

        }

        //Set data model to students
        model: students
    }

    //Output text box
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

        Flickable{
            id: flick1
            contentWidth: text_edit1.paintedWidth
            contentHeight: text_edit1.paintedHeight
            anchors.fill: parent
            anchors.rightMargin: 5
            anchors.leftMargin: 4
            anchors.bottomMargin: 5
            anchors.topMargin: 6
            clip: true

            //Text box for output
            TextEdit {
                id: text_edit1
                readOnly: true
                text: mainPanel.sourceText
                textFormat: TextEdit.AutoText

                anchors.fill: parent
                font.pixelSize: 12
            }
        }


    }

    //States
    states: [
        //Shows the output textbox
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

    //Animate panel change
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
