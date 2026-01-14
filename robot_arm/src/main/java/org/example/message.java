package org.example;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

public class message {
    
    public JsonObject encode_register_Message(String name, String ip, int port) {
        //String jsonString ="{\"type\":\"register\",\"name\":\""+name+"\",\"ip\":\""+ip+"\",\"port\":"+port+"\",\"entity_type\":\"robot\"}";
        JsonObject register = new JsonObject();
        register.addProperty("type", "register");
        register.addProperty("name", name);
        register.addProperty("ip", ip);
        register.addProperty("port", port);
        register.addProperty("entity_type", "robot");
        return register;
    }

    public JsonObject encode_heartbeat_Message(String name) {
        JsonObject heartbeat = new JsonObject();
        heartbeat.addProperty("type", "heartbeat");
        heartbeat.addProperty("name", name);
        heartbeat.addProperty("entity_type", "robot");
        return heartbeat;
    }
    public Response_Message decode_Response_Message(String jsonString) {
        Gson gson = new Gson();
        Response_Message responseMessage = gson.fromJson(jsonString, Response_Message.class);
        return responseMessage;
    }
    public Action_Message decode_Action_Message(String jsonString) {
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
    public Action_Message(String action, int value) {//constructor for testing
        this.action = action;
        this.value = value;
    }
    public String getAction() {
        return action;
    }
    public int getValue() {
        return value;
    }  
}

