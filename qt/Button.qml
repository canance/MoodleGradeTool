import QtQuick 1.1

Rectangle {
    id: btn1
    x: 0
    y: 0
    width: 106
    height: 35
    radius: 9
    gradient: Gradient {
        GradientStop {
            id: gradtop
            position: 0
            color: "#c4c3c3"
        }

        GradientStop {
            id: gradbottom
            position: 1
            color: "#083641"
        }
    }

    signal clicked()

    property string prompt: "Click Here"

    Text {
        id: txt_text
        text: prompt
        horizontalAlignment: Text.AlignHCenter
        font.bold: false
        smooth: true
        verticalAlignment: Text.AlignVCenter
        anchors.fill: parent
        font.pointSize: 12
    }

    MouseArea {
        id: mousearea1
        hoverEnabled: true
        anchors.fill: parent
        onClicked: {
            btn1.clicked()
        }

        onPressed: {
            btn1.state = "pressed"
        }

        onReleased: {
            if (mousearea1.containsMouse){
                btn1.state = "hover"
            }
            else
                btn1.state = ""
        }

        onHoveredChanged: {
            if (btn1.state == "")
                btn1.state = "hover"
            else
                btn1.state = ""
        }
    }
    states: [
        State {
            name: "hover"
            PropertyChanges {
                target: gradtop
                color: "#ffffff"

            }
        },
        State {
            name: "pressed"

            PropertyChanges {
                target: gradtop
                position: 1

            }
            PropertyChanges {
                target: gradbottom
                position: 0

            }
        }
    ]
}
