import os
import re
import ftplib
import warnings
import argparse
from mimetypes import guess_type


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload a batch of videos to the wulf. server."
    )
    parser.add_argument(
        "server",
        help="the server to establish ftp connection with."
    )
    parser.add_argument(
        "username",
        help="the username@server to login with."
    )
    parser.add_argument(
        "password",
        help="the username@server password"
    )
    parser.add_argument(
        "-l", "--local_dir",
        required=True,
        help="full path to the directory containing files to upload."
    )
    parser.add_argument(
        "-d", "--event_date",
        required=True,
        help="the date of the event in the form YYYY_MM_DD."
    )
    parser.add_argument(
        "-t", "--file_type",
        default="video",
        choices=("video", "audio", "image"),
        help="the mimetype of the files to upload"
    )
    parser.add_argument(
        "-u", "--upload_dir",
        default="/thewulf.org/public/media/events",
        help="the remote directory (relative to the login users home directory) which event videos are uploaded"
    )
    args = parser.parse_args()

    if not re.match(r"^\d{4}_\d{2}_\d{2}$", args.event_date):
        raise ValueError("argument event_date must be in the form YYYY_MM_DD")
    if not os.path.exists(args.local_dir):
        raise ValueError("argument local_dir must refer to an existing directory")

    print("establishing a connection with {0}@{1}".format(args.username, args.server))
    with ftplib.FTP(args.server, args.username, args.password) as ftp:
        try:
            ftp.sendcmd("MLST {0}".format(args.upload_dir))
        except ftplib.error_perm as err:
            raise OSError("specified upload_dir {0} does not exist on {1}".format(args.upload_dir, args.server))

        # get the list of videos
        videos = [video for video in os.listdir(args.local_dir) if args.file_type in guess_type(video)[0]]
        num_videos = len(videos)

        true_dir = os.path.join(args.upload_dir, args.event_date, "{0}s".format(args.file_type))
        try:
            ftp.mkd(os.path.join(args.upload_dir, args.event_date))
            ftp.mkd(true_dir)
        # raised when folders already exist
        except ftp.error_perm as err:
            warnings.warn(err, Warning)
        else:
            print("succesfully created {0}".format(true_dir))
        finally:
            print("preparing to transfer {0} files from {1} to {2}".format(num_videos, args.local_dir, true_dir))
            ftp.cwd(true_dir)

        for i, video in enumerate(videos):
            print("transfering file {0} of {1}".format(i, num_videos))
            ftp.storbinary(
                "STOR {filename}".format(video),
                open(os.path.join(args.local_dir, video), "rb")
            )
