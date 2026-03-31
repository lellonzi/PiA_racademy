# Chapter 3 – Working with ROS 2 Parameters

> _Goal_: Learn how to declare, read, update, and validate parameters so your nodes become configurable at run‑time.

## 1  What Are Parameters?

A **parameter** is a named, strongly‑typed value stored inside a node’s private key‑value map. Parameters let you:

- **Configure** behaviour at launch (`ros2 run … -p name:=value`)
- **Inspect** and **tune** a running node (`ros2 param get` / `set`)
- Persist settings in YAML files that load automatically

Supported types are **Boolean**, **Integer**, **Double**, **String**, **ByteArray**, **BoolArray**, **IntegerArray**, and **DoubleArray**.

Every node starts with an *empty* parameter set. You must explicitly `declare_parameter()` each key you intend to use—otherwise attempts to read or change it will fail.

---

## 2  Writing `simple_parameter.py`

Create *`racademy_ws/src/racademy_py_examples/racademy_py_examples/simple_parameter.py`*.

```python
#!/usr/bin/env python3
"""Demonstrate declaring, reading, and dynamically updating parameters."""

#  1  Core ROS 2 Python API
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
```

### 2.1  Line‑by‑Line Synopsis

| **Line(s)** | **Purpose**                                                                      |
| ----------- | -------------------------------------------------------------------------------- |
| 1–2         | Import ROS 2 client library and parameter message types.                         |
| 3           | Initialise the node named `simple_parameter`.                                    |
| 4           | Declare parameters with defaults—these now exist in the node’s parameter server. |
| 5           | Register a validation callback executed *atomically* before parameters apply.    |
| 6–9         | Inspect each incoming change; accept or reject based on name and type.           |
| 10          | Standard ROS 2 start‑spin‑shutdown sequence.                                     |

---

## 3  Package Integration

### 3.1  `package.xml`

Add the runtime dependency:

```xml
<exec_depend>rcl_interfaces</exec_depend>
```

### 3.2  `setup.py`

Extend the `console_scripts` list:

```python
entry_points={
    "console_scripts": [
        "simple_publisher  = racademy_py_examples.simple_publisher:main",
        "simple_subscriber = racademy_py_examples.simple_subscriber:main",
        "simple_parameter  = racademy_py_examples.simple_parameter:main",
    ],
},
```

Re‑build and re‑source:

```bash
$ colcon build --symlink-install
$ source install/setup.bash
```

---

## 4  Running and Interacting

### 4.1  Launch with defaults

```bash
$ ros2 run racademy_py_examples simple_parameter
```

### 4.2  Query parameter values

```bash
$ ros2 param get /simple_parameter simple_string_param
# prints: "voss"
```

### 4.3  Override at startup

```bash
$ ros2 run racademy_py_examples simple_parameter \
      --ros-args -p simple_int_param:=30
$ ros2 param get /simple_parameter simple_int_param   # prints 30
```

### 4.4  Change while running

```bash
$ ros2 param set /simple_parameter simple_int_param 34
```

Watch the node’s log output confirm the change. Attempting an invalid type, e.g. `ros2 param set /simple_parameter simple_int_param "oops"`, will be **rejected** by our callback and ROS 2 will print the reason.

---

## 5  Why Use Callbacks?

- Validate ranges and types before a bad value crashes your controller.
- Apply side‑effects (e.g. resize buffers) immediately after acceptance.
- Emit warnings or trigger events when certain thresholds change.

---

— **End of Chapter 3**

---
