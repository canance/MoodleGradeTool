import QtQuick 1.1

Rectangle {
    id: btn1
    x: 0
    y: 0
    width: 106
    height: 35
    radius: 9
    smooth: true
    gradient: Gradient {
        GradientStop {
            id: gradtop
            position: 0
            color: "#9bb7c2"
        }

        GradientStop {
            id: gradbottom
            position: 1
            color: "#083641"
        }
    }

    signal clicked()

    property string prompt: "Click Here"
    property bool enabled: true

    onEnabledChanged: {
        if (enabled)
            state = ""
        else
            state = "disabled"
    }

    Text {
        id: txt_text
        text: prompt
        horizontalAlignment: Text.AlignHCenter
        font.bold: true
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
        },
        State {
            name: "disabled"

            PropertyChanges {
                target: mousearea1
                hoverEnabled: false
                enabled: false
            }

            PropertyChanges {
                target: gradbottom
                color: "#414141"
            }

            PropertyChanges {
                target: txt_text
                color: "#555555"
                font.bold: false
                style: "Sunken"
            }
        }
    ]
}
