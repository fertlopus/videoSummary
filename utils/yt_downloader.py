from pytube import YouTube
import argparse


def download_video(url, save_to, custom_name="test.mp4"):
    yt = YouTube(url)
    yt.streams.filter(only_video=True, progressive=False, res="720p").first().download(output_path=save_to,
                                                                                       filename=custom_name)
    return None


def main():
    # Initialize parser for command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-yt_id", "--youtube_id", dest="youtube_id", type=str, help="YouTube id located in the url link,"
                                                                                   "e.g. youtube.com/watch?v=<__id__>")
    parser.add_argument("-o", "--output", dest="output", type=str, help="Saving directory, e.g. /data/videos/")
    parser.add_argument("-n", "--name", dest="name", type=str, required=False, help="Custom name of the file.",
                        default="test.mp4")
    args = parser.parse_args()

    # Command Line arguments
    yt_url, output_directory, filename = "https://www.youtube.com/watch?v=" + args.youtube_id, args.output, args.name
    try:
        download_video(url=yt_url, save_to=output_directory, custom_name=filename)
    except Exception as e:
        print("Error: ", e)
    return None


if __name__ == "__main__":
    main()

