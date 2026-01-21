package org.example;
//import java.net.*;
import java.io.*;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.Executors;

import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class Main {
    private static Connect_Handler connectHandler;

    public static void main(String[] args) {
        try {
            //hardcoded values for testing
            //connectHandler = new Connect_Handler( "localhost", 7000, "localhost", 6000);
            
            //interactive
            
            System.out.println("Geben Sie IPs und Ports für den Roboter und den Server  folgendermaßen ein: <Roboter-IP> <Roboter-Port> <Server-IP> <Server-Port>");
            BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
            String[] params = reader.readLine().split("\\s+");
            connectHandler = new Connect_Handler( params[0], Integer.parseInt(params[1]), params[2], Integer.parseInt(params[3]));
            
            
            //start connection handler
            connectHandler.start();

        } catch (Exception e) {
            e.printStackTrace();
        }
    
    }

    
}




class Connect_Handler {

    private String name;
    private final String ip;
    private final int port;

    private final String serverHost;
    private final int serverPort;

    private final Gson gson = new Gson();
    private message msg_handler = new message();
    private robot_node robot = new robot_node(null,0);

    private final ScheduledExecutorService scheduler =
            Executors.newScheduledThreadPool(3);

    public Connect_Handler(String ip, int port,
                     String serverHost, int serverPort) {
        this.ip = ip;
        this.port = port;
        this.serverHost = serverHost;
        this.serverPort = serverPort;
    }//name wird dynamisch bei der Registrierung gesetzt

       //START

    public void start() throws IOException {
        connectAndRegister();
        startHeartbeat();
        startIncomingServer();
        listenForCommand();
    }

    private void closeConnections(Socket serverSocket, BufferedWriter serverOut, BufferedReader serverIn) throws IOException {
        serverIn.close();
        serverOut.close();
        serverSocket.close();
    }
  
    //REGISTRIERUNG
    

    private void connectAndRegister() throws IOException {
        String responseStatus;
        try{//bis ein valider Name gewählt wurde versuchen zu registrieren
            do{//für jeden versuchten Namen eine neue Verbindung
                Socket serverSocket = new Socket(serverHost, serverPort);
                BufferedWriter serverOut = new BufferedWriter(
                        new OutputStreamWriter(serverSocket.getOutputStream()));
                BufferedReader serverIn = new BufferedReader(
                        new InputStreamReader(serverSocket.getInputStream()));
                System.out.println("Geben Sie den Namen des Roboters ein:");
                BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
                name = reader.readLine();
                JsonObject register = msg_handler.encodeRegisterMessage(name, ip, port);

                sendToServer(serverOut, register);

                // Status-Antwort lesen 
                responseStatus = recieveResponse(serverIn);
                closeConnections(serverSocket, serverOut, serverIn);
            } while (!responseStatus.equals("ok"));
        } catch (IOException e) {
            System.err.println("Registrierung fehlgeschlagen");
        }
    }

    //HEARTBEAT

    private void startHeartbeat() {
        scheduler.scheduleAtFixedRate(() -> {
            try {//neue Verbindungen jedes mal, da server immer die connections schließt
                Socket serverSocket = new Socket(serverHost, serverPort);
                BufferedWriter serverOut = new BufferedWriter(
                        new OutputStreamWriter(serverSocket.getOutputStream()));
                BufferedReader serverIn = new BufferedReader(
                        new InputStreamReader(serverSocket.getInputStream()));
                JsonObject heartbeat = msg_handler.encodeHeartbeatMessage(name);
                sendToServer(serverOut, heartbeat);
                //System.out.println("HEARTBEAT SENT ");
                recieveResponse(serverIn);
                closeConnections(serverSocket, serverOut, serverIn);
            } catch (IOException e) {
                System.err.println("Heartbeat fehlgeschlagen");
            }
        }, 5, 5, TimeUnit.SECONDS);
    }

    private synchronized void sendToServer(BufferedWriter serverOut, JsonObject json) throws IOException {
        serverOut.write(gson.toJson(json));
        serverOut.write("\n");
        serverOut.flush();
    }

    //INCOMING PYTHON CLIENTS

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

                Action_Message actionMessage = msg_handler.decodeActionMessage(gson.toJson(msg));
                //System.out.println("Empfangene Aktion: " + actionMessage.getAction() + " mit Wert: " + actionMessage.getValue());//nur debug
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

    private void listenForCommand() {//für Unregister -> zum beenden
        scheduler.execute(() -> {
            BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
            String command;
            try {
                while ((command = reader.readLine()) != null) {
                    System.out.println("Empfangener Befehl: " + command);
                    if(command.equals("exit")){
                        System.out.println("Sende Unregister Message und beende Programm...");
                        // Unregister Message senden
                        try {
                            Socket serverSocket = new Socket(serverHost, serverPort);
                            BufferedWriter serverOut = new BufferedWriter(
                                    new OutputStreamWriter(serverSocket.getOutputStream()));
                            BufferedReader serverIn = new BufferedReader(
                                    new InputStreamReader(serverSocket.getInputStream()));
                            JsonObject unregister = msg_handler.encodeUnregisterMessage(name);
                            sendToServer(serverOut, unregister);
                            recieveResponse(serverIn);
                            closeConnections(serverSocket, serverOut, serverIn);
                            scheduler.shutdown();
                            System.exit(0);
                        } catch (IOException e) {
                            System.err.println("Unregistrierung fehlgeschlagen");
                        }
                        
                    }
                    // Hier können Sie den Befehl verarbeiten});
                }
            } catch (IOException e) {
                System.out.println("Fehler beim Lesen des Befehls: " + e.getMessage());
            }
        });
    } 

    private String recieveResponse(BufferedReader serverIn){
        Response_Message responseMessage;
        // Status-Antwort lesen 
        try {
        String responseLine = serverIn.readLine();
        responseMessage = msg_handler.decodeResponseMessage(responseLine);
        //System.out.println("STATUS: " + responseMessage.getStatus());
        System.out.println("MESSAGE: " + responseMessage.getMessage());
        return responseMessage.getStatus();
        } catch (IOException e) {
            System.err.println("Fehler beim Lesen der Serverantwort");
            return null;
        }
    }
}
