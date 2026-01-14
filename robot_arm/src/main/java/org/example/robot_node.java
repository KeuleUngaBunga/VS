package org.example;

import org.cads.vs.roboticArm.hal.ICaDSRoboticArm;
import org.cads.vs.roboticArm.hal.simulation.CaDSRoboticArmSimulation;
import org.example.message;
import java.net.*;

import java.io.*;

//für terminal:
//compile:
//javac -cp "CaDSPracticalExamVS/VSEclipseExampleProject/resources/libs/*" robot_node.java
//run: mit module-path für javafx
//java -cp "CaDSPracticalExamVS/VSEclipseExampleProject/resources/libs/*" --module-path "C:/Users\pfeif/openjfx-21.0.2_windows-x64_bin-sdk/javafx-sdk-21.0.2/lib" --add-modules=javafx.controls,javafx.fxml robot_node.java
//java --module-path "C:/Users\pfeif/openjfx-21.0.2_windows-x64_bin-sdk/javafx-sdk-21.0.2/lib" --add-modules=javafx.controls,javafx.fxml robot_node.java

public class robot_node {
    private ICaDSRoboticArm roboticArm;

    public robot_node() {
        //real oder sim
        //roboticArm = new CaDSRoboticArmReal(roboticArmHostAddress, roboticArmHostPort);
        roboticArm = new CaDSRoboticArmSimulation();
    }

    public void moveArm(String move, int val) throws InterruptedException {
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


/** 
    public static void main(String[] args) {
        try {
            robot_node robot = new robot_node();
            message msg_handler = new message();
            Action_Message action = msg_handler.decode_Action_Message("{\"action\":\"leftRight\",\"value\":100}");

            robot.moveArm(action.getAction(), action.getValue());
            /** 
                System.out.println("Moving arm to 100% positions");
                robot.moveArm("leftRight", 100);
                robot.moveArm("upDown", 100);
                robot.moveArm("backForth", 100);
                robot.moveArm("openClose", 100);
                Thread.sleep(6000);
                System.out.println("Moving arm to 0% positions");
                robot.moveArm("leftRight", 0);
                robot.moveArm("upDown", 0);
                robot.moveArm("backForth", 0);
                robot.moveArm("openClose", 0);
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }*/
}
