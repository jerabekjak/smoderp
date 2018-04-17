"""The computing area is determined  as well as the boundary cells.

Vypocet probiha v zadanem casovem kroku, pripade je cas kracen podle
"Couranotva kriteria":
 - vystupy jsou rozdelieny do \b zakladnich a \b doplnkovych, podle zvoleneh typu vypoctu
 - zakladni
 - maximalni vyska haladiny plosneho odtoku
"""

import time
import os

from smoderp2d.main_classes.General import Globals as Gl
from smoderp2d.main_classes.Vegetation import Vegetation
from smoderp2d.main_classes.Surface import Surface

from smoderp2d.main_classes.Subsurface import Subsurface
from smoderp2d.main_classes.CumulativeMax import Cumulative
from smoderp2d.time_step import TimeStep

from smoderp2d.courant import Courant
from smoderp2d.io_functions import post_proc
from smoderp2d.io_functions import prt
from smoderp2d.io_functions import progress_bar
from smoderp2d.tools.times_prt import TimesPrt
from smoderp2d.io_functions import hydrographs as wf

from smoderp2d.exceptions import MaxIterationExceeded

class FlowControl():
    """FlowControl manage variables contains variables related to main
    computational loop."""
    def __init__(self):
        # type of infiltration
        #  - 0 for philip infiltration is the only
        #    one in current version
        self.infiltrationType = 0

        # actual time in calculation
        self.total_time = 0.0

        # keep order of a curent rainfall interval
        self.tz = 0

        # stores cumulative interception
        self.sum_interception = 0

        # factor deviding the time step for rill calculation
        # currently inactive
        self.ratio = 1

        # naximum amount of iterations
        self.maxIter = 40

        # current number of wihtin time step iterations
        self.iter_ = 0

    def save_vars(self):
        """Store tz and sum of interception
        in case of repeating time time stem iteration.
        """
        self.tz_tmp = self.tz
        self.sum_interception_tmp = self.sum_interception

    def restore_vars(self):
        """Restore tz and sum of interception
        in case of repeating time time stem iteration.
        """
        self.tz = self.tz_tmp
        self.sum_interception = self.sum_interception_tmp

    def refresh_iter(self):
        """Set current number of iteration to
        zero at the begining of each time step.
        """
        self.iter_ = 0

    def upload_iter(self):
        """Rises iteration count by one
        in case of iteration within a timestep calculation.
        """
        self.iter_ += 1

    def max_iter_reached(self):
        """Check if iteration exceed a maximum allowed amount.
        """
        return self.iter_ < self.maxIter

    def save_ratio(self):
        """Saves ration in case of interation within time step.
        """
        self.ratio_tmp = self.ratio

    def compare_ratio(self):
        """Check for changing ratio after rill courant criterion check.
        """
        return self.ratio_tmp == self.ratio

    def update_total_time(self, dt):
        """Rises time after successfully calculated previous time step.
        """
        self.total_time += dt

    def compare_time(self, end_time):
        """Checkes if end time is reached.
        """
        return self.total_time < end_time

class Runoff():
    """Performs the calculation.
    """
    def __init__(self, provider):
        """Initialize main classes.

        Method defines instances of classes for rainfall, surface,
        stream and subsurface processes handling.
        """
        self.provider = provider
        
        # handling print of the solution in given times
        self.times_prt = TimesPrt()

        # flow control
        self.flowControl = FlowControl()

        # handling the actual rainfall amount
        self.rain_arr = Vegetation()

        # handling the surface processes
        self.surface = Surface()

        # class handling the subsurface processes if desir
        # TODO: include in data preprocessing
        if Gl.subflow:
            self.subsurface = Subsurface(
                L_sub=0.1,
                Ks=0.005,
                vg_n=1.5,
                vg_l=0.5
            )
        else:
            self.subsurface = Subsurface()

        # maximal and cumulative values of resulting variables
        self.cumulative = Cumulative()

        # handle times step changes based on Courant condition
        self.courant = Courant()
        self.delta_t = self.courant.initial_time_step(self.surface)
        self.courant.set_time_step(self.delta_t)
        provider.message('Corrected time step is {} [s]'.format(self.delta_t))

        # opens files for storing hydrographs
        if Gl.points and Gl.points != "#":
            self.hydrographs = wf.Hydrographs()
            arcgis = Gl.arcgis
            if not arcgis:
                with open(os.path.join(Gl.outdir, 'points.txt'), 'w') as fd:
                    for i in range(len(Gl.array_points)):
                        fd.write('{} {} {} {}'.format(
                            Gl.array_points[i][0], Gl.array_points[i][3],
                            Gl.array_points[i][4], os.linesep
                        ))
        else:
            self.hydrographs = wf.HydrographsPass()

        # method for single time step calculation
        self.time_step = TimeStep()

        # record values into hydrographs at time zero
        for i in Gl.rr:
            for j in Gl.rc[i]:
                self.hydrographs.write_hydrographs_record(
                    i,
                    j,
                    self.flowControl,
                    self.courant,
                    self.delta_t,
                    self.surface,
                    self.subsurface,
                    0.0
                )
        # record values into stream hydrographs at time zero
        self.hydrographs.write_hydrographs_record(
            i,
            j,
            self.flowControl,
            self.courant,
            self.delta_t,
            self.surface,
            self.subsurface,
            0.0,
            True
        )

        self.provider.message('-' * 80)

    def run(self):
        # saves time before the main loop
        start = time.time()
        self.provider.message('Start of computing...')

        # main loop: until the end time
        i = j = 0
        while self.flowControl.compare_time(Gl.end_time):

            self.flowControl.save_vars()
            self.flowControl.refresh_iter()

            # iteration loop
            while self.flowControl.max_iter_reached():

                self.flowControl.upload_iter()
                self.flowControl.restore_vars()

                # reset of the courant condition
                self.courant.reset()
                self.flowControl.save_ratio()

                # time step size
                potRain = self.time_step.do_flow(
                    self.surface,
                    self.subsurface,
                    self.delta_t,
                    self.flowControl,
                    self.courant
                )

                # stores current time step
                delta_t_tmp = self.delta_t

                # update time step size if necessary (based on the courant
                # condition)
                self.delta_t, self.flowControl.ratio = self.courant.courant(
                    potRain, self.delta_t, Gl.spix, self.flowControl.ratio
                )

                # courant conditions is satisfied (time step did
                # change) the iteration loop breaks
                if delta_t_tmp == self.delta_t and self.flowControl.compare_ratio():
                    break

            # Calculate actual rainfall and adds up interception todo:
            # AP - actual is not storred in hydrographs
            actRain = self.time_step.do_next_h(
                self.surface,
                self.subsurface,
                self.rain_arr,
                self.cumulative,
                self.hydrographs,
                self.flowControl,
                self.courant,
                potRain,
                self.delta_t
            )

            # if the iteration exceed the maximal amount of iteration
            # last results are stored in hydrographs
            # and error is raised
            if not self.flowControl.max_iter_reached():
                for i in Gl.rr:
                    for j in Gl.rc[i]:
                        self.hydrographs.write_hydrographs_record(
                            i,
                            j,
                            self.flowControl,
                            self.courant,
                            self.delta_t,
                            self.surface,
                            self.subsurface,
                            self.curr_rain
                        )
                post_proc.do(self.cumulative, Gl.mat_slope, Gl, surface.arr)
                raise MaxIterationExceeded(maxIter, total_time)

            # adjusts the last time step size
            if (Gl.end_time - self.flowControl.total_time) < self.delta_t and \
               (Gl.end_time - self.flowControl.total_time) > 0:
                self.delta_t = Gl.end_time - self.flowControl.total_time

            # proceed to next time
            self.flowControl.update_total_time(self.delta_t)

            # if end time reached the main loop breaks
            if self.flowControl.total_time == Gl.end_time:
                break

            timeperc = 100 * (self.flowControl.total_time + self.delta_t) / Gl.end_time
            progress_bar.pb.update(
                timeperc,
                self.delta_t,
                self.flowControl.iter_,
                self.flowControl.total_time +
                self.delta_t
            )

            # calculate outflow from each reach of the stream network
            self.surface.stream_reach_outflow(self.delta_t)
            # calculate inflow to reaches
            self.surface.stream_reach_inflow()
            # record cumulative and maximal results of a reach
            self.surface.stream_cumulative(self.flowControl.total_time + self.delta_t)

            # set current times to previous time step
            self.subsurface.curr_to_pre()

            # write hydrographs of reaches
            self.hydrographs.write_hydrographs_record(
                i,
                j,
                self.flowControl,
                self.courant,
                self.delta_t,
                self.surface,
                self.subsurface,
                actRain,
                True
            )

            # print raster results in given time steps
            self.times_prt.prt(self.flowControl.total_time, self.delta_t, self.surface)

            # set current time results to previous time step
            # check if rill flow occur
            for i in Gl.rr:
                for j in Gl.rc[i]:
                    if self.surface.arr[i][j].state == 0:
                        if self.surface.arr[i][j].h_total_new > self.surface.arr[i][j].h_crit:
                            self.surface.arr[i][j].state = 1

                    if self.surface.arr[i][j].state == 1:
                        if self.surface.arr[i][j].h_total_new < self.surface.arr[i][j].h_total_pre:
                            self.surface.arr[i][j].h_last_state1 = self.surface.arr[i][j].h_total_pre
                            self.surface.arr[i][j].state = 2

                    if self.surface.arr[i][j].state == 2:
                        if self.surface.arr[i][j].h_total_new > self.surface.arr[i][j].h_last_state1: # state1 ?
                            self.surface.arr[i][j].state = 1

                    self.surface.arr[i][j].h_total_pre = self.surface.arr[i][j].h_total_new

        self.provider.message('Saving data...')

        self.provider.message('')
        self.provider.message('-' * 80)
        self.provider.message('Total computing time: {}'.format(time.time() - start))

        post_proc.do(self.cumulative, Gl.mat_slope, Gl, self.surface.arr)

        post_proc.stream_table(Gl.outdir + os.sep, self.surface, Gl.tokyLoc)

        self.hydrographs.closeHydrographs()
        self.provider.message("")

        # TODO: print stats in better way
        import platform
        if platform.system() == "Linux":
            pid = os.getpid()
            prt.message("/proc/" + str(pid) + "/status", 'reading')
            with open("/proc/" + str(pid) + "/status", 'r') as fp:
                for i, line in enumerate(fp):
                    if i >= 11 and i <= 23:
                        prt.message(line.replace("\n", ""))