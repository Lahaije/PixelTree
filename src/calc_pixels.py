import json

import cv2
import time
from typing import List, Union
from numpy import zeros, array
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

from webcam import read_im
from config import storage, NUM_PIXELS
from model.bit_info import BitInfo


class Pixel:
    register: List['Pixel'] = []

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.group = 0
        self.disabled = False
        self.id = len(self.register)  # Id of pixel
        self.register.append(self)

    def disable(self):
        self.disabled = True
        self.group = -1


def make_pixel(x, y):
    for i in range(x):
        for j in range(y):
            Pixel(i, j)


class ClusterGroup:
    """
    A ClusterGroup represents a cluster of pixels with similar properties.
    """
    def __init__(self, data: List, series_name):
        self.data = data
        self._center = []
        self.bit_info = BitInfo(self.data, series_name)
        self.pixel_id = []

    def add_pixel(self, pid: Union[int, List[int]]):
        if isinstance(pid, int):
            self.pixel_id.append(pid)
        else:
            self.pixel_id.extend(pid)
        self._center = []

    @property
    def size(self):
        return len(self.pixel_id)

    @property
    def center(self) -> array:
        if not self._center:
            x = 0
            y = 0
            for pid in self.pixel_id:
                pixel = Pixel.register[pid]
                x += pixel.x
                y += pixel.y
            self._center = [int(x/len(self.pixel_id)), int(y/len(self.pixel_id))]
        return self._center

    def disable_pixels(self):
        """
        Disable all pixels from cluster for further calculations
        :return:
        """
        for pid in self.pixel_id:
            Pixel.register[pid].disable()


class Cluster:
    def __init__(self, series_name, num_frames: int = 8, num_leds: int = NUM_PIXELS):
        Pixel.register = []
        self.series_name = series_name
        self.storage = storage
        self.ground = read_im(f'{series_name}/ground')
        self.all = read_im(f'{series_name}/all')
        self.X = self.ground.shape[0]
        self.Y = self.ground.shape[1]
        make_pixel(self.X, self.Y)

        self.num_frames = num_frames
        self.num_leds = num_leds
        self.images = self.load_images()

        self.data = zeros((self.X * self.Y, num_frames), dtype=int)
        self.cluster_data: List[ClusterGroup] = []

        self.detected_led: List[ClusterGroup] = []  # Array to hold likely locations of leds.

        self.disabled_pixels = {}  # This list excludes pixels from being grouped
        self.fill_data()

    def load_images(self):
        images = [read_im(f'{self.series_name}/{self.num_frames-n-1}') for n in range(self.num_frames)]
        return [cv2.cvtColor(cv2.absdiff(_, self.ground), cv2.COLOR_BGR2GRAY) for _ in images]

    def fill_data(self):
        counter = 0
        for i in range(self.X):
            for j in range(self.Y):
                self.data[counter] = [self.images[_][i][j] for _ in range(self.num_frames)]
                counter += 1

    def calc_kmeans(self):
        data = self.data[[not p.disabled for p in Pixel.register]]
        print(len(data))
        km = KMeans(n_clusters=self.num_leds).fit(data)
        self.cluster_data = [ClusterGroup(row, self.series_name) for row in km.cluster_centers_]

        prediction = km.predict(data)

        counter = 0
        for p in Pixel.register:
            if p.disabled:
                continue
            p.group = prediction[counter]
            self.cluster_data[prediction[counter]].add_pixel(p.id)
            counter += 1

    def biggest_cluster(self) -> ClusterGroup:
        """
        :return: the ClusterGroup with the most pixels
        """
        return max(self.cluster_data, key=lambda x: x.size)

    def filter_ground_all(self):
        """Filter out all pixels with a small difference between full on and off"""
        diffim = cv2.absdiff(c.ground, c.all)

        counter = 0
        for i in range(self.X):
            for j in range(self.Y):
                weight = sum(diffim[i, j])
                if weight < 21:
                    Pixel.register[counter].disable()

    def filter_by_biggest(self, max_cluster_size=100):
        while self.biggest_cluster().size > max_cluster_size:
            print(f"Removing {self.biggest_cluster().size} pixels")
            self.biggest_cluster().disable_pixels()
            self.calc_kmeans()

    def filter_by_low_score(self):
        while len(self.detected_led) < self.num_leds:
            print(f"LEN = {len(self.detected_led)}")

            self.calc_kmeans()
            self.cluster_data.sort(key=lambda x: x.bit_info.score)
            # Use the best scoring 20% of clusters
            smallest = self.cluster_data[0]
            largest = self.cluster_data[0]
            for i in range(1, int(self.num_leds/5)):
                if self.cluster_data[i].size < smallest.size:
                    smallest = self.cluster_data[i]
                if self.cluster_data[i].size > largest.size:
                    largest = self.cluster_data[i]

            self.register_detected(smallest)

            largest.disable_pixels()
            smallest.disable_pixels()

    def register_detected(self, cluster: ClusterGroup):
        for c in self.detected_led:
            if c.bit_info.bit_number != cluster.bit_info.bit_number:
                continue
            # Check if the centers of both clusters are in the cloud of surrounding pixels
            if (c.center[0]-cluster.center[0])**2 + (c.center[1]-cluster.center[1])**2 < c.size + cluster.size:
                c.add_pixel(cluster.pixel_id)
                return
        self.detected_led.append(cluster)

    def show_plot(self):
        data = zeros((self.X, self.Y))
        for p in Pixel.register:
            data[p.x, p.y] = p.group
        plt.clf()
        plt.imshow(data)
        self.plot_cluster_center()
        plt.show()

    def plot_groups(self):
        counter = 0
        for c in self.data:
            plt.plot(c)

            if counter == 5:
                plt.show()
                counter = 0
            else:
                counter += 1

    def plot_cluster_center(self):
        x = []
        y = []
        for cluster in self.detected_led:
            x.append(cluster.center[0])
            y.append(cluster.center[1])
        plt.scatter(y, x, s=2, marker='*',)

    def plot_group_number(self):
        for cluster in self.detected_led:

            if cluster.bit_info.led_key < 0:
                """
                print(f"For cluster with {cluster.bit_info.bit_number} no match. Location {cluster.center}")
                print(f"Data = {cluster.data}")
                """
                continue

            plt.text(cluster.center[1], cluster.center[0], cluster.bit_info.led_key, fontsize=12, color='red')

    def show_results(self):
        plt.imshow(self.all)
        self.plot_cluster_center()
        self.plot_group_number()
        plt.show()

    def write_data(self):
        result = []
        for row in self.detected_led:
            result.append({'x': row.center[0], 'y': row.center[1],
                           'led': row.bit_info.led_key,
                           'bit': row.bit_info.bit_string,
                           'random': row.bit_info.bit_number})

        with (storage / self.series_name / 'data.txt') as file:
            file.write_text(json.dumps(result))

    def write_result_plot(self):
        plt.clf()
        plt.imshow(self.all)
        with (storage / self.series_name / 'data.txt') as file:
            data = json.loads(file.read_text())

        for i in data:
            try:
                row = data[i]
            except TypeError:
                # Workaround for old data files.
                row = i
            plt.scatter(row['y'], row['x'], s=2, marker='*', edgecolors='blue')
            plt.text(row['y'], row['x'], row['led'], fontsize=12, color='red')

        plt.savefig(storage / self.series_name / 'results.png')

    def store_results(self):
        self.write_data()
        self.write_result_plot()


if __name__ == "__main__":
    for folder in storage.iterdir():
        print(f"start {folder}")
        start = time.time()
        c = Cluster(folder)
        c.filter_by_low_score()
        c.store_results()
        print(f"done {int(time.time()-start)} seconds")
