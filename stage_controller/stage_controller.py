import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry


def yaw_from_quaternion(q):
    return math.atan2(
        2.0 * (q.w * q.z + q.x * q.y),
        1.0 - 2.0 * (q.y ** 2 + q.z ** 2)
    )


def normalize_angle(angle):
    return math.atan2(
        math.sin(angle),
        math.cos(angle)
    )


class StageController(Node):

    def __init__(self):
        super().__init__('stage_controller')

        # Comando de movimento
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Sensor LiDAR
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/base_scan',
            self.scan_callback,
            10
        )

        # Posição e orientação do robô
        self.odom_sub = self.create_subscription(
            Odometry,
            '/ground_truth',
            self.odom_callback,
            10
        )

        # Leituras do LiDAR
        self.front_distance = float('inf')
        self.left_distance = float('inf')
        self.right_distance = float('inf')

        # Estado do robô
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_yaw = 0.0

        # Objetivo
        self.goal_x = 5.0
        self.goal_y = 4.0

        # Controle do desvio
        self.avoiding = False
        self.turn_direction = 1.0
        self.avoid_ticks = 0

        # Controle da missão
        self.goal_reached = False

        # Executa o controlador a cada 0,1 s
        self.timer = self.create_timer(
            0.1,
            self.timer_callback
        )

    def odom_callback(self, msg):

        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y

        self.robot_yaw = yaw_from_quaternion(
            msg.pose.pose.orientation
        )

    def sector_distance(self, msg, min_angle_deg, max_angle_deg):

        min_angle = math.radians(min_angle_deg)
        max_angle = math.radians(max_angle_deg)

        distances = []

        for i, distance in enumerate(msg.ranges):

            angle = msg.angle_min + i * msg.angle_increment

            if min_angle <= angle <= max_angle:

                if (
                    math.isfinite(distance)
                    and distance >= msg.range_min
                    and distance <= msg.range_max
                ):
                    distances.append(distance)

        if not distances:
            return msg.range_max

        return min(distances)

    def scan_callback(self, msg):

        # Frente
        self.front_distance = self.sector_distance(
            msg,
            -25,
            25
        )

        # Esquerda
        self.left_distance = self.sector_distance(
            msg,
            25,
            90
        )

        # Direita
        self.right_distance = self.sector_distance(
            msg,
            -90,
            -25
        )

    def timer_callback(self):

        msg = Twist()

        # Distância e direção até o objetivo
        dx = self.goal_x - self.robot_x
        dy = self.goal_y - self.robot_y

        distance = math.hypot(dx, dy)

        desired_yaw = math.atan2(dy, dx)

        heading = normalize_angle(
            desired_yaw - self.robot_yaw
        )

        # -------------------------------------------------
        # REATIVA A MISSÃO SE O ROBÔ FOR RETIRADO DO DESTINO
        # -------------------------------------------------

        if self.goal_reached and distance > 0.90:

            self.goal_reached = False
            self.avoiding = False
            self.avoid_ticks = 0

            self.get_logger().info(
                'MISSAO REATIVADA!'
            )

        # -------------------------------------------------
        # ROBÔ JÁ ESTÁ NO OBJETIVO
        # -------------------------------------------------

        if self.goal_reached:

            msg.linear.x = 0.0
            msg.angular.z = 0.0

            self.publisher.publish(msg)
            return

        # -------------------------------------------------
        # CHEGOU AO OBJETIVO
        # -------------------------------------------------

        if distance < 0.70:

            self.goal_reached = True

            msg.linear.x = 0.0
            msg.angular.z = 0.0

            self.get_logger().info(
                'OBJETIVO ALCANCADO!'
            )

            self.publisher.publish(msg)
            return

        # -------------------------------------------------
        # ENTRAR NO MODO DE DESVIO
        # -------------------------------------------------

        if not self.avoiding:

            if (
                self.front_distance < 0.65
                or self.left_distance < 0.25
                or self.right_distance < 0.25
            ):

                self.avoiding = True
                self.avoid_ticks = 0

                # Escolhe o lado com mais espaço
                if self.left_distance > self.right_distance:
                    self.turn_direction = 1.0
                else:
                    self.turn_direction = -1.0

        # -------------------------------------------------
        # DESVIO DE OBSTÁCULO
        # -------------------------------------------------

        if self.avoiding:

            self.avoid_ticks += 1

            # Obstáculo muito próximo
            if self.front_distance < 0.55:

                msg.linear.x = 0.0
                msg.angular.z = 0.35 * self.turn_direction

            # Faz curva em arco
            else:

                msg.linear.x = 0.12
                msg.angular.z = 0.22 * self.turn_direction

            # Sai do modo de desvio quando a frente está livre
            if (
                self.avoid_ticks > 12
                and self.front_distance > 0.90
            ):
                self.avoiding = False

        # -------------------------------------------------
        # SEGUIR PARA O OBJETIVO
        # -------------------------------------------------

        else:

            # Grande diferença angular: gira primeiro
            if abs(heading) > 0.60:

                msg.linear.x = 0.0

                msg.angular.z = max(
                    -0.40,
                    min(
                        0.40,
                        0.7 * heading
                    )
                )

            # Pequena diferença: anda corrigindo a trajetória
            else:

                msg.linear.x = 0.20

                msg.angular.z = max(
                    -0.30,
                    min(
                        0.30,
                        0.6 * heading
                    )
                )

        self.get_logger().info(
            f'x={self.robot_x:.2f} '
            f'y={self.robot_y:.2f} '
            f'dist={distance:.2f} '
            f'heading={heading:.2f} | '
            f'F={self.front_distance:.2f} '
            f'L={self.left_distance:.2f} '
            f'R={self.right_distance:.2f} '
            f'avoid={self.avoiding}'
        )

        self.publisher.publish(msg)


def main(args=None):

    rclpy.init(args=args)

    node = StageController()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    stop = Twist()
    node.publisher.publish(stop)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
