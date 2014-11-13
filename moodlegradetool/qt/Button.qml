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

    signal clicked() //Fires when the button is clicked

    property string prompt: "Click Here" //The button's text
    property bool enabled: true //Controls whether button is enabled or not

    //Changes the state when enabled is changed
    onEnabledChanged: {
        if (enabled)
            state = ""
        else
            state = "disabled"
    }

    //The text box for the main text
    Text {
        id: txt_text
        text: prompt //Connects this text box to the prompt
        horizontalAlignment: Text.AlignHCenter //Centers the text
        verticalAlignment: Text.AlignVCenter
        font.bold: true
        smooth: true
        anchors.fill: parent  //The text box has the same area as the parent
        font.pointSize: 12
    }

    //Needed to handle mouse clicks and hovers
    MouseArea {
        id: mousearea1
        hoverEnabled: true //Check for hover
        anchors.fill: parent //The mouse area covers the entire button

        //When we're clicked we need to fire the clicked signal
        onClicked: {
            btn1.clicked()
        }

        //Set state to pressed when the mouse button is held down
        onPressed: {
            btn1.state = "pressed"
        }

        //Set state back to the original state when the mouse button is released
        onReleased: {
            if (mousearea1.containsMouse){
                btn1.state = "hover"
            }
            else
                btn1.state = ""
        }

        //Switch between states when the mouse enters or leaves the area
        onHoveredChanged: {
            if (btn1.state == "")
                btn1.state = "hover"
            else
                btn1.state = ""
        }
    }

    //Set the properties for the states
    states: [
        //For hovering
        State {
            name: "hover"
            //We just change the top of the background to white
            PropertyChanges {
                target: gradtop
                color: "#ffffff"

            }
        },
        //When held down
        State {
            name: "pressed"
            //These changes invert the gradient
            PropertyChanges {
                target: gradtop
                position: 1

            }
            PropertyChanges {
                target: gradbottom
                position: 0

            }
        },

        //When disabled
        State {
            name: "disabled"

            //Disable mouse events
            PropertyChanges {
                target: mousearea1
                hoverEnabled: false
                enabled: false
            }
            //Change main color to gray
            PropertyChanges {
                target: gradbottom
                color: "#414141"
            }
            //And change the text style
            PropertyChanges {
                target: txt_text
                color: "#555555"
                font.bold: false
                style: "Sunken"
            }
        }
    ]
}
