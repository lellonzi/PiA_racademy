#!/usr/bin/env python3
"""Demonstrate declaring, reading, and dynamically updating parameters."""

#  1  Core ROS 2 Python API
import rclpy
from rclpy.node import Node

#  2  Interface types for the callback result and type checking
from rcl_interfaces.msg import SetParametersResult
from rclpy.parameter   import Parameter


class SimpleParameter(Node):
    """Expose two parameters and print a message whenever they change."""

    def __init__(self) -> None:
        #  3  Initialise the Node with a unique name
        super().__init__("simple_parameter")

        #  4  Declare parameters with default values
        self.declare_parameter("simple_int_param",    28)
        self.declare_parameter("simple_string_param", "voss")

        #  5  Register a callback that fires *before* any parameter actually changes
        self.add_on_set_parameters_callback(self.param_change_callback)

    #  6  Validation callback. If we return success=False the change is rejected.
    def param_change_callback(self, params: list[Parameter]) -> SetParametersResult:
        result = SetParametersResult(successful=True)

        for param in params:
            # 7  Integer guard
            if param.name == "simple_int_param":
                if param.type_ == Parameter.Type.INTEGER:
                    self.get_logger().info(f"simple_int_param changed to {param.value}")
                else:
                    result.successful = False
                    result.reason     = "simple_int_param must be an integer"

            # 8  String guard
            elif param.name == "simple_string_param":
                if param.type_ == Parameter.Type.STRING:
                    self.get_logger().info(f"simple_string_param changed to {param.value}")
                else:
                    result.successful = False
                    result.reason     = "simple_string_param must be a string"

            # 9  Unknown parameter – reject
            else:
                result.successful = False
                result.reason     = f"Invalid parameter: {param.name}"

        return result


def main() -> None:
    # 10  Boilerplate lifecycle
    rclpy.init()
    node = SimpleParameter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()