#!/usr/bin/python
"""
`new uploading process'
    * chop locally - HD -
    * upload chopped HD to server
    * separate audio from video on server
    * covert to streaming format on server

the goal is to host both video and audio in the following formats:
    :uncompressed audo: .wav
    :compressed audio: .mp3, .ogg
    :compressed vide: .ogv, .mp4, .webm -> all with .mp3 audio
"""
import os
import sys
import re
import subprocess

OUTPUT_FORMAT = ".MOV"

def _sort_dir(directory, extension=""):
    """unfortunately directories are not inherently sorted in the way our Zoom
    camera saves consecutive videos. this function excludes files without an
    `extension` and sorts them such that ZOOM0001.MOV will preceed ZO010001.MOV
    """
    assert os.path.exists(directory), 'invalid directory <%s>.'\
        ' please sure to use absolute paths only.' % directory
    _files = [f for f in os.listdir(directory) if f.endswith(extension)]
    _files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)))
    return _files


def format_string(directory, sort_func=_sort_dir, file_extension=OUTPUT_FORMAT):
    """ffmpeg requires a temporary .txt file containing all of the filenames in
    the directory we would like to concatinate. the syntax for the file is,
        file <filename>!linebreak
        file <filename>!linebreak
        ...
    !! NOTICE , function returns both the formatted string for the temp txt file
    and the directory list.
    """
    _files = sort_func(directory, file_extension)
    _list = ""
    for _file in _files:
        _list += 'file ' + _file + '\n'
    assert _list is not '', 'directory %s does not contain any %s files.' % \
        (directory, file_extension)
    return _list, _files


def output_tmp_txt(filename, directory, formatter=format_string):
    """the main worker function for writing and outputting the temporary .txt
    file. the function returns the path to the file for cleanup later.
    """
    _filename = os.path.join(directory, filename)
    _formatted, _files = formatter(directory)
    with open(_filename, 'w') as _output:
        _output.write(_formatted)
    return _filename, _files


def concat_video(directory, event_date, file_extension=OUTPUT_FORMAT):
    """the main algorithm for running our the ffmpeg concat command. returns a
    filepath to the created file, temp txt file and the origional video files
    for cleanup.
    """
    _outfile = os.path.join(directory, event_date + file_extension)
    _tmpfile = output_tmp_txt('tmp.txt', directory)
    subprocess.check_call(['ffmpeg', '-f', 'concat', '-i', _tmpfile[0], '-c',
                           'copy', _outfile])
    return _outfile, _tmpfile, [os.path.join(directory, f) for f in _tmpfile[1]]


def main(directory, event_date, remote_dir='', concat_func=concat_video):
    sys.stdout.write("\n" + ("-"*20) + ("concatination of %s begun" % directory)
                     + ("-"*20) + "\n")
    video, tmpfile, pieces = concat_func(directory, event_date)

def run():
    import argparse
    parser = argparse.ArgumentParser(
        description='concatinate all video files in a directory.'
    )
    parser.add_argument(
        'local_dir',
        help='full filepath to directory containing videos'
    )
    parser.add_argument(
        'event_date',
        help='date of the event in format YYYY_MM_DD'
    )
    args = parser.parse_args()

    if not re.match(r'^\d{4}_\d{2}_\d{2}', args.event_date):
        raise AssertionError('invalide date format. please use YYYY_MM_DD.')

    main(args.local_dir, args.event_date)
