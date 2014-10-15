import QtQuick 1.1

Item{
    id: check1
    height: 40

    property bool checked: false
    property string text: "Checkbox"
    property color textColor: "#777777"
    property color uncheckedColor: "#a8a4a4"
    property color checkedColor: "#004684"
    width: text1.width + text1.x

    onCheckedChanged: {
        if (checked && state != "checked"){
            state = "checked"
        }
        else if (!checked && state != ""){
            state = ""
        }
    }

    Rectangle {
        id: rectangle1
        x: 8
        y: 11
        width: 15
        height: 15
        color: uncheckedColor
        border.width: 2
        border.color: "#000000"

        MouseArea {
            id: mouse1
            anchors.fill: parent

            onClicked: {
                if (check1.state == "")
                    check1.state = "checked"
                else
                    check1.state = ""
            }
        }
    }

    Text {
        id: text1
        x: 34
        y: 12
        color: textColor
        text: check1.text
        font.pointSize: 12
        font.pixelSize: 12
    }
    states: [
        State {
            name: "checked"

            PropertyChanges {
                target: check1
                checked: true
            }

            PropertyChanges {
                target: rectangle1
                color: checkedColor
            }

            PropertyChanges {
                target: text1
                font.bold: true
            }
        }
    ]
}
