#!/usr/bin/env python3
"""A minimal ROS 2 subscriber that prints every String it receives on /chatter."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimpleSubscriber(Node):
    """Log every incoming String on /chatter."""

    def __init__(self) -> None:
        super().__init__("simple_subscriber")

        # 1 Create the subscription
        self.subscriber = self.create_subscription(
            String,                  # Message type
            "chatter",              # Topic name
            self.message_callback,   # Callback executed on arrival
            10                       # Queue size
        )

        # 2 Prevent unused‑variable warning (only needed in C++)
        self.subscriber  # noqa: F841

    # 3 Callback function
    def message_callback(self, msg: String) -> None:
        self.get_logger().info(f"I heard: {msg.data}")


def main() -> None:
    rclpy.init()
    node = SimpleSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()