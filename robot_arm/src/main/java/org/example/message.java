package org.example;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

public class message {
    
    public JsonObject encodeRegisterMessage(String name, String ip, int port) {
        JsonObject register = new JsonObject();
        register.addProperty("type", "register");
        register.addProperty("name", name);
        register.addProperty("ip", ip);
        register.addProperty("port", port);
        register.addProperty("entity_type", "robot");
        return register;
    }

    public JsonObject encodeUnregisterMessage(String name) {
        JsonObject register = new JsonObject();
        register.addProperty("type", "unregister");
        register.addProperty("name", name);
        return register;
    }

    public JsonObject encodeHeartbeatMessage(String name) {
        JsonObject heartbeat = new JsonObject();
        heartbeat.addProperty("type", "heartbeat");
        heartbeat.addProperty("name", name);
        heartbeat.addProperty("entity_type", "robot");
        return heartbeat;
    }
    public Response_Message decodeResponseMessage(String jsonString) {
        Gson gson = new Gson();
        Response_Message responseMessage = gson.fromJson(jsonString, Response_Message.class);
        return responseMessage;
    }
    public Action_Message decodeActionMessage(String jsonString) {
        Gson gson = new Gson();
        Action_Message actionMessage = gson.fromJson(jsonString, Action_Message.class);
        return actionMessage;
    }

}

class Response_Message {
    private String status;
    private String message;
    public String getStatus() {
        return status;
    }
    public String getMessage() {
        return message;
    }  
}

class Action_Message {
    private String action;
    private int value;
    
    public String getAction() {
        return action;
    }
    public int getValue() {
        return value;
    }  
}

