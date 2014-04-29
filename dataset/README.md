Verschoor Aerial Cow Dataset
============================


![Verschoor Aerial Cow Dataset](dataset.png "Verschoor Aerial Cow Dataset")

This folder contains the Verschoor Cow Aerial dataset. It entails:
- Makefile to download the videos.
- Frame by frame annotations for the videos in videos.
- The annotated videos.
- The original videos.


Usage
-----


1. Download the videos by executing the Makefile
2. Annotation files contain per column:
    1.  **Track ID:** All rows with the same ID belong to the same path.
    2.  **Xmin:** The top left x-coordinate of the bounding box.
    3.  **Ymin:** The top left y-coordinate of the bounding box.
    4.  **Xmax:** The bottom right x-coordinate of the bounding box.
    5.  **Ymax:** The bottom right y-coordinate of the bounding box.
    6.  **Frame:** The frame that this annotation represents.
    7.  **Lost** If 1, the annotation is outside of the view screen.
    8.  **Occluded** If 1, the annotation is occluded.
    9.  **Generated:** If 1, the annotation was automatically interpolated.
    10. **Label:** The label for this annotation, enclosed in quotation marks.


Creation
--------


- **Date:** August 28, 2013
- **Location:** Voorsterweg 31, 8316 PR Marknesse, The Netherlands
- **Pilot:** Christian Muller
- **Platform:** Ascending Technologies Pelican
- **Camera:** GoPro HERO 3: Black edition
- **Type:** Video
- **Quality:** 1080p
- **Field of view:** Medium (Vertical: 55° Horizontal: 94.4°)
- **Frames per second:** 60
- **Mount:** 3D printed made by Rob van Holstein.


Annotation
----------


- **Annotator:** Camiel R. Verschoor
- **Tool:** [Video Annotation Tool from Irvine, California](http://web.mit.edu/vondrick/vatic/). Vatic is a free, online, interactive video annotation tool for computer vision research that crowdsources work to Amazon's Mechanical Turk. The tool makes it easy to build massive, affordable video data sets and can be deployed on a cloud. After three years of research, vatic is now used by labs around the world to annotate the next generation of data sets. The tool contains:
    - A web interface.
    - Interfacing for Mechanical Turk.
    - Automatic interpolation between annotated frames.
    - Gold Standard Training for users for better results.
    - Outputs in various standards (ie. VOC PASCAL)


Videos
------
