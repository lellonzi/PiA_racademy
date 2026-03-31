# Chapter 4 – Visualising a Live URDF in RViz with *robot_state_publisher*

> _Goal_: Publish your robot’s TF tree from the URDF, drive joint angles interactively, and build an RViz configuration you can reuse.

## 1 Conceptual Flow

```
URDF (xacro) ──▶ robot_description parameter ──▶ robot_state_publisher ─▶ TF frames
                                                 ▲
                                                 │
                            joint_state_publisher / GUI ─▶ sensor_msgs/JointState
```

- **robot_state_publisher** – Reads the static URDF, subscribes to joint states, and continuously publishes the complete transform tree.
- **joint_state_publisher_gui** – Emits real‑time `sensor_msgs/JointState` messages from a slider panel (perfect for modelling **continuous** joints such as wheels).
- **RViz** – Visualises both the TF tree and the rendered mesh geometry.

---

## 2 Launching the State Publisher

### 2.1 Terminal 1

```bash
$ ros2 run robot_state_publisher robot_state_publisher \
      --ros-args -p robot_description:="$(xacro \
        $(pwd)/src/racademy_description/urdf/racademy.urdf.xacro)"
```

| **Fragment**                                           | **What it does**                                                                                |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| `ros2 run robot_state_publisher robot_state_publisher` | Execute the node.                                                                               |
| `--ros-args`                                           | Everything that follows is interpreted by rcl arguments parser.                                 |
| `-p robot_description:=…`                              | Inject a *parameter* named `robot_description`.                                                 |
| `$(xacro …)`                                           | Shell substitution: run `xacro`, convert the macro file into plain URDF, and inline the result. |
| `$(pwd)/…`                                             | Expands to an absolute path so ROS finds the file regardless of the current directory.          |

> **Tip** – Wrapping the long command in a launch file is cleaner; we keep it inline here for educational clarity.

---

## 3 Publishing Joint States

### 3.1 Continuous wheel joints

Your URDF defines the wheels as

```xml
<joint name="wheel_left_joint" type="continuous">
```

A **continuous joint** has unlimited rotation but requires live angle data. Without it, every wheel frame stays frozen at 0 rad.

### 3.2 Terminal 2 – Slider GUI

```bash
$ ros2 run joint_state_publisher_gui joint_state_publisher_gui
```

Move the sliders labelled `wheel_left_joint`, `wheel_right_joint`, etc. The GUI emits a `JointState` topic that the state publisher converts into TF transforms.

---

## 4 Launching RViz

### 4.1 Terminal 3

```bash
$ ros2 run rviz2 rviz2
```

### 4.2 Initial RViz setup

1. **Fixed Frame** – Set to `base_footprint`, matching the root link declared in Chapter 2:

   ```xml
   <link name="base_footprint"/>
   ```

2. **Add Displays**
   - **TF** – Visualise the complete frame hierarchy.
   - **RobotModel** – Choose *Description Topic* `/robot_description` (already published by robot_state_publisher).

Your screen should now show the chassis and a pair of wheels whose orientation updates live when you drag the GUI sliders.

---

## 5 Saving an RViz Configuration

RViz stores layouts in `~/.rviz2/`. To persist the view for teammates:

```bash
# Inside a fourth terminal or RViz menu: File ▸ Save
$ mkdir -p src/racademy_description/rviz
$ cp ~/.rviz2/default.rviz \
      src/racademy_description/rviz/display.rviz
```

add into /Users/gabrielvoss/Documents/GitHub/Robotics_academy/racademy_ws/src/racademy_description/CMakeLists.txt

```bash
install(
  DIRECTORY meshes rviz urdf
  DESTINATION share/${PROJECT_NAME}
)
```

| **Command**                  | **Explanation**                                                                                     |
| ---------------------------- | --------------------------------------------------------------------------------------------------- |
| `mkdir -p …/rviz`            | Create a dedicated folder inside the *description* package.                                         |
| `cp ~/.rviz2/default.rviz …` | Copy the freshly saved layout so it becomes part of version control and can ship with your package. |

Later you can launch RViz pre‑configured with:

```bash
$ ros2 run rviz2 rviz2 -d $(ros2 pkg prefix racademy_description)/share/racademy_description/rviz/display.rviz
```

---

## 6 Troubleshooting Checklist

- **Robot invisible?** Ensure `robot_description` parameter was set (inspect with `ros2 param list /robot_state_publisher`).
- **Wheels don’t rotate?** Verify `joint_state_publisher_gui` is running and publishing (`ros2 topic echo /joint_states`).
- **Mesh path errors?** Remember to `colcon build && source install/setup.bash` after adding new files so the package URI resolves.

---

— **End of Chapter 4**

---
