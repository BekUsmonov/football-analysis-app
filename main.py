from trackers import Tracker
from utils import read_video, save_video
import supervision as sv
import cv2
from team_assigner import TeamAssigner
from player_ball_assigner import PlayerBallAssigner
import numpy as np
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_and_distance_estimator import SpeedAndDistance_Estimator


def main():
    # 1. Read Video
    video_frames = read_video('input_videos/08fd33_4.mp4')

    # 2. Initialize Tracker
    tracker = Tracker('models/best.pt')

    tracks = tracker.get_object_tracks(
        video_frames,
        read_from_stub=True,
        stub_path='stubs/track_stubs.pkl'
    )

    # 3. Add object positions to tracks
    tracker.add_position_to_tracks(tracks)

    # 4. Camera movement estimation
    camera_movement_estimator = CameraMovementEstimator(video_frames[0])

    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(
        video_frames, read_from_stub=True, stub_path='stubs/camera_movement_stubs.pkl'
    )

    camera_movement_estimator.add_adjust_positions_to_tracks(tracks, camera_movement_per_frame)

    # 5. View transformation
    view_transformer = ViewTransformer(video_frames[0])
    view_transformer.add_transformed_position_to_tracks(tracks)
    
   
    import json

    # Convert NumPy int64 keys to int
    clean_dict = {int(k): v for k, v in tracks['players'][0].items()}
    print(json.dumps(clean_dict, indent=2))


    # 6. Interpolate missing ball positions
    tracks['ball'] = tracker.interpolate_ball_positions(tracks['ball'])

    # 7. Speed and distance estimation
    speed_and_distance_estimator = SpeedAndDistance_Estimator()
    speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)

    # 8. Assign teams
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(video_frames[0], tracks['players'][0])

    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num], track['bbox'], player_id)
            track['team'] = team
            track['team_color'] = team_assigner.team_colors[team]

    # 9. Assign ball possession
    player_assigner = PlayerBallAssigner()
    team_ball_control = []

    for frame_num, player_track in enumerate(tracks['players']):
        ball_entry = tracks['ball'][frame_num].get(1)
        if ball_entry is None:
            team_ball_control.append(team_ball_control[-1] if team_ball_control else None)
            continue

        ball_box = ball_entry['bbox']
        assigned_player = player_assigner.assign_ball_to_player(player_track, ball_box)

        if assigned_player is not None:
            player_track[assigned_player]['has_ball'] = True
            team_ball_control.append(player_track[assigned_player]['team'])
        else:
            team_ball_control.append(team_ball_control[-1] if team_ball_control else None)

    team_ball_control = np.array(team_ball_control)

    # 10. Draw output annotations
    output_video_frames = tracker.draw_annotations(video_frames, tracks, team_ball_control)

    # Draw camera movement vectors
    output_video_frames = camera_movement_estimator.draw_camera_movement(
        output_video_frames, camera_movement_per_frame
    )

    # Draw speed and distance labels
    output_video_frames = speed_and_distance_estimator.draw_speed_and_distance(
        output_video_frames, tracks
    )

    # 11. Save final output
    save_video(output_video_frames, 'output_videos/output_video.avi')


if __name__ == '__main__':
    main()
