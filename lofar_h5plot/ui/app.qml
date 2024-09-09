import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ApplicationWindow {
    id: mainwindow
    visible: true
    title: "LOFAR H5plot"
    width: 410
    GridLayout {
        id: grid
        columns: 4

        MenuBar {
            Layout.row: 0
            Menu {
                title: "File"
                MenuItem {
                    text: "Open"
                }
                MenuItem {
                    text: "Exit"
                }
            }
        }
        Label {
            Layout.column: 0
            Layout.columnSpan: 1
            Layout.row: 1
            text: "Solset: "
        }
        ComboBox {
            Layout.column: 1
            Layout.columnSpan: 3
            Layout.row: 1
        }
        
        // Plot selection line
        Label {
            Layout.column: 0
            Layout.row: 2
            text: "Plot "
        }
        ComboBox {
            Layout.column: 1
            Layout.row: 2
        }
        Label {
            Layout.column: 2
            Layout.row: 2
            text: "vs "
        }
        ComboBox {
            Layout.column: 3
            Layout.row: 2
            model: ["time", "frequency", "waterfall"]
        }
        
        // Ant dir selection line
        Label {
            Layout.column: 0
            Layout.row: 3
            text: "Ref. Ant. "
        }
        ComboBox {
            Layout.column: 1
            Layout.row: 3
        }
        Label {
            Layout.column: 2
            Layout.row: 3
            text: "Dir. "
        }
        ComboBox {
            Layout.column: 3
            Layout.row: 3
            model: ["dir0"]
        }
        GridLayout {
            Layout.columnSpan: 4
            Layout.preferredWidth: mainwindow.width
            // Mode checkboxes
            CheckBox {
                Layout.column: 0
                Layout.row: 4
                text: "Plot weights"
            }
            CheckBox {
                Layout.column: 2
                Layout.row: 4
                text: "Time diff."
            }
            CheckBox {
                Layout.column: 0
                Layout.row: 5
                text: "Pol. diff. (XX - YY)"
            }
            CheckBox {
                Layout.column: 2
                Layout.row: 5
                text: "Freq. diff."
            }
        }
        Button {
            Layout.column: 0
            Layout.columnSpan: 4
            Layout.row: 6
            Layout.preferredWidth: mainwindow.width
            text: "Plot"
        }
        Button {
            Layout.columnSpan: 4
            Layout.row: 7
            Layout.preferredWidth: mainwindow.width
            text: "Plot all stations"
        }
        ListView {
            anchors.fill: root
            Layout.columnSpan: 4
            Layout.row: 8
            Layout.fillHeight: true
            Layout.preferredWidth: mainwindow.width
            width: 200
            height: 200
            model: station_list
            delegate: Row {
                    Label { text: name}
                }
            ScrollBar.vertical: ScrollBar {
                active: true
            }
            }
        }

            ListModel {
                id: station_list
                ListElement {
                    name: "RS106HBA"
                }
                ListElement {
                    name: "ST001"
                }
    }
}
