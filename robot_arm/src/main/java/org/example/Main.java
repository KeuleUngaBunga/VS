package org.example;
//import java.net.*;
import java.io.*;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

import java.net.ServerSocket;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.concurrent.Executors;

import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class Main {
    private static Connect_Handler connectHandler;

    public static void main(String[] args) {
        try {
            
            connectHandler = new Connect_Handler("robot1", "10.8.0.8", 7000, "10.8.0.7", 6000);
            connectHandler.start();


            //testing----------------------------------------------------
            /** 
            robot_node robot = new robot_node();
            message msg_handler = new message();
            Action_Message action = msg_handler.decode_Action_Message("{\"action\":\"leftRight\",\"value\":100}");

            robot.moveArm(action.getAction(), action.getValue());
             
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




class Connect_Handler {

    private final String name;
    private final String ip;
    private final int port;

    private final String serverHost;
    private final int serverPort;

    private final Gson gson = new Gson();
    private Socket serverSocket;
    private BufferedWriter serverOut;
    private BufferedReader serverIn;
    private message msg_handler = new message();
    private robot_node robot = new robot_node();

    private final ScheduledExecutorService scheduler =
            Executors.newScheduledThreadPool(2);

    public Connect_Handler(String name, String ip, int port,
                     String serverHost, int serverPort) {
        this.name = name;
        this.ip = ip;
        this.port = port;
        this.serverHost = serverHost;
        this.serverPort = serverPort;
    }

    /* =====================
       START
       ===================== */

    public void start() throws IOException {
        connectAndRegister();
        startHeartbeat();
        startIncomingServer();
    }

    /* =====================
       REGISTRIERUNG
       ===================== */

    private void connectAndRegister() throws IOException {
        serverSocket = new Socket(serverHost, serverPort);
        serverOut = new BufferedWriter(
                new OutputStreamWriter(serverSocket.getOutputStream()));
        serverIn = new BufferedReader(
                new InputStreamReader(serverSocket.getInputStream()));
        try{
            JsonObject register = msg_handler.encode_register_Message(name, ip, port);

            sendToServer(register);

            // Status-Antwort lesen ------------- responses weird
            String responseLine = serverIn.readLine();
            Response_Message responseMessage = msg_handler.decode_Response_Message(responseLine);

            System.out.println("REGISTER STATUS: " + responseMessage.getStatus());//error handling?
            System.out.println("MESSAGE: " + responseMessage.getMessage());
        } catch (IOException e) {
            System.err.println("Registrierung fehlgeschlagen");
        }
    }

    /* =====================
       HEARTBEAT
       ===================== */

    private void startHeartbeat() throws IOException {
        //++++++++++++++++++++++++++++++++++++++++++++++
        scheduler.scheduleAtFixedRate(() -> {
            try {
                serverSocket = new Socket(serverHost, serverPort);
            } catch (UnknownHostException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
                try {
                    serverOut = new BufferedWriter(
                            new OutputStreamWriter(serverSocket.getOutputStream()));
                } catch (IOException e1) {
                    e1.printStackTrace();
                }
                try {
                    serverIn = new BufferedReader(
                            new InputStreamReader(serverSocket.getInputStream()));
                } catch (IOException e) {
                    e.printStackTrace();
                }
                        //krise der try catch blöcke++++++++++++++++++++++++++
            try {
                //System.out.println("HEARTBEAT NOT SENT ");

                JsonObject heartbeat = msg_handler.encode_heartbeat_Message(name);
                sendToServer(heartbeat);
                //System.out.println("HEARTBEAT SENT ");

                // Status-Antwort lesen ------------ responses weird
                String responseLine = serverIn.readLine();
                Response_Message responseMessage = msg_handler.decode_Response_Message(responseLine);

                System.out.println("HEARTBEAT STATUS: " + responseMessage.getStatus());
                System.out.println("MESSAGE: " + responseMessage.getMessage());//timestamp
            } catch (IOException e) {
                System.err.println("Heartbeat fehlgeschlagen");
            }
        }, 5, 5, TimeUnit.SECONDS);
    }

    private synchronized void sendToServer(JsonObject json) throws IOException {
        serverOut.write(gson.toJson(json));
        serverOut.write("\n");
        serverOut.flush();
    }

    /* =====================
       INCOMING PYTHON CLIENTS
       ===================== */

    private void startIncomingServer() {
        scheduler.execute(() -> {
            try (ServerSocket serverSocket = new ServerSocket(port)) {
                System.out.println("Empfange Python Clients auf Port " + port);

                while (true) {
                    Socket client = serverSocket.accept();
                    scheduler.execute(() -> handlePythonClient(client));
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        });
    }

    private void handlePythonClient(Socket socket) {
        try (BufferedReader in = new BufferedReader(
                     new InputStreamReader(socket.getInputStream()))) {

            String line;
            while ((line = in.readLine()) != null) {
                JsonObject msg = gson.fromJson(line, JsonObject.class);

                Action_Message actionMessage = msg_handler.decode_Action_Message(gson.toJson(msg));
                System.out.println("Empfangene Aktion: " + actionMessage.getAction() +
                                   " mit Wert: " + actionMessage.getValue());
                try{
                    robot.moveArm(actionMessage.getAction(), actionMessage.getValue());
                } catch (Exception e) {
                    System.out.println("Fehler beim Bewegen des Roboters: " + e.getMessage());
                }

            }

        } catch (IOException e) {
            System.out.println("Python Client getrennt");
        }
    }
}

