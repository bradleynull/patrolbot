"""main.py
Simple flask application for streaming motion jpg images to a web browser.
"""
from flask import Flask, render_template, Response, request, render_template
from camera.processor import VideoProcessor
from camera.camera import VideoCamera
import cv2
import requests
import signal
from threading import Thread

app = Flask(__name__)
"""The global Flask app used for talking to clients through HTTP"""


@app.route('/')
def index():
    """Setup the index page when people navigate to the machine name and port"""
    return render_template('index.html')


def gen(vid_proc):
    """ Generate a new image stream from the camera object.

    Args:
        vid_proc(VideoProcessor): The VideoProcessor object to grab the camera
        frame and perform image processing on it.

    Yields:
        A new image frame in motion jpg format
    """
    count = 0
    while True:
        frame = vid_proc.get_last_frame()
        if frame is not None:
            yield(b'--frame\r\n'
                  b'Content-Type:image/jpeg\r\n\r\n' +
                  cv2.imencode('.jpg', frame)[1].tostring() +
                  b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    """ Start a new video feed by telling the browser we're about to send motion
    jpg frames

    Returns:
        The Flask response to the client.
    """
    return Response(gen(vid_proc),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def start_flask_thread():
    """Wrapper for starting the Flask app in a different thread."""
    print("Starting the Flask app.")
    # app.run(host='0.0.0.0', debug=False, use_reloader=False)
    app.run(host='0.0.0.0')


@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Wrapper to handles shutting down the server with a request"""
    shutdown_flask_server()
    return "Flask server shutting down..."


def shutdown_flask_server():
    """Handle stopping the server by running the server's shutdown script."""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError("Not running with Werkzeug Server")
    func()


if __name__ == '__main__':
    # Start the app so that anyone on the network can see it
    vid_proc = VideoProcessor(VideoCamera(device=0, width=1280, height=720,
                                          multithread=True))
    # Get one frame so that the video fee will populate
    vid_proc.get_frame()
    # Kick off the viewer in another thread to get it out of the way
    flask_thread = Thread(target=start_flask_thread, args=())
    flask_thread.start()

    def signal_handler(sig, frame):
        global running

        requests.post("http://127.0.0.1:5000/shutdown")
        flask_thread.join(timeout=1)
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    running = True

    while running:
        vid_proc.get_frame(show_fps=True)
