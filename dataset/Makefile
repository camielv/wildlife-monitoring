all: videos/GOPR0809_start_0_27_end_1_55.mp4 original_videos/GOPR0809.MP4

videos/GOPR0809_start_0_27_end_1_55.mp4: videos.tar.gz
    mkdir videos
    tar -zxvf videos.tar.gz -C videos
    touch videos/GOPR0809_start_0_27_end_1_55.mp4

original_videos/GOPR0809.MP4: original_videos.tar.gz
    mkdir original_videos
    tar -zxvf original_videos.tar.gz -C original_videos
    touch original_videos/GOPR0809.MP4

videos.tar.gz:
    wget -c https://googledrive.com/host/0B-1XujYg7VVXM3hJWjJhSFBkTHM --no-check-certificate -O videos.tar.gz

original_videos.tar.gz:
    wget -c https://googledrive.com/host/0B-1XujYg7VVXM3hJWjJhSFBkTHM --no-check-certificate -O original_videos.tar.gz

clean:
    rm videos.tar.gz original_videos.tar.gz
    rm -rf original_videos
    rm -rf videos
