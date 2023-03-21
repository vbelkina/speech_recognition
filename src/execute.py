#!/usr/bin/env python3


import rospy 
import json 
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from gtts import gTTS
import os
import rostopic
import pysine

class Execute():

    def __init__(self):
        self.node_name = "[EXECUTE]"
        self.cmd_vel = rospy.Publisher("/cmd_vel", Twist, queue_size=1)
        self.command_sub = rospy.Subscriber("/whisper/command", String, self.command_cb)
        self.commands = []
        self.prev_command = ""

        with open('/home/nika/catkin_ws/src/whisper_4/commands.json') as file:
            self.parsed_json = json.load(file)
    
    def process_command(self, text):
        return text.lower().strip().split()

    def execute_command(self, text):
        rospy.loginfo(f"{self.node_name} received command <{text}>")
        twist = Twist()
        command = self.process_command(text)

        if command[0] == "stop":
            self.cmd_vel.publish(twist)
            self.play_tone(freq=440, duration=0.2)
            self.play_tone(freq=300, duration=0.2)
            # self.speak("Stopping now.")
        elif command[0] == "exit" or command[0] == "shutdown":
            self.cmd_vel.publish(twist)
            self.play_tone(freq=300, duration=0.2)
            self.play_tone(freq=440, duration=0.2)
            self.play_tone(freq=200, duration=0.3) 
            # self.speak("Exiting program now.")
            return -1
        elif command[0] in self.parsed_json:
            if command[1] in self.parsed_json[command[0]]:
                twist.linear.x = self.parsed_json[command[0]][command[1]]["linear.x"]
                twist.linear.y = self.parsed_json[command[0]][command[1]]["linear.y"]
                twist.linear.z = self.parsed_json[command[0]][command[1]]["linear.z"]
                twist.angular.x = self.parsed_json[command[0]][command[1]]["angular.x"]
                twist.angular.y = self.parsed_json[command[0]][command[1]]["angular.y"]
                twist.angular.z = self.parsed_json[command[0]][command[1]]["angular.z"]

                self.cmd_vel.publish(twist)
                
                self.play_tone(440)
                # self.speak(f"Executing command {command}")
            else: 
                # self.speak(f"I don't know the command {command}.")
                self.play_tone(220)
        else: 
            # self.speak(f"I don't know the command {command}.")
            self.play_tone(220)
        
        self.prev_command = text

    def command_cb(self, msg):
        self.commands.append(msg.data)
        current_command = self.commands.pop()
        if self.prev_command != current_command:
            self.execute_command(current_command)

    def play_tone(self, freq, duration=1.0):
        pysine.sine(frequency=freq, duration=duration)  
        
    def speak(self, text):
        rospy.loginfo(f"{self.node_name} Going to say: {text}")
        speech = gTTS(text= text, lang="en", slow=False)

        # Saving the converted audio in a mp3 file named
        speech.save("speak.mp3")
        
        # Playing the converted file
        os.system("mpg123 -q speak.mp3")

rospy.init_node("execute")
executer = Execute()
rospy.spin()