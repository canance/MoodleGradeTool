import QtQuick 1.1



Rectangle {
    id: rectangle1
    width: 983
    height: 900
    color: "#2b2828"

    //Signals to fire when our state is changed (typically alerts python code)
    signal studentSelected(int id)
    signal parseTests()  //When Reload Configuration button is pressed
    signal setupTests()  //When Change Selection button is pressed
    signal startTesting() //When start button is pressed
    signal gradeFolderBrowse() //When browse button for the grading folder is pressed
    signal testFolderBrowse()  //When browse button for the configuration folder is pressed

    //Properties
    property string gradeFolder: input_grade.text //The actual grading folder
    //Select between test folder path and grade folder path when chkUseGrade is checked
    property string testFolder: chkUseGrade.checked?gradeFolder:input_test.text
    property QtObject testList: ListModel{} //The available tests
    property QtObject studentsList: ListModel {} //The list of all the students
    property QtObject outputs: ListModel {}  //The available outputs
    property QtObject testResults: ListModel {} //The test results

    //These functions are called from python to update certain things
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

    //Arranges widgets in a column
    Column {
        id: column1
        width: rectangle1.width - 295 //Set with to the parent, but leaves space for the tests list
        height: parent.height
        z: 1

        //Item for the top third of the column
        //Holds: Test selector, grading selector, and Reload and Start buttons
        Item {
            id: item1
            x: 0
            width: column1.width //Set width to the parents
            height: 200
            anchors.top: parent.top
            anchors.topMargin: 0

            //Text box for the grading folder
            //Holds: Label and browse button
            TextInput {
                id: input_grade
                x: 56
                y: 52
                width: item1.width - (x + 106 + 20)  //Set width to parent but leaves space for button and spacing
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
                        gradeFolderBrowse()  //Fires signal to show file dialog
                    }
                }
            }

            //Text box for the configuration or tests folder
            //Almost identical to the setup for the grading folder text box
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

            //Start button
            Button {
                id: btn_start
                x: 206
                y: 142
                width: item1.width * .2 //Buttons width is %20 of parents
                height: 41
                //Offset from center by half our width (makes space for two buttons)
                anchors.horizontalCenterOffset: -(width/2 + 5)
                //Align our center with our parents center
                anchors.horizontalCenter: parent.horizontalCenter
                prompt: "Start"
                enabled: false //We don't start off enabled
                onClicked: {
                    startTesting()  //Fire signal to start testing
                }
            }

            //Button to load the configuration
            Button {
                id: button1
                x: 345
                y: 142
                //See start button for explanation for these properties
                width: parent.width * .2
                height: 41
                prompt: "Reload\n Configuration"
                anchors.horizontalCenterOffset: (width/2 + 5)
                anchors.horizontalCenter: parent.horizontalCenter

                onClicked: {
                    parseTests()  //Fire signal to parse test configurations
                }
            }
        }

        //The students panel, this constitutes the middle section of the main column
        StudentPanel {
            id: mainPanel
            width: column1.width
            clip: false
            students: studentsList //The panel gets is students source from the student list property

            onCurrentStudentChanged: {
                studentSelected(currentStudent) //Fire student selected signal with the id of the selected student
            }

        }


        //The bottom section of the main column
        Item {
            id: item2
            x: 0
            y: 580
            width: column1.width
            height: 300

            //The test results list
            ListView {
                id: lst_tests
                x: 29
                y: 70
                //Our width is from our x position to the Show Output button with a 5 pixel spacing
                width: btnOutput.x - x -5
                height: 160

                //How to show each item in our list
                delegate: Item {
                    width: lst_tests.width
                    height: 12

                    //Text box with the tests name
                    Text {
                        text: Obj.name
                    }

                    //Text box with the tests score
                    Text {
                        text: Obj.score + '/' + Obj.possible
                        x: lst_tests.width - 30
                    }
                }

                //Our data comes from the testResults property
                model: testResults

                //Label
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

            //Switches between the mainPanel's two states (student list and output)
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

            //Show the available outputs
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

    //The background for the column
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

    //Shows the available tests
    ListView {
        id: lstTests
        x: column1.width + 30
        y: 82
        width: 243
        height: 592
        smooth: false
        z: 2
        spacing: 1

        //We show each test as a checkbox
        delegate: CheckBox{
            id: chkTest
            text: name
            //Create local binding for the Obj field in the provided data model
            property QtObject object: Obj

            onCheckedChanged: {
                btnChangeTests.enabled = true //Enable the tests changed button
                object.selected = checked //Toggle the objects selected property
            }
        }

        //Our list comes from the testList property
        model: testList

        //Label
        Text {
            id: text5
            x: 0
            y: -36
            color: "#ffffff"
            text: qsTr("Tests")
            font.bold: true
            font.pointSize: 14
        }

        //Button to handle test selection changes
        Button {
            id: btnChangeTests
            x: 40
            y: 605
            width: 163
            height: 35
            prompt: "Change Selection"
            enabled: false //Start off disabled

            onClicked: {
                setupTests()  //Fire signal to setup the selected tests
                btn_start.enabled = true  //Allow testing to begin
            }
        }
    }
}
