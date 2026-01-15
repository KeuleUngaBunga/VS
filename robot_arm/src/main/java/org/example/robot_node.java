package org.example;

import org.cads.vs.roboticArm.hal.ICaDSRoboticArm;
import org.cads.vs.roboticArm.hal.simulation.CaDSRoboticArmSimulation;


//für terminal:
//compile:
//javac -cp "CaDSPracticalExamVS/VSEclipseExampleProject/resources/libs/*" robot_node.java
//run: mit module-path für javafx
//java -cp "CaDSPracticalExamVS/VSEclipseExampleProject/resources/libs/*" --module-path "C:/Users\pfeif/openjfx-21.0.2_windows-x64_bin-sdk/javafx-sdk-21.0.2/lib" --add-modules=javafx.controls,javafx.fxml robot_node.java
//java --module-path "C:/Users\pfeif/openjfx-21.0.2_windows-x64_bin-sdk/javafx-sdk-21.0.2/lib" --add-modules=javafx.controls,javafx.fxml robot_node.java

public class robot_node {
    private ICaDSRoboticArm roboticArm;

    public robot_node(String roboticArmHostAddress, int roboticArmHostPort) {
        //real 
        //roboticArm = new CaDSRoboticArmReal(roboticArmHostAddress, roboticArmHostPort);
        //simulation
        roboticArm = new CaDSRoboticArmSimulation();
    }

    public void moveArm(String move, int val) throws InterruptedException {
        System.out.println("Moving arm: " + move + " to " + val + "%");
        switch (move) {
            case "leftRight":
                roboticArm.setLeftRightPercentageTo(val);
                break;
            case "upDown":
                roboticArm.setUpDownPercentageTo(val);
                break;
            case "backForth":
                roboticArm.setBackForthPercentageTo(val);
                break;
            case "openClose":
                roboticArm.setOpenClosePercentageTo(val);
                break;
            default:
                break;
        }
        Thread.sleep(1000); // wait for movement to complete
    }

}
