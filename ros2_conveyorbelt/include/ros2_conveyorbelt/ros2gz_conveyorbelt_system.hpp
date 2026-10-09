#ifndef ROS2GZ_CONVEYORBELT_SYSTEM_HPP
#define ROS2GZ_CONVEYORBELT_SYSTEM_HPP

#include <memory>
#include <mutex>
#include <chrono>
#include <limits>
#include <string>
#include <thread>

#include <rclcpp/rclcpp.hpp>
#include <rclcpp/executors.hpp>
#include <conveyorbelt_msgs/msg/conveyor_belt_state.hpp>
#include <conveyorbelt_msgs/srv/conveyor_belt_control.hpp>

// Gazebo Sim (Harmonic)
#include <gz/sim/System.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/Entity.hh>
#include <gz/sim/EntityComponentManager.hh>
#include <gz/sim/Types.hh>
#include <gz/sim/components/Name.hh>
#include <gz/sim/components/JointVelocityCmd.hh>
#include <gz/sim/components/JointPosition.hh>
#include <gz/sim/components/JointPositionReset.hh>
#include <gz/sim/Util.hh>

#include <gz/common/Console.hh>

namespace gz_conveyor
{
class ROS2ConveyorBeltSystem
  : public gz::sim::System,
    public gz::sim::ISystemConfigure,
    public gz::sim::ISystemPreUpdate
{
public:
  ROS2ConveyorBeltSystem() = default;
  ~ROS2ConveyorBeltSystem() override;

  // Gazebo entry points
  void Configure(const gz::sim::Entity &entity,
                 const std::shared_ptr<const sdf::Element> &sdf,
                 gz::sim::EntityComponentManager &ecm,
                 gz::sim::EventManager &eventMgr) override;

  void PreUpdate(const gz::sim::UpdateInfo &info,
                 gz::sim::EntityComponentManager &ecm) override;

private:
  // ROS 2
  rclcpp::Node::SharedPtr ros_node_;
  std::shared_ptr<rclcpp::executors::SingleThreadedExecutor> executor_;
  std::thread executor_thread_;

  rclcpp::Publisher<conveyorbelt_msgs::msg::ConveyorBeltState>::SharedPtr status_pub_;
  rclcpp::Service<conveyorbelt_msgs::srv::ConveyorBeltControl>::SharedPtr power_srv_;
  std::mutex mtx_;  // protects power_ and belt_velocity_

  // Model / joint
  gz::sim::Entity model_{gz::sim::kNullEntity};
  gz::sim::Entity joint_{gz::sim::kNullEntity};
  std::string joint_name_{"belt_joint"};

  // Params
  double max_velocity_{1.0};     // m/s
  double power_{0.0};            // [0..100]
  double belt_velocity_{0.0};    // m/s (derived)
  double lower_limit_{0.0};      // meters
  double upper_limit_{0.01};     // meters (wrap distance target)
  double publish_rate_{1000.0};  // Hz

  // Wrap control
  bool pending_reset_{false};

  // Distance integrator (for deterministic wrap even without JointPosition)
  double travel_accum_{0.0};  // meters since last wrap
  std::chrono::nanoseconds last_time_{std::chrono::nanoseconds(0)};

  // Publish throttling (by sim time)
  std::chrono::nanoseconds publish_period_{std::chrono::nanoseconds(1'000'000)};
  std::chrono::nanoseconds last_pub_sim_{std::chrono::nanoseconds(0)};

  // Helpers
  void onSetPower(const conveyorbelt_msgs::srv::ConveyorBeltControl::Request::SharedPtr req,
                  conveyorbelt_msgs::srv::ConveyorBeltControl::Response::SharedPtr res);

  void publishStatus();
};
} // namespace gz_conveyor

#endif // ROS2GZ_CONVEYORBELT_SYSTEM_HPP
