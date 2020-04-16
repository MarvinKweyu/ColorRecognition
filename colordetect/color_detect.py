"""
Module ColorDetect
==================
Defines ColorDetect class
For example:

>>> user_image = ColorDetect("<path_to_image>")
# where color_count is the target most dominant colors to be found. Default set to 5
>>> colors =  user_image.get_color_count(color_count=5)
>>> colors
# alternatively, save these RGB values to the image
>>> user_image.save_color_count()
Image processed and saved successfully
>>>
"""

from pathlib import Path

import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.colors as mcolors


class ColorDetect:
    """
    Detect and recognize the number of colors in an image
    """

    def __init__(self, image):
        """Create ColorDetect object by providing an image"""
        self.image = cv2.imread(image)
        self.color_description = {}

    def get_color_count(self, color_count: int = 5, color_format: str = 'rgb') -> dict:
        """
        Count the number of different colors

        Parameters
        ----------
        color_count: int
            The number of most dominant colors to be obtained from the image
        color_format:str
            The format to return  the color in.
            Options:
                hsv:(60°,100%,100%)
                rgb: rgb(255, 255, 0) for yellow
                hex: #FFFF00 for yellow
                # Todo name: yellow 
        """

        # convert image from BGR to RGB for better accuracy
        rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        reshape = rgb.reshape((rgb.shape[0] * rgb.shape[1], 3))
        cluster = KMeans(n_clusters=color_count).fit(reshape)

        unique_colors = self._find_unique_colors(
            cluster, cluster.cluster_centers_)

        # round  up figures
        for percentage, v in unique_colors.items():
            rgb_value = list(np.around(v))
            if color_format != 'rgb':
                color_value = self._format_color(v, color_format)
                self.color_description[round(percentage, 2)] = color_value
            else:
                self.color_description[round(percentage, 2)] = rgb_value
        return self.color_description

    def _format_color(self, rgb_value, color_format):
        """
        Get the correct color format as specified
        :return:
        """
        if color_format == 'hsv':
            # list(np.around(v))
            return mcolors.rgb_to_hsv(rgb_value)  # <class 'numpy.ndarray'>

        elif color_format == 'hex':
            rgb_value = np.divide(rgb_value, 255)  # give a scale from 0-1
            # Todo: Normalize rgb_value to get a range of 0-1 on each scale mcolors.Normalize
            return mcolors.to_hex(rgb_value)

    def _find_unique_colors(self, cluster, centroids) -> dict:

        # Get the number of different clusters, create histogram, and normalize
        labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
        (hist, _) = np.histogram(cluster.labels_, bins=labels)
        hist = hist.astype("float")
        hist /= hist.sum()

        # iterate through each cluster's color and percentage
        colors = sorted([((percent * 100), color)
                         for (percent, color) in zip(hist, centroids)])

        for (percent, color) in colors:
            color.astype("uint8").tolist()
        return dict(colors)

    def write_color_count(self):
        """
        Write the number of colors found to the image
        """
        y_axis = 200
        for k, v in self.color_description.items():
            font = cv2.FONT_HERSHEY_SIMPLEX
            bottomLeftCornerOfText = (10, y_axis)
            fontScale = 1
            fontColor = (0, 0, 0)
            lineType = 1

            cv2.putText(self.image, str(k) + '% :' + str(v),
                        bottomLeftCornerOfText,
                        font,
                        fontScale,
                        fontColor,
                        lineType)
            y_axis += 23

    def save_color_count(self, location=".", file_name="out.jpg"):
        """
        Save the resultant image file to the local directory

        Parameters
        ----------
        location: str
            The file location of the image
        file_name:str
            The name of the new image

        """
        # write image colors to the image
        self.write_color_count()

        image_folder = Path(location)
        image_to_save = image_folder / file_name

        # Save image
        cv2.imwrite(str(image_to_save), self.image)

        print("Image processed and saved successfully")
