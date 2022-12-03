import pandas as pd

from model.camera import CameraPosition
from model.snap import RawSnapData
from model.spherical_coordinate import SphereCoord
from model.triangulation import triangulate


class Pixel(SphereCoord):
    def __init__(self, led_id: int,  x: float, y: float, z: float):
        self.id = led_id
        super().__init__(x, y, z)


class CameraInfo:
    """
    This class holds all information available for all camera positions
    """
    def __init__(self):
        self.iteration = 0
        self.main_camera = None  # The main camera is the first camera added. All other cameras are referenced to this camera
        self.camera_pos = pd.DataFrame(columns=['x', 'y', 'z', 'name', 'origin_x', 'origin_y', 'iteration'])

    def add_camera(self, cam: CameraPosition):
        """
        Add a possible camera position
        :param cam: Camera position
        :return:
        """
        if not self.main_camera:
            self.main_camera = cam.name

        df = cam.data_frame
        df['iteration'] = self.iteration
        self.camera_pos = pd.concat(self.camera_pos, df)

    @staticmethod
    def triangulate(cam1: RawSnapData, cam2: RawSnapData, cam3: RawSnapData):
        """
        Triangulate 3 camera positions to the most likely locations.
        Re Calculate the locations of all visible pixels based on the new camera locations.
        Store the new pixel locations
        :param cam1:
        :param cam2:
        :param cam3:
        :return:
        """
        angles = triangulate(cam1, cam2, cam3)


class PixelPositions:
    def __init__(self):
        pass
