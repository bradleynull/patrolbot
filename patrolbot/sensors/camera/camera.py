"""camera.py
Classes for accessing onboard raspberry pi camera
"""
import cv2
from threading import Thread


class VideoCamera(object):
    """ Class for accessing the camera attached to the RPi.
    """
    def __init__(self, device=0, width=640, height=480, fps=30,
                 multithread=False):
        """Constructor.

        Args:
            device(int): The device id of the camera to connect to
            width(int): The width of the images to acquire from the camera in
            pixels.
            height(int): The height of the images to acquire from the camera in
            pixels.
            fps(int): The number of frames per second to request from the camera
            multithread(bool): If set to True, a background thread will be used
            to acquire the most recent image from the camera. If False, the most
            recent image in the buffer will be read when get_frame() is called.
        """
        # The device id for the camera to connect to
        self._device_id = device
        # The desired image width to request
        self._img_width = width
        # The desired image height to request
        self._img_height = height
        # The desired frames per second to request
        self._requested_fps = fps
        # If true, the multithreading image acqusition will be used
        self._multithread = multithread
        # The most up to date frame we have from the camera stream
        self._current_frame = None
        # Flag to signal that we want to retrieve the next frame instead
        # of just grabbing it from the buffer
        self._retrieve_frame = False
        # Variable to control the frame grabbing thread
        self._stopped = False

        # Video capture device connected to the web cam
        self._video = cv2.VideoCapture(self._device_id)
        self._video.set(cv2.CAP_PROP_FRAME_WIDTH, self._img_width)
        self._video.set(cv2.CAP_PROP_FRAME_HEIGHT, self._img_height)
        self._video.set(cv2.CAP_PROP_FPS, self._requested_fps)

        # Go ahead and start the update thread
        if self._multithread:
            self._update_thread = Thread(target=self.update, args=())
            self._update_thread.start()

    def release(self):
        """Release the resources the camera has been holding onto prior to
        it being deleted.
        """
        # Stop the frame grabber thread
        self._stopped = True
        if self._multithread:
            self._update_thread.join(1000)
        # Cleanup the web cam
        self._video.release()

    def update(self):
        """Thread to continually read frames from the camera buffer so we are
        always as up to date as possible."""
        while not self._stopped:
            self._video.grab()

            if self._retrieve_frame:
                success, self._current_frame = self._video.retrieve()

    def get_current_frame(self):
        """Signal that we want to actually retrieve a frame from the camera.

        Returns:
            ndarray of the current frame retrieved from the camera
        """

        # Just grab the most recent frame from the buffer and return it if
        # we are not using the multithreaded method
        if not self._multithread:
            success, self._current_frame = self._video.read()
            return self._current_frame

        # Set the frame to None, signal that we want a new frame, then wait
        # for it to show up
        self._current_frame = None
        self._retrieve_frame = True
        while self._current_frame is None:
            pass
        # Set this back to False so we don't keep retrieving frames
        self._retrieve_frame = False

        return self._current_frame
