from calc_pixels import Cluster, storage, Pixel
from numpy import median, average, argwhere
import time

if __name__ == "__main__":
    c = Cluster(storage / 'corner2')
    data = c.data
    variance = data.var(axis=1)

    start = time.time()
    for _ in argwhere(variance < average(variance)**2):
        Pixel.register[_[0]].disable()

    c.calc_kmeans()
    print(f"done {time.time() - start} seconds")

    for klus in c.cluster_data:
        print(klus.bit_info)

    c.show_plot()
