"""main.py
App that will kick off the PatrolBot processing.
"""
from camera.processor import VideoProcessor
from camera.camera import VideoCamera
import cv2
import signal
from gui.pitft_main_window import PiTftMainWindow
from flask_app.flask_app import FlaskApp
from argparse import ArgumentParser


if __name__ == '__main__':
    parser = ArgumentParser(description="PatrolBot App.")
    parser.add_argument('--flask', action='store_const', const=True,
                        help="Use Flask to enable viewing imagery from the "
                             "browser on port 5000.")
    args = parser.parse_args()

    # The main PyGame window that we will use to display and get touch
    # screen input from
    mw = PiTftMainWindow((320, 240))

    # Start the app so that anyone on the network can see it
    vid_proc = VideoProcessor(VideoCamera(device=0,
                                          width=mw.size[0],
                                          height=mw.size[1],
                                          fps=60,
                                          multithread=False))

    # Get one frame so that the video fee will populate
    vid_proc.get_frame()
    if args.flask:
        flask_app = FlaskApp(vid_proc)
    else:
        # Install our own signal handler so the user can gracefully exit.
        def signal_handler(sig, frame):
            global running
            running = False
            print("\nPatrolBot: Caught SIGINT. Quitting.")

        signal.signal(signal.SIGINT, signal_handler)

    running = True
    while running:
        vid_proc.get_frame(show_fps=True)
        mw.update(
            cv2.cvtColor(
                cv2.resize(
                    cv2.flip(
                        cv2.rotate(vid_proc.get_last_frame(),
                                   cv2.ROTATE_90_COUNTERCLOCKWISE),
                        0),
                    (mw.size[1], mw.size[0])),
                cv2.COLOR_BGR2RGB)
        )