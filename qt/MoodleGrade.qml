import QtQuick 1.1



Rectangle {
    id: rectangle1
    width: 700
    height: 900
    color: "#2b2828"

    Column {
        id: column1
        anchors.fill: parent

        Item {
            id: item1
            x: 0
            width: rectangle1.width
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
                text: qsTr("Text")
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
                }
            }

            TextInput {
                id: input_test
                x: 56
                y: 107
                width: item1.width - (x + 106 + 20)
                height: 20
                color: "#a6a4a4"
                text: qsTr("Text")
                font.pointSize: 11

                Button {
                    id: btn_test
                    x: input_test.width + 10
                    y: -15
                    smooth: true
                    prompt: "Browse..."
                }

                Text {
                    id: text4
                    x: 0
                    y: -26
                    color: "#ffffff"
                    text: qsTr("Configuration Folder (Default: Grading folder)")
                    font.pointSize: 13
                }
            }

            Button {
                id: btn_start
                x: rectangle1.width /3
                y: 139
                width: item1.width * .3
                height: 35
                prompt: "Start"
            }
        }

        StudentPanel {
            id: mainPanel
            width: rectangle1.width

        }



        Item {
            id: item2
            x: 0
            y: 580
            width: 700
            height: 300

            ListView {
                id: lst_tests
                x: 29
                y: 70
                width: 221
                height: 160
                delegate: Item {
                    width: lst_tests.width
                    height: 12

                    Text {
                        text: name
                    }
                    Text {
                        text: score + '/' + possible
                        x: lst_tests.width - 30
                    }
                }

                model: ListModel {
                    ListElement {
                        name: "Grey"
                        score: 0
                        possible: 0
                    }

                    ListElement {
                        name: "Red"
                        score: 0
                        possible: 0
                    }

                    ListElement {
                        name: "Blue"
                        score: 0
                        possible: 0
                    }

                    ListElement {
                        name: "Green"
                        score: 0
                        possible: 0
                    }
                }

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
                id: button1
                x: 256
                y: 8
                width: 189
                height: 35
                prompt: "View Output"

                onClicked: {
                    if (mainPanel.state == "")
                        mainPanel.state = "output"
                    else
                        mainPanel.state = ""

                }
            }

            ListView {
                id: list_view1
                x: 458
                y: 70
                width: 217
                height: 160
                highlightRangeMode: ListView.NoHighlightRange
                delegate: Item {
                    x: 5
                    height: 15
                    Row {
                        id: row1
                        Text {
                            text: name
                            font.bold: true
                            font.pointSize: 13
                        }
                    }
                }
                model: ListModel {
                    ListElement {
                        name: "Grey"
                        colorCode: "grey"
                    }

                    ListElement {
                        name: "Red"
                        colorCode: "red"
                    }

                    ListElement {
                        name: "Blue"
                        colorCode: "blue"
                    }

                    ListElement {
                        name: "Green"
                        colorCode: "green"
                    }
                }

                Text {
                    id: text3
                    x: 141
                    y: -36
                    color: "#959393"
                    text: qsTr("Outputs")
                    font.pointSize: 14
                }
            }
        }
    }


}
