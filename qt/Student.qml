import QtQuick 1.1

Rectangle {
    id: rectangle1
    width: 300
    height: 100
    radius: 11
    border.width: 0
    border.color: "#C5B9AB"
    gradient: Gradient {
        GradientStop {
            id: gradtop
            position: 0
            color: "#8d7f7f"
        }

        GradientStop {
            id: gradbottom
            position: 1
            color: "#201e1e"
        }
    }
    visible: true
    smooth: true

    property string static_state: ""
    property string disp_name: "Student Name"
    property string disp_status: "Waiting to build"
    property int disp_score: 0
    property int disp_possible: 0
    state: static_state

    MouseArea{
        id: rect1_mouse
        anchors.fill: parent
        hoverEnabled: true
        onHoveredChanged: {
            if (rectangle1.state == rectangle1.static_state)
                rectangle1.state = "mouse_over"
            else
                rectangle1.state = rectangle1.static_state
        }
    }



    Text {
        id: txt_name
        x: 8
        y: 8
        text: disp_name
        font.pointSize: 19

    }



    Text {
        id: text1
        x: 8
        y: 43
        text: qsTr("Status: ")
        font.pointSize: 11

    }


    Text {
        id: txt_status
        x: 72
        y: 43
        text: disp_status
        font.pointSize: 11

    }

    Text {
        id: text3
        x: 8
        y: 67
        text: qsTr("Score: ")
        font.pointSize: 10

    }


    Text {
        id: txt_score
        x: 64
        y: 68
        text: disp_score + '/' + disp_possible
        font.bold: true
        font.pointSize: 13

    }

    states: [
        State {
            name: "mouse_over"
            PropertyChanges {
                target: rectangle1
                border.width: 2
            }
            PropertyChanges {
                target: gradtop
                color: "#AFBDD4"

            }

        },
        State {
            name: "error"
            PropertyChanges {
                target: gradtop
                color: "#C13434"
            }
        },
        State {
            name: "ready"
            PropertyChanges {
                target: gradtop
                color: "#799279"

            }
        },
        State {
            name: "selected"
            PropertyChanges {
                target: gradtop
                color: "#CBB7B7"

            }
            PropertyChanges {
                target: gradbottom
                color: "#4D4848"
            }

            PropertyChanges {
                target: rect1_mouse
                z: 2
            }
        }

    ]

    transitions: [
        Transition {
            to: "*"
            ColorAnimation { target: gradtop; duration: 100 }

        }
    ]
}
