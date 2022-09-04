from flask import Flask, Response, request
from google.cloud import pubsub_v1

import json
import sys
import os
import time

app = Flask(__name__)


def parseRequest(r):
 
    return r.json

@app.route('/alert',methods=['POST'])
def alert():

    global i2c
    global I2C_SLAVE_ADDRESS
    global alertStarted
    global alertTimer

    if request.method == 'POST':

        jsonData = parseRequest(request)

        print("Received event data: "+json.dumps(jsonData))

        #check if people is present for a while
        if jsonData != None and "detections" in jsonData:

            peopleDetected = 0

            for object in jsonData["detections"]:

                if object["label"] == "person":
                    peopleDetected += 1

            if peopleDetected > 0:
                if alertStarted:

                    PEOPLE_ALERT_INTERVAL = float(os.getenv('PEOPLE_ALERT_INTERVAL', "5.00"))

                    if time.time() - alertTimer >= PEOPLE_ALERT_INTERVAL:
                        print ("Alert confirmed. Sendindg notification...")

                        DEVICE_ID = os.getenv('DEVICE_ID', "G0")
                        PROJECT_ID = os.getenv('PROJECT_ID', "cogthings")
                        TOPIC_ID = os.getenv('TOPIC_ID', "fiap")

                        publisher = pubsub_v1.PublisherClient()
                        topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

                        data_str = '{"device":'+DEVICE_ID+', "type":"peopleAlert", "count":'+str(peopleDetected)+'}'

                        # Data must be a bytestring
                        data = data_str.encode("utf-8")
                        # When you publish a message, the client returns a future.
                        future = publisher.publish(topic_path, data)

                        print ("Notification sent!")

                        print(future.result())                        

                        #send close command over i2c
                        #command = "close"
                        #print("Sending "+command+" to I2C slave!")
                        #i2c.write_i2c_block_data(I2C_SLAVE_ADDRESS, 0, command.encode('utf-8'))			

                        alertStarted = False

                    else:
                        print ("Trying to confirm people alert...")
                else:
                    print ("Starting people alert timer..")
                    alertStarted = True
                    alertTimer = time.time()
            else:
                alertStarted = False
                print ("Finished or False Alert!")


        return Response("ok", status=201) 

    else:
        return Response("Invalid method")


def main():

    global i2c
    global I2C_BUS_NUMBER
    global I2C_SLAVE_ADDRESS
    global alertStarted
    global alertTimer
    
    alertStarted = False
    alertTimer = time.time()

    I2C_BUS_NUMBER = int(os.getenv('I2C_BUS_NUMBER', "0"))
    I2C_SLAVE_ADDRESS = int(os.getenv('I2C_SLAVE_ADDRESS', 0x08))

    try:
        print("\nPython %s\n" % sys.version )
        print("Command Module." )

        app.run(host='0.0.0.0', port=8081)

    except KeyboardInterrupt:
        print("Command Module stopped" )


if __name__ == '__main__':

    main()



