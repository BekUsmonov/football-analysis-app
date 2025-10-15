import sys
sys.path.append('../')
from utils import measure_distance, get_foot_position
import cv2

class SpeedAndDistance_Estimator:
    def __init__(self, frame_window=5, frame_rate=24):
        self.frame_window = frame_window
        self.frame_rate = frame_rate

    def add_speed_and_distance_to_tracks(self, tracks):
        total_distance = {}

        for object_type, object_tracks in tracks.items():
            if object_type in ["ball", "referees"]:
                continue

            number_of_frames = len(object_tracks)

            for frame_num in range(0, number_of_frames, self.frame_window):
                last_frame = min(frame_num + self.frame_window, number_of_frames - 1)

                for track_id, _ in object_tracks[frame_num].items():
                    if track_id not in object_tracks[last_frame]:
                        continue

                    start_position = object_tracks[frame_num][track_id].get('transformed_position')
                    end_position = object_tracks[last_frame][track_id].get('transformed_position')

                    if start_position is None or end_position is None:
                        continue

                    distance_covered = measure_distance(start_position, end_position)
                    time_elapsed = (last_frame - frame_num) / self.frame_rate

                    if time_elapsed == 0:
                        continue

                    speed_meters_per_second = distance_covered / time_elapsed
                    speed_km_per_hour = speed_meters_per_second * 3.6

                    total_distance.setdefault(object_type, {}).setdefault(track_id, 0)
                    total_distance[object_type][track_id] += distance_covered

                    for frame_num_batch in range(frame_num, last_frame):
                        if track_id not in object_tracks[frame_num_batch]:
                            continue
                        object_tracks[frame_num_batch][track_id]['speed'] = speed_km_per_hour
                        object_tracks[frame_num_batch][track_id]['distance'] = total_distance[object_type][track_id]

    def draw_speed_and_distance(self, frames, tracks):
        output_frames = []

        for frame_num, frame in enumerate(frames):
            for object_type, object_tracks in tracks.items():
                if object_type in ["ball", "referees"]:
                    continue

                if frame_num >= len(object_tracks):
                    continue

                for _, track_info in object_tracks[frame_num].items():
                    speed = track_info.get("speed")
                    distance = track_info.get("distance")
                    bbox = track_info.get("bbox")

                    if not bbox or speed is None or distance is None:
                        continue

                    position = list(get_foot_position(bbox))
                    position[1] += 40
                    position = tuple(position)

                    cv2.putText(frame, f"{speed:.2f} km/h", position,
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                    cv2.putText(frame, f"{distance:.2f} m", (position[0], position[1] + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

            output_frames.append(frame)

        return output_frames

                
               