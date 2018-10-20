"""flask_app.py
Simple Flask server for viewing images on a remote browser.
"""
from flask import Flask, render_template, Response, request, render_template
from threading import Thread
import requests
import cv2

app = Flask(__name__)
"""The global Flask app used for talking to clients through HTTP"""

VID_PROC = None
"""The video processor to acquire image data from when displaying mjpg."""


@app.route('/')
def index():
    """Setup the index page when people navigate to the machine name and
    port.
    """
    return render_template('index.html')


def gen():
    """ Generate a new image stream from the camera object.

    Yields:
        A new image frame in motion jpg format
    """
    count = 0
    while True:
        frame = VID_PROC.get_last_frame()
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
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


def start_flask_thread():
    """Wrapper for starting the Flask app in a different thread."""
    print("Starting the Flask app.")
    app.run(host='0.0.0.0')


@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Wrapper to handles shutting down the server with a request"""
    shutdown_flask_server()
    return "Flask server shutting down..."


def shutdown_flask_server():
    """Handle stopping the server by running the server's shutdown
    script.
    """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError("Not running with Werkzeug Server")
    func()


class FlaskApp:
    """Class to stand up a Flask server that will allow images to be shown on a
    remote browser.
    """

    def __init__(self, vid_proc):
        """Constructor, will kick off the Flask app.

        Args:
            vid_proc(VideoProcessor): The video processor to use when acquiring
            frames.
        """
        global VID_PROC
        VID_PROC = vid_proc

        # Kick off the viewer in another thread to get it out of the way
        self.flask_thread = Thread(target=start_flask_thread, args=())
        self.flask_thread.start()

    def __del__(self):
        """Destructor. Will properly shutdown the Flask app."""
        requests.post("http://localhost:5000/shutdown")
        self.flask_thread.join(timeout=1)


