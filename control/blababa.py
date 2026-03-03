# print(f"Detected {len(our_robots)} of our robots.")
# for robot_info in our_robots:
#     robot_id = robot_info.robot_id
#     x, y, orientation = robot_info.x, robot_info.y, robot_info.orientation

#     print(f"Robot {robot_id}: x={x:.1f}, y={y:.1f}, θ={orientation:.2f}")
#     try:
#         can_play = enforce_game_rules(robot_info, ball_info, components, gc_parser)

#         if can_play:
#             print("robo vai jogar")
#             gc_data = gc_parser.get_last_data()
#             process_robot_logic(robot_info, ball_info, components)
#         else:
#             print("pararei de jogar")
#             # Para o robô se não puder jogar
#             components["robot_senders"][robot_id].stop()

#     except Exception as e:
#         logger.error(f"Error processing robot {robot_id}: {e}", exc_info=True)
