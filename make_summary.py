import sys, os, cv2, shutil, uuid, numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from pathlib import Path
from feature_extractor.get_video_features import *


def run(percent, input, sampling_rate, skim_length, output):
    title = Path(input).name.split('.')[0]
    video = cv2.VideoCapture(input)
    fps = int(video.get(cv2.CAP_PROP_FPS))
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    skim_frames_length = fps * skim_length

    print("----------Video opened----------")

    i = 0
    frames = []
    while (video.isOpened()):
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

    base = os.path.dirname(os.path.realpath(__file__))
    frames = uuid.uuid4().hex
    while os.path.exists(os.path.join(base, output, frames)):
        frames = uuid.uuid4().hex

    extension = 'jpg'
    if os.path.exists(os.path.join(base, output)):
        shutil.rmtree(os.path.join(base, output))
    Path(os.path.join(base, output, frames)).mkdir(parents=True, exist_ok=True)

    frames_indices = []
    for centre in centres:
        for idx in range(max(int(centre * sampling_rate - skim_frames_length / 2), 0),
                         min(int(centre * sampling_rate + skim_frames_length / 2) + 1, frame_count)):
            frames_indices.append(idx)
    frames_indices = sorted(set(frames_indices))
    for frame in frames_indices:
        if frame >= 0 & frame <= frame_count:
            video.set(cv2.CAP_PROP_POS_FRAMES, frame)
            ret, image = video.read()
            cv2.imwrite(os.path.join(base, output, frames, str(frame) + '.' + extension), image)

    files = [(f, f[f.rfind("."):], f[:f.rfind(".")]) for f in os.listdir(os.path.join(base, output, frames)) if
             f.endswith(extension)]
    maxlen = len(max([f[2] for f in files], key=len))
    for item in files:
        zeros = maxlen - len(item[2])
        dir_from = os.path.join(base, output, frames, item[0])
        dir_to = os.path.join(base, output, frames, str(zeros * "0" + item[2]) + item[1])
        shutil.move(dir_from, dir_to)

    print("----------Frames saved: " + str(len(frames_indices)) + "----------")

    start = sorted([int(i.split('.')[0]) for i in os.listdir(os.path.join(base, output, frames))])[0]
    cmd = "ffmpeg -framerate " + str(fps) + " -start_number " + f'{start:04d}' + " -i \"" + os.path.join(base, output,
                                                                                                         frames,
                                                                                                         '%04d.jpg') + "\" \"" + os.path.join(
        base, output, title + '.gif') + "\""
    os.system(cmd)

    print("----------Video processed.----------")

    shutil.rmtree(os.path.join(base, output, frames))

    print("Output: " + os.path.join(base, output, title + '.gif'))


if __name__ == '__main__':
    skim_length = 1.8  # skim length per chosen frames in second (will be adjusted according to the fps of the video)
    video = sys.argv[1]  # location of the video
    sampling_rate = int(sys.argv[2])  # frame chosen every k frames
    percent = int(sys.argv[3])  # percentage of video for summary
    output = sys.argv[4]  # output dir

    run(percent, video, sampling_rate, skim_length, output)
