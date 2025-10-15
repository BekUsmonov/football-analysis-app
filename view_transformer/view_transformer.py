import numpy as np
import cv2

class ViewTransformer:
    def __init__(self, frame):
        # Use frame dimensions to create a polygon that covers the visible region.
        h, w = frame.shape[:2]

        court_width = 68
        court_length = 23.32

        # Option: use full frame corners so all in-frame points get transformed
        self.pixel_vertices = np.array([
            [0, 0],
            [w - 1, 0],
            [w - 1, h - 1],
            [0, h - 1]
        ], dtype=np.float32)

        # World coordinates for perspective mapping (adjust to your desired target coords)
        self.target_vertices = np.array([
            [0, 0],
            [court_length, 0],
            [court_length, court_width],
            [0, court_width]
        ], dtype=np.float32)

        # compute transformer
        self.perspective_transformer = cv2.getPerspectiveTransform(self.pixel_vertices, self.target_vertices)

    def transform_point(self, point):
        pt = np.array(point, dtype=np.float32)
        reshaped_point = pt.reshape(-1, 1, 2)
        transformed = cv2.perspectiveTransform(reshaped_point, self.perspective_transformer)
        transformed = transformed.reshape(-1, 2)
        if np.isnan(transformed).any():
            return None
        return transformed

    def add_transformed_position_to_tracks(self, tracks):
        for obj, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    position = track_info.get('position_adjusted')
                    if position is None:
                        continue
                    position = np.array(position, dtype=np.float32)
                    position_transformed = self.transform_point(position)
                    if position_transformed is not None:
                        position_transformed = position_transformed.squeeze().tolist()
                    tracks[obj][frame_num][track_id]['transformed_position'] = position_transformed
