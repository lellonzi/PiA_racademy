# Chapter 1 – Setting Up Your ROS 2 Workspace and Writing Your First Nodes

> _Goal_: By the end of this chapter you will have a functional ROS 2 workspace containing two Python nodes—a **publisher** and a **subscriber**—and you will understand **every single line** of code that makes them tick.

---

## 1  Prerequisites

- Ubuntu 22.04 or later (ROS 2 Humble recommended)
- A terminal window and basic command‑line confidence
- ROS 2 already installed and sourced (e.g. `source /opt/ros/humble/setup.bash`)

If you installed a different ROS 2 distribution, replace `humble` in the examples with the correct name.

---

## 2  Creating a Workspace

A *workspace* is simply a directory that mirrors your project. It contains your source code (`src/`), build products (`build/`) and installed artifacts (`install/`). We will call our workspace racademy_ws.

If you have your own docker setup or you are in vs code you need to do this first:
source ROS 2 on the terminal

```
. /opt/ros/humble/local_setup.bash
```

if you have the one in this guide you can start here:
enter in a terminal on your host machine

```bash
docker exec -it --user ubuntu racademy bash
```

now you are inside the docker container

```bash
# 1. Move to a convenient parent directory (adjust to taste)
$ cd github/<your_ros_ws>

# 2. Create the workspace and its source folder
$ mkdir -p racademy_ws/src

# 3. Step into the workspace root so colcon can find it
$ cd racademy_ws
```

### 2.1 First build (empty workspace)

`colcon build` discovers every package beneath the current directory’s `src/` tree, builds them, and stages the output into `install/`.

```bash
$ colcon build    # Nothing to compile yet, but this prepares directory structure
```

You should now see three folders:

```
racademy_ws/
├── build/    # CMake & Python byte‑code output
├── install/  # Ready‑to‑run executables, libraries, resources
└── src/      # Your source code lives here
```

**Possible errors**

if the colcon build does not instantly work try to

```
colcon build --cmake-clean-cache
```

[﻿source and more commands](https://answers.ros.org/question/333534/when-to-use-cmake-cleanconfigure/)

---

## 3  Creating Example Packages

ROS 2 supports several *build types*. We will create **one Python package** and (optionally) **one C++ package** so you can compare idioms later.

```bash
# Inside racademy_ws/src
$ cd src/

# 3.1  Python package
$ ros2 pkg create --build-type ament_python racademy_py_examples

# 3.2  C++ package (optional for this chapter)
$ ros2 pkg create --build-type ament_cmake  racademy_cpp_examples

# Return to workspace root and rebuild
$ cd ..
$ colcon build
```

NOTE: After the build finishes, **always** *source* the local overlay so that your shell can discover the newly built packages:

```bash
# source via absolute path
$ source install/setup.bash
```

Confirm everything worked:

```bash
$ ros2 pkg list | grep racademy
racademy_cpp_examples
racademy_py_examples
```

---

## 4  Writing `simple_publisher.py`

Create the file *`racademy_ws/src/racademy_py_examples/racademy_py_examples/simple_publisher.py`*. The full code is reproduced below, followed by an exhaustive line‑by‑line explanation.

```python
#!/usr/bin/env python3
"""A minimal ROS 2 publisher that writes a string to /chatter once per second."""

# 1 Import the rclpy client library (core ROS 2 Python API)
import rclpy

# 2 Import the base Node class we will inherit from
from rclpy.node import Node

# 3 Import the message type we intend to send
from std_msgs.msg import String


class SimplePublisher(Node):
    """Publish a string message on /chatter at 1 Hz."""

    def __init__(self) -> None:
        # 4 Call parent constructor with the node name
        super().__init__("simple_publisher")

        # 5 Create a publisher handle
        #   • String: message type
        #   • "chatter": topic name
        #   • 10: size of the outgoing message queue
        self.publisher = self.create_publisher(String, "chatter", 10)

        # 6 State variables
        self.counter = 0            # message number
        self.timer_period = 1.0     # seconds; 1 Hz

        # 7 Log a banner so the user knows the node is alive
        self.get_logger().info(f"Publishing at {1/self.timer_period:.0f} Hz")

        # 8 Register a periodic callback
        #   When `self.timer_period` elapses, `timer_callback` is invoked
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

    # 9 The callback executed every self.timer_period seconds
    def timer_callback(self) -> None:
        msg = String()
        msg.data = f"Hello World {self.counter}"

        # 10 Transmit the message
        self.publisher.publish(msg)

        # 11 Bookkeeping for the next pass
        self.counter += 1


def main() -> None:
    """ROS 2 boilerplate: initialize, spin, and shut down."""

    # 12 Initialize the rclpy system
    rclpy.init()

    # 13 Instantiate our node
    node = SimplePublisher()

    # 14 Enter the event loop—this blocks until Ctrl‑C
    rclpy.spin(node)

    # 15 Clean up explicitly (optional but good style)
    node.destroy_node()
    rclpy.shutdown()


# 16 Allow the file to be executed directly.
if __name__ == "__main__":
    main()
```

### 4.1 Why Each Line Exists

| **Line(s)** | **Purpose**                                                                                          |
| ----------- | ---------------------------------------------------------------------------------------------------- |
| 1 – 3       | Import ROS 2 core API and the message definition we will publish.                                    |
| 4           | Create a uniquely named node so ROS 2 can manage it.                                                 |
| 5           | Register as a publisher on `/chatter`; the queue length of 10 buffers bursts if the network hiccups. |
| 6           | Keep state between callbacks: `counter` increments every message; `timer_period` sets publish rate.  |
| 7           | Human‑readable console output.                                                                       |
| 8           | Arrange for `timer_callback()` to run every second.                                                  |
| 9 – 11      | Construct and publish a message, then increment the counter.                                         |
| 12 – 15     | Required boilerplate for every rclpy application.                                                    |
| 16          | Standard Python *entry‑point* check so the file doubles as a script.                                 |

---

## 5  Registering the Executable

Open *`racademy_ws/src/racademy_py_examples/setup.py`* and add the `simple_publisher` entry‑point so that `ros2 run` can find it:

```python
entry_points={
    "console_scripts": [
        "simple_publisher = racademy_py_examples.simple_publisher:main",
    ],
},
```

> **Tip** – Every time you change `setup.py` or any Python source file inside a package, you must **re‑build** and **re‑source** the workspace.

### 5.1 Declaring Runtime Dependencies

Edit *`racademy_ws/src/racademy_py_examples/package.xml`* and add two tags **after** the `<license>` element:

```xml
<exec_depend>rclpy</exec_depend>
<exec_depend>std_msgs</exec_depend>
```

These inform the ROS packaging system that your node will not run unless the `rclpy` library and the `std_msgs` interface definitions are present.

Re‑build and re‑source:

```bash
$ cd ~/github/<path_to_github>/racademy_ws
$ colcon build --symlink-install   # --symlink-install speeds up Python edits
$ source install/setup.bash
```

---

## 6  Running the Publisher

1. **Terminal 1 – Run the node**

   ```bash
   $ ros2 run racademy_py_examples simple_publisher
   [INFO] [simple_publisher]: Publishing at 1 Hz
   [INFO] [simple_publisher]: Sending: "Hello World 0"
   …
   ```

2. **Terminal 2 – Inspect topics**

   ```bash
   $ ros2 topic list
   /chatter
   /parameter_events
   /rosout

   $ ros2 topic echo /chatter
   data: Hello World 0
   data: Hello World 1
   …
   ```

Congratulations! You have written and launched your first ROS 2 publisher.

---

## 7  Writing `simple_subscriber.py`

Create *`racademy_ws/src/racademy_py_examples/racademy_py_examples/simple_subscriber.py`*:

```python
#!/usr/bin/env python3
"""A minimal ROS 2 subscriber that prints every String it receives on /chatter."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimpleSubscriber(Node):
    """Log every incoming String on /chatter."""

    def __init__(self) -> None:
        super().__init__("simple_subscriber")

        # 1 Create the subscription
        self.subscriber = self.create_subscription(
            String,                  # Message type
            "chatter",              # Topic name
            self.message_callback,   # Callback executed on arrival
            10                       # Queue size
        )

        # 2 Prevent unused‑variable warning (only needed in C++)
        self.subscriber  # noqa: F841

    # 3 Callback function
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
```

### 7.1 Add to `setup.py`

Extend the `console_scripts` list so it now reads:

```python
entry_points={
    "console_scripts": [
        "simple_publisher  = racademy_py_examples.simple_publisher:main",
        "simple_subscriber = racademy_py_examples.simple_subscriber:main",
    ],
},
```

Re‑build and re‑source **again**:

```bash
$ colcon build --symlink-install
$ source install/setup.bash
```

---

## 8  Testing the Full Pipeline

1. **Terminal 1 – Publisher**

   ```bash
   $ ros2 run racademy_py_examples simple_publisher
   ```

2. **Terminal 2 – Subscriber**

   ```bash
   $ ros2 run racademy_py_examples simple_subscriber
   [INFO] [simple_subscriber]: I heard: Hello World 0
   [INFO] [simple_subscriber]: I heard: Hello World 1
   …
   ```

3. **Terminal 3 – Inject a manual message** (optional)

   ```bash
   $ ros2 topic pub /chatter std_msgs/msg/String "data: 'Manual hello'"
   ```

   Watch Terminal 2 print the injected string.

— **End of Chapter 1**

---
