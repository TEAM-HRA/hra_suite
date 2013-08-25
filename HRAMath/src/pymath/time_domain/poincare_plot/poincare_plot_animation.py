'''
Created on Aug 18, 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import matplotlib.animation as animation
    from pycore.io_utils import as_path
    from pymath.time_domain.poincare_plot.poincare_plot_movie_worker \
                    import PoincarePlotMovieMakerWorker
except ImportError as error:
    print_import_error(__name__, error)

#convert from mp4 to avi
#mencoder  pp_movie_000000.mp4 -ovc lavc -lavcopts vcodec=mpeg4 -oac copy -o
#          pp_movie_000000.avi
#mencoder  pp_movie_000031.mp4 -ovc lavc -lavcopts vcodec=mpeg4 -oac copy -o
#          pp_movie_000031.avi
#mencoder  pp_movie_000061.mp4 -ovc lavc -lavcopts vcodec=mpeg4 -oac copy -o
#          pp_movie_000061.avi
#mencoder  pp_movie_000091.mp4 -ovc lavc -lavcopts vcodec=mpeg4 -oac copy -o
#          pp_movie_000091.avi
#join avi files
#cat file1.avi file2.avi file3.avi > video_draft.avi
#create one correct avi file
#mencoder video_draft.avi -o video_final.avi -forceidx -ovc copy -oac copy


class PoincarePlotAnimation(PoincarePlotMovieMakerWorker):
    def __init__(self, pp_specs_manager):
        super(PoincarePlotAnimation, self).__init__(pp_specs_manager)
        interval = int(1000.0 / self.manager.movie_fps)
        ani = animation.FuncAnimation(self.fig,
                            self.update_plot,
                            init_func=self.setup_plot,
                            frames=len(self.pp_specs),
                            interval=interval,
                            blit=True,
                            repeat_delay=0,
                            repeat=False)

        p0 = self.pp_specs[0]  # alias
        output_movie_file = as_path(self.manager.movie_dir,
                        '%s_%06d.mp4' % (self.manager.movie_name, p0.idx))
        ani.save(output_movie_file, fps=self.manager.movie_fps,
                 dpi=self.manager.movie_dpi,
                 #extra_args=['-vcodec', 'libx264']
                 #extra_args=['-vcodec', 'mpeg4']
                 #extra_args=['-vcodec', 'h264']
                 #, '-lavcopts', 'vcodec=avi']
                 )
        #plt.show()

    def setup_plot(self):
        self.initiate()
        return self.scatter,

    def update_plot(self, idx):
        self.plot(idx)
        return self.scatter,
