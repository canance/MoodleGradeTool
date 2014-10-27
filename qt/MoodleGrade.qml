import QtQuick 1.1



Rectangle {
    id: rectangle1
    width: 983
    height: 900
    color: "#2b2828"

    signal studentSelected(int id)
    signal parseTests()
    signal setupTests()
    signal startTesting()
    signal gradeFolderBrowse()
    signal testFolderBrowse()

    property string gradeFolder: input_grade.text
    property string testFolder: chkUseGrade.checked?gradeFolder:input_test.text
    property QtObject testList: ListModel{}
    property QtObject studentsList: ListModel {}
    property QtObject outputs: ListModel {}
    property QtObject testResults: ListModel {}

    function updateStudents(list){
        studentsList = list
    }

    function updateOutputs(list){
        outputs = list
    }

    function updateTestResults(list){
        testResults = list
    }

    function updateGradeFolder(path){
        input_grade.text = path
    }

    function updateTestFolder(path){
        input_test.text = path
    }

    function updateTestList(list){
        testList = list
    }


    Column {
        id: column1
        width: rectangle1.width - 295
        height: parent.height
        z: 1

        Item {
            id: item1
            x: 0
            width: column1.width
            height: 200
            anchors.top: parent.top
            anchors.topMargin: 0

            TextInput {
                id: input_grade
                x: 56
                y: 52
                width: item1.width - (x + 106 + 20)
                height: 20
                color: "#a6a4a4"
                text: "/tmp/grade"
                font.pointSize: 11

                Text {
                    id: text1
                    x: 0
                    y: -26
                    color: "#ffffff"
                    text: qsTr("Grading Folder")
                    font.pointSize: 13
                }

                Button {
                    id: btn_grade
                    x: input_grade.width + 10
                    y: -7
                    smooth: true
                    prompt: "Browse..."
                    onClicked: {
                        gradeFolderBrowse()
                    }
                }
            }

            TextInput {
                id: input_test
                x: 56
                y: 107
                width: item1.width - (x + 106 + 20)
                height: 20
                color: chkUseGrade.checked?"#FFFFFF":"#a6a4a4"
                text: "/tmp/"
                font.italic: chkUseGrade.checked
                readOnly: chkUseGrade.checked
                font.pointSize: 11

                Button {
                    id: btn_test
                    x: input_test.width + 10
                    y: -15
                    smooth: true
                    prompt: "Browse..."
                    enabled: !chkUseGrade.checked
                    onClicked: {
                        testFolderBrowse()
                    }

                }

                Text {
                    id: text4
                    x: 0
                    y: -26
                    color: "#ffffff"
                    text: qsTr("Configuration Folder")
                    font.pointSize: 13
                }

                CheckBox {
                    id: chkUseGrade
                    x: 187
                    y: -58
                    text: "Use grading folder"
                    checked: true
                    anchors.verticalCenter: text4.verticalCenter

                }
            }

            Button {
                id: btn_start
                x: 206
                y: 142
                width: item1.width * .2
                height: 41
                anchors.horizontalCenterOffset: -(width/2 + 5)
                anchors.horizontalCenter: parent.horizontalCenter
                prompt: "Start"
                enabled: false
                onClicked: {
                    startTesting()
                }
            }

            Button {
                id: button1
                x: 345
                y: 142
                width: parent.width * .2
                height: 41
                prompt: "Reload\n Configuration"
                anchors.horizontalCenterOffset: (width/2 + 5)
                anchors.horizontalCenter: parent.horizontalCenter

                onClicked: {
                    parseTests()
                }
            }
        }

        StudentPanel {
            id: mainPanel
            width: column1.width
            clip: false
            students: studentsList

            onCurrentStudentChanged: {
                studentSelected(currentStudent)
            }

        }



        Item {
            id: item2
            x: 0
            y: 580
            width: column1.width
            height: 300

            ListView {
                id: lst_tests
                x: 29
                y: 70
                width: btnOutput.x - x -5
                height: 160
                delegate: Item {
                    width: lst_tests.width
                    height: 12

                    Text {
                        text: Obj.name
                    }
                    Text {
                        text: Obj.score + '/' + Obj.possible
                        x: lst_tests.width - 30
                    }
                }

                model: testResults

                Text {
                    id: text2
                    x: 0
                    y: -31
                    color: "#959393"
                    text: qsTr("Test Results")
                    style: Text.Normal
                    font.pointSize: 14
                }
            }

            Button {
                id: btnOutput
                x: 261
                y: 8
                width: 189
                height: 35
                anchors.horizontalCenter: parent.horizontalCenter
                prompt: "View Output"

                onClicked: {
                    if (mainPanel.state == "")
                        mainPanel.state = "output"
                    else
                        mainPanel.state = ""

                }
            }

            ListView {
                id: lstOuputs
                x: btnOutput.x+btnOutput.width+15
                y: 70
                width: parent.width - x - 20
                height: 160
                highlightRangeMode: ListView.NoHighlightRange
                delegate: Item {
                    height: 15
                    width: lstOuputs.width

                    Text {
                        id: txtOutName
                        text: Obj.name
                    }

                    property bool currentItm: ListView.isCurrentItem

                    Binding {
                        target: mainPanel
                        property: "sourceText"
                        value: Obj.output
                        when: currentItm
                    }

                }

                model: outputs

                Text {
                    id: text3
                    x: parent.width - width
                    y: -36
                    color: "#959393"
                    text: qsTr("Outputs")
                    font.pointSize: 14
                }
            }
        }
    }

    Rectangle {
        id: rectangle2
        x: column1.x
        y: column1.y
        width: column1.width
        height: column1.height
        radius: 3
        smooth: true
        gradient: Gradient {
            GradientStop {
                position: 0
                color: "#a6a5a5"
            }

            GradientStop {
                position: 0.02
                color: "#383535"
            }

            GradientStop {
                position: 0.97
                color: "#383535"
            }

            GradientStop {
                position: 1
                color: "#a6a5a5"
            }
        }
        z: 0
    }

    ListView {
        id: lstTests
        x: column1.width + 30
        y: 82
        width: 243
        height: 592
        smooth: false
        z: 2
        spacing: 1
        delegate: CheckBox{
            id: chkTest
            text: name
            property QtObject object: Obj
            onCheckedChanged: {
                btnChangeTests.enabled = true
                object.selected = checked
            }
        }

        model: testList

        Text {
            id: text5
            x: 0
            y: -36
            color: "#ffffff"
            text: qsTr("Tests")
            font.bold: true
            font.pointSize: 14
        }

        Button {
            id: btnChangeTests
            x: 40
            y: 605
            width: 163
            height: 35
            prompt: "Change Selection"
            enabled: false

            onClicked: {
                setupTests()
                btn_start.enabled = true
            }
        }
    }
}
