#!/usr/bin/env python3

import subprocess
import requests
import xml.etree.ElementTree as ET
import time

# Configuration
STREAM_NAME = "STREAM KEY NAME"  # Stream key to send to the server
HLS_URL = "http://localhost:8080/hls/{STREAM_NAME}.m3u8"
STREAM_URL = "rtmp://{Stream URL}" #Streaming URL
OFFLINE_IMAGE = "/home/ubuntu/offline.png"  # Offline image

STAT_URL = "http://localhost:8080/stat"
BITRATE_THRESHOLD = 500

def get_bitrate(stream_name):
    try:
        response = requests.get(STAT_URL)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        for stream in root.findall(".//application/live/stream"):
            if stream.find("name").text == stream_name:
                bw_in = stream.find("bw_in").text
                return int(bw_in) / 1024  # kbps
        return 0
    except:
        return 0

def start_main_stream():
    return subprocess.Popen([
        "ffmpeg", "-re", "-fflags", "+genpts", "-i", HLS_URL,
        "-vf", "format=yuv420p,scale=1280:720", "-c:v", "libx264",
        "-preset", "veryfast", "-g", "60", "-keyint_min", "60", "-r", "30",
        "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-f", "flv", STREAM_URL
    ])

def start_offline_stream():
    return subprocess.Popen([
        "ffmpeg", "-loop", "1", "-re", "-i", OFFLINE_IMAGE,
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-vf", "format=yuv420p,scale=1280:720", "-c:v", "libx264",
        "-preset", "veryfast", "-tune", "stillimage", "-g", "60",
        "-keyint_min", "60", "-r", "30", "-c:a", "aac", "-b:a", "128k",
        "-ar", "44100", "-f", "flv", STREAM_URL
    ])

if __name__ == "__main__":
    is_offline = False
    main_process = start_main_stream()

    try:
        while True:
            bitrate = get_bitrate(STREAM_NAME)
            print(f"Current bitrate: {bitrate:.2f} kbps")

            if bitrate < BITRATE_THRESHOLD:
                if not is_offline:
                    print("Bitrate dropped. Switching to offline placeholder image.")
                    main_process.terminate()
                    main_process.wait()
                    offline_process = start_offline_stream()
                    is_offline = True
            else:
                if is_offline:
                    print("Bitrate restored. Switching back to main stream.")
                    offline_process.terminate()
                    offline_process.wait()
                    main_process = start_main_stream()
                    is_offline = False

            time.sleep(3)

    except KeyboardInterrupt:
        print("Shutting down stream relay...")
        main_process.terminate()
        main_process.wait()
        if is_offline:
            offline_process.terminate()
            offline_process.wait()
