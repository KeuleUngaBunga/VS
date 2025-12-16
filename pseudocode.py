#pseudocode Registry Client



class RegistryClient:
    
    def __init__(self, IP_address, port):
        self.IP_address = IP_address
        self.port = port
        self.robots = {}#Tupel{ID,Name,IP,Port}
        self.cleints={}#Tupel{ID,Name,IP,Port}
        self.id=0 #unique ID for everyone

    def list(self):
        msg=messages.encode_message(messages.ListResponse())
        return msg

    def register(self, name, ip, port):#register + vergeben von IDs//vllt prüfen von doppelten Namen
        #------------------------------robot block------------------------------
        #if (robot):
        #if name in self.robots:
            #return messages.ErrorResponse("Name already exists")
            #else:    
        self.robots.add((self.id,name, ip, port))
        out_msg = messages.RegisterResponse(True, self.id)
        self.id+=1

        #------------------------------client block------------------------------
        #if (client):
        # if name in self.clients:
            #return messages.ErrorResponse("Name already exists")
            # else:    
        self.clients.add((self.id,name, ip, port))
        out_msg = messages.RegisterResponse(True, self.id)
        self.id+=1

        return out_msg
    
    def unregister(self, name):#Eintrag zu dem Namen löschen, deshalb keine doppelten Namen erlaubt
        #if (robot):
        self.robots.remove((name))
        #if (client): 
        self.clients.remove((name))
        return True
    
    def run(self):
        #connection logic
        #socket creation.....
        socket= None
        socket.bind((self.IP_address,self.port))
        #listening for messages
        while True:
            #Nebenläufigkeit beachten evtl Threading für mehrere Anfragen im Socket
            #recieve message
            #new Thraed:
            in_msg = messages.decode_message(None)
            if(in_msg.type)== "ListRequest":
                out_msg = self.list()
                
            elif(in_msg.type)=="RegisterRequest":
                out_msg = self.register(in_msg.name, in_msg.ip, in_msg.port)
                
            #elif... other message types
            #send response
            socket.sendto(messages.encode_message(out_msg), in_msg.address)
        pass

    def cleanup(self):
        #close socket
        pass
    

#Example messages
class messages:
    #differnet types of messages mit Aufbau
    class ListRequest:
        pass

    class ListResponse:
        def __init__(self, type):#Liste mit allen Robotern oder Clients in eine msg zum verschicken verpacken
            msg=None
            #if robot:
            for robot in self.robots:
                #string =  mit allen Robotern
                #msg=message.decode_message(string)
                return msg
            #if client:
            for client in self.clients:
                #string =  mit allen Clients 
                #msg=message.decode_message(string)
                return msg
        

    class RegisterRequest:
        def __init__(self, name, ip, port):
            self.name = name
            self.ip = ip
            self.port = port

    class RegisterResponse:#response mit unique ID
        def __init__(self,id):
            self.ID = id

    class UnregisterRequest:
        def __init__(self, name):#vllt ID sinnvoller? aber laut aufgabe name, wenn dieser unique, dann ok
            self.name = name

    class UnregisterResponse:#response hier sinnvoll?
        def __init__(self, success):
            self.success = success

    class ErrorResponse:
        def __init__(self, error_msg):
            self.error_msg = error_msg

    def decode_message(data):
        # Simulate decoding a message
        pass
    def encode_message(message):
        # Simulate encoding a message
        pass


#example main for RegistryClient
def main(self):
    #input IP and Port
    registry_client = RegistryClient()
    registry_client.run()
    #cleanup and close socket when done