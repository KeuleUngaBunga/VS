package org.example;

public class Main {
    public static void main(String[] args) {
        try {
            robot_node robot = new robot_node();
            message msg_handler = new message();
            //testing----------------------------------------------------
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
            */
        } catch (Exception e) {
            e.printStackTrace();
        }
    
    }
}