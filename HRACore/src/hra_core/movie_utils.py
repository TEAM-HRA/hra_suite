'''
Created on Sep 14, 2013

@author: jurek
'''
import os
import multiprocessing
import collections
from sys import platform as _platform
from hra_core.system_utils import execute_command
from hra_core.system_utils import run_command
from hra_core.io_utils import as_path
from hra_core.misc import is_empty


MovieSpecification = collections.namedtuple('MovieSpecification',
    ["name", "directory", "width", "height", "fps", "frames_file",
     "idx", "movie_frames"])


def __generate_movie__(movie_specification):
    """
    function generate a movie using mencoder based on frame's files extension
    or a file listing
    """
    m = movie_specification
    if m.idx == None:
        output_file = as_path(m.directory, '%s.avi' % (m.name))
    else:
        output_file = as_path(m.directory,
                              '%s_part_%02i.avi' % (m.name, m.idx))

    #frames_file if not null contains frames listing
    frames_source = 'mf://' + (('@' + m.frames_file)
            if m.frames_file else as_path(m.movie_directory, m.movie_frames))
    command = ('mencoder',
               frames_source,
               #'mf://@' + m.frames_file,
               '-mf',
               #'type=png:w=1024:h=800:fps=30',
               'type=png:w=' + str(m.width) + \
                    ':h=' + str(m.height) + \
                    ':fps=' + str(m.fps),
               '-ovc',
               'lavc',
               '-lavcopts',
               'vcodec=mpeg4:mbd=2:trell',
               '-oac',
               'copy',
               '-o',
               '%s' % (output_file))
    os.spawnvp(os.P_WAIT, 'mencoder', command)
    return output_file


def generate_movie(movie_name, movie_dir,
                   movie_width, movie_height,
                   movie_fps, movie_frames='*.png'):
    """
    function used by client code to generate a movie according to
    specified parameters; at this time multiprocessing
    version is used only for Linux OS
    """
    if _platform.find("linux") >= 0:
        return generate_multiprocessing_movie(movie_name, movie_dir,
                                              movie_width, movie_height,
                                              movie_fps, movie_frames)
    elif _platform == "darwin":
        # OS X
        raise Exception('Not implemented yet !')
    else:
        # windows family
        movie_specification = MovieSpecification(movie_name, movie_dir,
                            movie_width, movie_height, movie_fps, None,
                            None, movie_frames)
        return __generate_movie__(movie_specification)


def generate_multiprocessing_movie(movie_name, movie_dir,
                                   movie_width, movie_height,
                                   movie_fps, movie_frames='*.png'):
    """
    generating a movie with given specification using multiprocessing;
    all frames are divided into excluded sets of files, for each set
    a movie is create, in the next step all parts are joined to create
    one final movie
    """

    #delete previous partial listing files
    command = 'rm %s' % as_path(movie_dir, '%s_lst_*' % (movie_name))
    execute_command(command)

    #create listing of all files
    listing_file = str(as_path(movie_dir, movie_name + ".lst"))
    command = 'ls %s > %s' % (as_path(movie_dir, movie_frames), listing_file)
    execute_command(command)

    #get number of movie frames
    command = 'wc -l %s' % listing_file
    count = int(execute_command(command, 1).split()[0])

    #get bytes per line
    command = 'head %s' % listing_file
    bytes_per_line = int(len(execute_command(command, 1)))

    #divide number of files frames per processors count
    size = count / multiprocessing.cpu_count()

    #split listing file into equal parts prefixed <movie_name>_lst_
    command = '(cd %s; split -C %i %s %s_lst_)' % \
                (movie_dir, bytes_per_line * size, listing_file, movie_name)
    execute_command(command)

    #delete all previous movie parts
    command = 'rm %s' % as_path(movie_dir, '%s_part_*.avi' % (movie_name))
    execute_command(command)

    movie_specifications = []
    #iterate over splits to create movie_specifications objects
    command = 'ls ' + as_path(movie_dir, '%s_lst_*' % (movie_name))
    for idx, frames_file in enumerate(run_command(command)):
        frames_file = frames_file.replace('\n', '')
        movie_specification = MovieSpecification(movie_name, movie_dir,
                            movie_width, movie_height, movie_fps, frames_file,
                            idx, movie_frames)
        movie_specifications.append(movie_specification)

    #run generation of partial movies
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    #if not self.params.info_message_handler == None:
    #    self.params.info_message_handler('Generating frames'
    #                                 + (' ' * 20))
    pool.map(__generate_movie__, movie_specifications)
    pool.close()

    #join all video part movies
    movie_draft = movie_name + '_draft.avi'
    command = '(cd %s; cat %s_part_*.avi  > %s)' % (
                                    movie_dir, movie_name, movie_draft)
    execute_command(command)

    #convert draft file into final movie file
    output_file = '%s.avi' % (movie_name)
    command = '(cd %s; mencoder %s -o %s -forceidx -ovc copy -oac copy)' \
                 % (movie_dir, movie_draft, output_file)
    execute_command(command)

    #delete draft movie
    command = 'rm %s' % as_path(movie_dir, movie_draft)
    execute_command(command)

    #delete all movie parts
    command = 'rm %s' % as_path(movie_dir, '%s_part_*.avi' % (movie_name))
    execute_command(command)

    #delete all listing files
    command = 'rm %s' % as_path(movie_dir, '%s_lst_*' % (movie_name))
    execute_command(command)

    command = 'rm %s' % as_path(movie_dir, '%s.lst' % (movie_name))
    execute_command(command)

    return output_file

#mencoder mf://@list.txt -mf w=550:h=550:fps=700:type=png -ovc lavc -lavcopts
#vcodec=mpeg4:mbd=2:trell -oac copy -o output.avi

if __name__ == '__main__':
    generate_movie("pp_movie", "/tmp", 500, 500, 700)
