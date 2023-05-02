import sys, os, cv2, numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from feature_extractor.get_video_features import *


def run(percent, input, sampling_rate, skim_length, output):
    video = cv2.VideoCapture(input)
    fps = int(video.get(cv2.CAP_PROP_FPS))
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    skim_frames_length = fps * skim_length

    print("----------Video opened----------")

    i = 0
    frames = []
    while video.isOpened():
        if i % sampling_rate == 0:
            video.set(1, i)
            ret, frame = video.read()
            if frame is None:
                break
            frames.append(np.asarray(frame))  # im = np.expand_dims(im, axis=0) #convert to (1, width, height, depth)
        i += 1
    frames = np.array(frames)  # convert to (num_frames, width, height, depth)

    features = get_color_hist(frames, 16)  # REPLACE WITH APPROPRIATE FEATURES
    num_centroids = int(percent * frame_count / skim_frames_length / 100) + 1

    print("Length of video: " + str(frames.shape[0]))
    print("Shape of features: " + str(features.shape))
    print("Number of clusters: " + str(num_centroids))

    centres = []
    kmeans = KMeans(n_clusters=num_centroids).fit(
        features)  # kmeans=GaussianMixture(n_components=num_centroids).fit(features)
    features_transform = kmeans.transform(features)
    for cluster in range(features_transform.shape[1]):
        centres.append(np.argmin(features_transform.T[cluster]))
    centres = sorted(centres)

    print("----------Centers: " + str(centres) + "----------")

    title = Path(input).stem
    for centre in centres:
        video.set(cv2.CAP_PROP_POS_FRAMES, centre * sampling_rate)
        ret, image = video.read()
        cv2.imwrite(os.path.join(output, title + '_' + str(centre * sampling_rate) + '.jpg'), image)

    print("----------Video processed.----------")
    print("Frames saved to: " + output)


if __name__ == '__main__':
    percent = 100  # percentage of video for summary
    input = sys.argv[1]  # location of the video
    sampling_rate = int(sys.argv[2])  # frame chosen every k frames
    skim_length = float(
        sys.argv[3])  # skim length per chosen frames in second (will be adjusted according to the fps of the video)
    output = sys.argv[4]  # output dir

    run(percent, input, sampling_rate, skim_length, output)
