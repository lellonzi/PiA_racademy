#!/usr/bin/env python3
"""A minimal ROS 2 publisher that writes a string to /chatter once per second."""

# 1 Import the rclpy client library (core ROS 2 Python API)
import rclpy

# 2 Import the base Node class we will inherit from
from rclpy.node import Node

# 3 Import the message type we intend to send
from std_msgs.msg import String


class SimplePublisher(Node):
    """Publish a string message on /chatter at 1 Hz."""

    def __init__(self) -> None:
        # 4 Call parent constructor with the node name
        super().__init__("simple_publisher")

        # 5 Create a publisher handle
        #   • String: message type
        #   • "chatter": topic name
        #   • 10: size of the outgoing message queue
        self.publisher = self.create_publisher(String, "chatter", 10)

        # 6 State variables
        self.counter = 0            # message number
        self.timer_period = 1.0     # seconds; 1 Hz

        # 7 Log a banner so the user knows the node is alive
        self.get_logger().info(f"Publishing at {1/self.timer_period:.0f} Hz")

        # 8 Register a periodic callback
        #   When `self.timer_period` elapses, `timer_callback` is invoked
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

    # 9 The callback executed every self.timer_period seconds
    def timer_callback(self) -> None:
        msg = String()
        msg.data = f"Hello World {self.counter}"

        # 10 Transmit the message
        self.publisher.publish(msg)

        # 11 Bookkeeping for the next pass
        self.counter += 1


def main() -> None:
    """ROS 2 boilerplate: initialize, spin, and shut down."""

    # 12 Initialize the rclpy system
    rclpy.init()

    # 13 Instantiate our node
    node = SimplePublisher()

    # 14 Enter the event loop—this blocks until Ctrl‑C
    rclpy.spin(node)

    # 15 Clean up explicitly (optional but good style)
    node.destroy_node()
    rclpy.shutdown()


# 16 Allow the file to be executed directly.
if __name__ == "__main__":
    main()