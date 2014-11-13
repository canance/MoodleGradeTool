import QtQuick 1.1

Rectangle {
    id: rectangle1
    width: 300
    height: 100
    radius: 11
    border.width: 0
    border.color: "#C5B9AB"
    //Background gradient
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

    signal wasSelected(int id)  //Signal to fire if we were selected

    property string static_state: ""  //Holds current base state to return to after hover or selected
    property string disp_name: "Student Name"  //Name to display
    property string disp_status: "Waiting to build" //Status to display
    property int disp_score: 0 //Student's score
    property int disp_possible: 0 //Maximum Possible score
    property int std_id: 0 // Our id
    property bool selected: false

    state: static_state //Initial binding

    Binding {
        target: rectangle1
        property: "state"
        value: static_state
        when: !(selected || rect1_mouse.containsMouse) //Conditionally bind static state to state
    }

    //Handles hover and click events
    MouseArea{
        id: rect1_mouse
        anchors.fill: parent
        hoverEnabled: true
        //Change state based on hover
        onHoveredChanged: {
            //See if we are not in hovered state and should be
            if ((rectangle1.state == rectangle1.static_state) || selected) {
                rectangle1.state = "mouse_over"
            }
            //If we are selected, return to that
            else if (selected) {
                rectangle1.state = "selected"
            }
            //Else go back to our static state
            else {
                rectangle1.state = rectangle1.static_state
            }
        }

        onClicked: {
            wasSelected(std_id) //Fire selected signal
        }
    }

    //Handle selection change events
    function handleSelected(sender){
        //If the sender id matches our id then we've been selected
        selected = rectangle1.std_id === sender
    }

    //Text box for the students name
    Text {
        id: txt_name
        x: 8
        y: 8
        color: "#d1d1d1"
        text: disp_name
        style: Text.Sunken
        font.pointSize: 19

    }


    //Status label
    Text {
        id: text1
        x: 8
        y: 43
        text: qsTr("Status: ")
        font.pointSize: 11

    }

    //Status name textbox
    Text {
        id: txt_status
        x: 72
        y: 43
        text: disp_status
        font.pointSize: 11

    }

    //Score label
    Text {
        id: text3
        x: 8
        y: 67
        text: qsTr("Score: ")
        font.pointSize: 10

    }

    //Score value textbox
    Text {
        id: txt_score
        x: 64
        y: 68
        text: disp_score + '/' + disp_possible
        font.bold: true
        font.pointSize: 13

    }

    //State list
    states: [
        //Hovered state
        State {
            name: "mouse_over"
            //Add a border
            PropertyChanges {
                target: rectangle1
                border.width: 2
            }
            //Make the top of the gradient lighter
            PropertyChanges {
                target: gradtop
                color: "#AFBDD4"

            }

        },
        //Error state
        State {
            name: "error"
            //Change gradient top to red
            PropertyChanges {
                target: gradtop
                color: "#C13434"
            }
        },
        //Ready state
        State {
            name: "ready"
            //Change gradient top to green
            PropertyChanges {
                target: gradtop
                color: "#799279"

            }
        },

        //Selected state
        State {
            name: "selected"
            //Change gradient colors
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
    //On any state change, animate the color change
    transitions: [
        Transition {
            to: "*"
            ColorAnimation { target: gradtop; duration: 100 }
            ColorAnimation { target: gradbottom; duration: 100 }

        }
    ]
}
