FROM julianassmann/opencv-cuda:cuda-10.2-opencv-4.2

ENV TZ=Africa/Johannesburg

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


RUN apt-get update && apt-get install -y --no-install-recommends \
  python3-pip \
  gstreamer1.0-libav \
  gstreamer1.0-tools \
  libgstreamer-plugins-good1.0-0 \
  libgstreamer-plugins-good1.0-dev \
  gstreamer1.0-plugins-good \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN mkdir input
RUN mkdir output

RUN pip3 install --upgrade pip

RUN pip3 install setuptools \
         wheel \
         scikit-build

RUN pip3 install numpy      \
         imageio-ffmpeg     \
         watchdog

COPY . .

CMD [ "python3", "yolo_od.py"]