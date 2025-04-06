# IRL-Streaming-Switcher
The Python script monitors the incoming live stream's bitrate from the nginx RTMP server. If the bitrate drops below a predefined threshold, it automatically switches the YouTube stream to a standby (offline) placeholder image, and restores the main stream when the bitrate returns to normal.
