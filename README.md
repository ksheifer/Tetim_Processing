The Tetim_Processing project aims to collect speech data from the Sakha language radio station, Tetim. It operates at a frequency of 107.1 MHz in its broadcast area of Yakutsk. The channel is also available for online broadcasting [here](http://icecast-saha.cdnvideo.ru/saha).

Requirements
- **tenacity**: A Python library for retrying code execution upon failure. In this project, it is used to automatically retry the audio recording function up to 10 times if an error occurs, with a 10-second wait between attempts.
