import QtQuick 1.1

Item{
    id: check1

    //Exposed properties
    property bool checked: false //If we're checked
    property string text: "Checkbox" //The text box
    property color textColor: "#777777"  //The text color
    property color uncheckedColor: "#a8a4a4" //The box's background color when unchecked
    property color checkedColor: "#004684" //The box's background color when checked


    width: text1.width + text1.x //Our width is based on our text box's size
    //Our height is determined by our largest element
    height: (rectangle1.height + rectangle1.y) > (text1.height + text1.y)?(rectangle1.height + rectangle1.y):(text1.height + text1.y)

    //Change our state based on changes in checked
    onCheckedChanged: {
        if (checked && state != "checked"){
            state = "checked"
        }
        else if (!checked && state != ""){
            state = ""
        }
    }

    //The actual check box
    Rectangle {
        id: rectangle1
        x: 8
        y: 11
        width: 15
        height: 15
        color: uncheckedColor //We default to unchecked color
        border.width: 2
        border.color: "#000000"

        //The mouse area for the box to detect clicks
        MouseArea {
            id: mouse1
            anchors.fill: parent //We fill our parent

            onClicked: {
                check1.checked = !checked //Toggle the main checked state when clicked
            }
        }
    }

    //Our text box
    Text {
        id: text1
        x: 34
        y: 12
        color: textColor
        text: check1.text //Bind the text box's text to the text property
        font.pointSize: 12
        font.pixelSize: 12
    }

    states: [
        //State changes for checked
        State {
            name: "checked"

            //Change the rectangle color to checked
            PropertyChanges {
                target: rectangle1
                color: checkedColor
            }

            //Bold our font when checked
            PropertyChanges {
                target: text1
                font.bold: true
            }
        }
    ]
}
