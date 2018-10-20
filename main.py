"""main.py
App that will kick off the PatrolBot processing.
"""
from argparse import ArgumentParser
import cv2
import signal
from patrolbot.sensors.camera.processor import VideoProcessor
from patrolbot.sensors.camera.camera import VideoCamera
from patrolbot.gui.pitft_main_window import PiTftMainWindow
from patrolbot.flask_app.flask_app import FlaskApp
from patrolbot.logger.logger import Logger


if __name__ == '__main__':
    parser = ArgumentParser(description="PatrolBot App.")
    parser.add_argument('--flask', action='store_const', const=True,
                        help="Use Flask to enable viewing imagery from the "
                             "browser on port 5000.")
    args = parser.parse_args()

    log = Logger().get_logger()

    # The main PyGame window that we will use to display and get touch
    # screen input from
    mw = PiTftMainWindow((320, 240))

    # Start the app so that anyone on the network can see it
    log.info("Launching the video processor.")
    vid_proc = VideoProcessor(VideoCamera(device=0,
                                          width=mw.size[0],
                                          height=mw.size[1],
                                          fps=60,
                                          multithread=False))

    # Get one frame so that the video fee will populate
    vid_proc.get_frame()
    if args.flask:
        log.info("Setting up the Flask interface.")
        flask_app = FlaskApp(vid_proc)
    else:
        # Install our own signal handler so the user can gracefully exit.
        def signal_handler(sig, frame):
            global running
            running = False
            log.info("Caught SIGINT. Quitting.")

        signal.signal(signal.SIGINT, signal_handler)

    log.info("Starting the processing loop.")
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