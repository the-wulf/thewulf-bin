import re
import glob
import os
import mimetypes
import subprocess


class Video(object):
    """
    """
    def __init__(self, filepath, name=None):
        self.filepath = filepath
        self.name = name

    @property
    def output_path(self):
        return os.path.join(os.path.splitext(self.filepath)[0], "output")

    @property
    def converted_path(self):
        return os.path.join(os.path.splitext(self.filepath)[0], "converted")

    @property
    def audio_path(self):
        return os.path.join(os.path.splitext(self.filepath)[0], "audio")

    def __repr__(self):
        return "<Video({0}-{1})>".format(self.name, self.get_size())

    __str__ = __repr__

    def get_size(self):
        return os.path.getsize(self.filepath)

    def _get_next_filename(self):
        next_name = 1
        try:
            next_name = len(os.listdir(self.output_path))
        except IOError:
            pass
        finally:
            yield str(next_name)
            next_name += 1

    def convert_to_mp4(self):
        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)
        file_num = self._get_next_filename()
        new_path = os.path.join(self.output_path, file_num + ".mp4")
        cmnd = \
            "ffmpeg -i {old} -vcodec libx264 -preset slow -profile main -crf"\
            " 20 -acodec libfaac -ab 128k {new}"
        cmnd = cmnd.format(old=self.filepath, new=new_path)
        subprocess.check_call(cmnd.split(" "))
        return Video(new_path, name=file_num)

    def cut(self, *timings):
        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)
        for timing in timings:
            file_num = self._get_next_filename()
            new_path = os.path.join(self.output_path, file_num + ".mp4")
            start, end = timing
            cmnd = "ffmpeg -i {old} -ss {start} -c copy -t {end} {new}"
            cmnd = cmnd.format(
                old=self.filepath, start=start, end=end, new=new_path)
            subprocess.check_call(cmnd.split(" "))
            yield Video(new_path, name=file_num)

    def extract_audio(self):
        return


class VideoDirectory(object):
    """
    """
    def __init__(self, directory_path):
        self.directory_path = directory_path

    def __repr__(self):
        return "<VideoDirectory({0})>".format(self.directory_path)

    __str__ = __repr__

    def _collect_videos(self):
        """
        """
        all_videos = filter(
            lambda filepath: 'video' in mimetypes.guess_type(filepath)[0],
            glob.iglob(self.directory_path + '*')
        )
        all_videos = list(all_videos)  # in case of py3
        all_videos.sort(key=lambda x: os.path.getmtime(x))
        all_videos = iter(all_videos)
        yield Video(next(all_videos))

    def join_videos(self, event_date):
        """
        """
        if not re.match(r"^20[0-9]{2}_[0-9]{2}_[0-9]{2}_$", event_date):
            raise ValueError("argument event_date must be in form: YYYY_MM_DD!")

        output_dir = os.path.path.join(self.directory_path, "/concat")
        os.makedir(output_dir)

        tmpfile = os.path.join(output_dir, "tmp.txt")
        outfile = os.path.join(output_dir, "{0}.mov".format(event_date))

        with open(tmpfile) as _tmpfile:
            for video in self._collect_videos():
                _, filename = video.filepath.rsplit("/", 1)
                _tmpfile.write("file {0}\n".format(filename))

        subprocess.check_call(
            ['ffmpeg', '-f', 'concat', '-i', tmpfile, '-c', 'copy', outfile])

        os.remove(tmpfile)
        return Video(outfile, name=event_date)
