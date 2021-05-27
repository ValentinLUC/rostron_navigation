"""
    Suppression de noeud
    Certains imports sont useless (World)

"""
import math
from math import sin, cos, pi
import numpy as np

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist

from .aStar_to_ros import get_path_a_star
from .rviz_vizualisation import RvizVizualisation

from rostron_interfaces.msg import Robots
from rostron_interfaces.msg import Order

class MoveToStrategie(Node):
    #poseRobots= Robots()
    def __init__(self):
        super().__init__("move_to")
        self.subscription = self.create_subscription(
            Robots,
            '/yellow/allies',
            self.listener_robots,
            1
        )
        self.subscription
        self.poseRobots = Robots()
        self.publisher = self.create_publisher(Order,'/yellow/order', 1)

    def listener_robots(self, robots):
        self.poseRobots = robots
        return robots

    """
        Utilisation de numpy !
    """
    def normeVecteur (self, x, y):
        return math.sqrt( x**2 + y**2 )

    def normaliserVecteur(self, vecteur):
        return  vecteur / np.sqrt(np.sum(vecteur**2))

    def distance (self, x, y, xa, ya):
        return math.sqrt(((xa-x)**2)+((ya-y)**2))


    """
        Regarder tf de ros....
        Numpy propose sinon quelque chose dans cette veine !
    """
    def matriceRotation(self, x ,y, theta):
        # [cos(θ) -sin(θ)]   [x]
        # [sin(θ)  cos(θ)] * [y]
        return( cos(theta)*x - sin(theta)*y , sin(theta)*x+cos(theta)*y )
    
    # faire fonction qui prends une liste de points et arriveX arriveY dernier point
    def order_robot(self, id, path):
        for pose in path:
            rclpy.spin_once(self)
            robotIdPose = self.poseRobots.robots[id].pose # Robot 0

            ArriveX=pose[0]
            ArriveY=pose[1]

            # 1. récupérer: position et orientation courante du robot + position d'arrivé les deux étant dans le repère du terrain
            robotX = robotIdPose.position.x
            robotY = robotIdPose.position.y
            robotO = robotIdPose.orientation.z

            # 2. calculer le vecteur allant de la position du robot à la position d'arrivée
            vecteur = (ArriveX-robotX, ArriveY-robotY)
        
            # 3. créer une matrice de rotation anti-horaire correspondant à l'orientation du robot
            # 4. appliquer cette matrice sur le vecteur
            vecteur = self.matriceRotation(vecteur[0],vecteur[1],robotO)

            # 5. limiter la vitesse du robot en limitant la norme du vecteur, si norm(vec) > MAX_SPEED alors on normalise vec
            """
            MAX_SPEED= 5.5
            if self.normeVecteur(vecteur[0], vecteur[1]) > MAX_SPEED : 
                vecteur = self.normaliserVecteur(vecteur)
            """
            robotX = self.poseRobots.robots[id].pose.position.x
            robotY = self.poseRobots.robots[id].pose.position.y
            while self.distance(robotX, robotY, ArriveX, ArriveY)>0.1:
                rclpy.spin_once(self) # get current poseRobots
                robotX = self.poseRobots.robots[id].pose.position.x
                robotY = self.poseRobots.robots[id].pose.position.y
                if self.distance(robotX, robotY, ArriveX, ArriveY)>0.3 or pose==path[-1]:
                    vecteur = (ArriveX-robotX, ArriveY-robotY)
                    vecteur = self.matriceRotation(vecteur[0],vecteur[1],robotO)
                vel_msg = Twist()
                vel_msg.linear.x= vecteur[0]
                vel_msg.linear.y= vecteur[1]
                msg = Order()
                msg.id = id
                msg.velocity = vel_msg
                self.publisher.publish(msg)
        self.stop_robot(id)


    def stop_robot(self, id):
        msg = Order()
        msg.id = id
        msg.velocity = Twist()
        self.publisher.publish(msg)
        

    def move_to(self, id, finalPose):
        rclpy.spin_once(self)

        path= get_path_a_star(id,finalPose)
        self.order_robot(id, path)

        rviz = RvizVizualisation()
        rviz.get_rviz_vizualisation(path)

        self.destroy_node()

if __name__ == '__main__':
    pass
    # main()
