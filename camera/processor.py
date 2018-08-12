"""video_processor.py
Classes that connect to a camera and process the imagery from it.
"""
import cv2
import time
from multiprocessing import Lock


class VideoProcessor(object):
    """ Class for accessing handling the input VideoCamera object and processing
    imagery acquired from it.
    """
    def __init__(self, video_camera):
        """Constructor.

        Args:
            video_camera(VideoCamera): The active camera object to acquire
            imagery from.
        """
        # The VideoCamera object to obtain imagery from
        self._cam = video_camera

        # Start a timer to use for various timing calculations
        self._start_time = time.time()
        # The last time that a frame was acquired
        self._frame_time = None
        # The average time between frames
        self._average_delta_time = 0
        # The actual FPS we are using from the camera
        self._effective_fps = 0
        # Start a timer to use for various timing calculations
        self._start_time = time.time()
        # The last time that a a frame was acquired
        self._frame_time = None
        # The current number of frames that have been processed
        self._frame_count = 0

        # The previous frame that was obtained from the call to get_frame
        self._last_frame = None
        # Lock to support atomic access to the image data
        self._last_frame_lock = Lock()

    def get_last_frame(self):
        """Get the last frame that was obtained by get_frame().

        Returns:
            An ndarray containing the image information.
        """
        self._last_frame_lock.acquire()
        frame = self._last_frame
        self._last_frame_lock.release()
        return frame

    def get_frame(self, vid_proc_function=None, show_fps=False):
        """Get a single frame from the camera and run some image processing
        and stat analysis on the frame.

        Args:
            vid_proc_function(function): The function to use when processing
            the images retrieved from the camera. The function must only
            take one numpy array as a parameter.
            show_fps(bool): Determine whether or not to draw the FPS in the
            top left corner of the image.

        Returns:
            The numpy array of the image that was retrieved.
        """
        # Read in a frame from the camera and update any stats (e.g. frames)
        image = self._cam.get_current_frame()
        self._frame_count += 1

        # Calculate the effective FPS through an averaging window
        delta_time = 0
        current_time = time.time()
        if self._frame_time is not None:
            delta_time = current_time - self._frame_time
            self._average_delta_time = self._average_delta_time * 0.97 + \
                delta_time * 0.03
            self._effective_fps = 1. / self._average_delta_time
        self._frame_time = current_time

        # Put the frame rate info at the top of the image
        if show_fps:
            cv2.putText(image, "FPS: " + str(round(self._effective_fps, 2)),
                        (0, 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.30, (255, 255, 255))

        # Save the frame so it can be seen later
        self._last_frame_lock.acquire()
        self._last_frame = image
        self._last_frame_lock.release()

        # Perform the user's image processing if we have a function to do so
        if vid_proc_function is not None:
            vid_proc_function(self._last_frame)

        # Convert the image to a binary string and return it
        return image
