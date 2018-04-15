# @package smoderp2d.src.main_classes.CumulativeMax
#
#  package contains classes save the cumulative or maximum
#  values of the results in each time step.
#
#


# globals import
import numpy as np


# smoderp import
from smoderp2d.src.main_classes.General import *
from smoderp2d.src.tools.tools import comp_type
import smoderp2d.src.io_functions.prt as prt


from smoderp2d.src.main_classes.General import Globals as Gl


# Max and cumulative values of the subsurface flow
#
#  Stores arrays of max or cumulative values of important variables of
#  the subsurface flow \n
#
#  The class is inhered by the class Cumulative
#  if the subsurface computation is desired
#
#
class CumulativeSubsurface(object):

    # constructor
    #

    def __init__(self):

        prt.message('\tSubsurface')
        super(CumulativeSubsurface, self).__init__()

        self.arrs[17] = 'exfiltration'
        self.arrs[18] = 'percolation'
        self.arrs[19] = 'h_sub'
        self.arrs[20] = 'q_sub'
        self.arrs[21] = 'V_sub'

        self.names[17] = 'CumExfiltrL3'
        self.names[18] = 'CumPercolL3'
        self.names[19] = 'MaxWaterSubL'
        self.names[20] = 'MaxQSubL3t_1'
        self.names[21] = 'CumVOutSubL3'

        r = self.r
        c = self.c

        self.n += 5

        # cumulative exfiltration volume [m3]
        self.exfiltration = np.zeros([r, c], float)
        # cumulative percolation volume [m3]
        self.percolation = np.zeros([r, c], float)
        # maximum water level in rills [m]
        #
        #  the height is related to the total cell area not the rill ares
        #
        self.h_sub = np.zeros([r, c], float)
        # maximum discharge from rills [m3s-1]
        self.q_sub = np.zeros([r, c], float)
        # cumulative outflow volume in rills [m3]
        self.V_sub = np.zeros([r, c], float)

    # Method is used after each time step to save the desired variables.
    #
    #  Method is called in smoderp2d.src.runoff
    #
    def update_cumulative_subsur(self, i, j, sub, q_subsur):

        self.exfiltration[i][j] += sub.exfiltration * self.pixel_area
        self.percolation[i][j] += sub.percolation * self.pixel_area
        self.V_sub[i][j] += sub.V_runoff

        if sub.h > self.h_sub[i][j]:
            self.h_sub[i][j] = sub.h
        if q_subsur > self.q_sub[i][j]:
            self.q_sub[i][j] = q_subsur


# Empty (pass) Class
#
# Class is inherited by the class Cumulative if the subsurface flow is not desired.
#
class CumulativeSubsurfacePass(object):

    # Method is used after each time step.
    #
    #  Method is called in smoderp2d.src.runoff
    #

    def update_cumulative_sur(self, i, j, sub, q_subsur):
        pass


# Max and Cumulative values
#
#  Stores array of max or cumulative values at of important variables from
#  the surface and rill flow
#
#
class Cumulative(CumulativeSubsurface if Gl.subflow else CumulativeSubsurfacePass, Globals, Size):

    # the constructor
    #
    #

    def __init__(self):

        prt.message('Save cumulative and maximum values from:')
        prt.message('\tSurface')

        # Dictionary stores the python arrays identification.
        #
        #  self.arr is used in the smoderp2d.src.io_functions.post_proc
        #
        self.arrs = {1: 'infiltration',
                     2: 'precipitation',
                     3: 'h_sur',
                     4: 'q_sur',
                     5: 'V_sur',
                     6: 'v_sur',
                     7: 'shear_sur',
                     8: 'h_rill',
                     9: 'q_rill',
                     10: 'V_rill',
                     11: 'b_rill',
                     12: 'inflow_sur',
                     13: 'sur_ret',
                     14: 'V_sur_r',
                     15: 'q_sur_tot',
                     16: 'V_sur_tot'
                     }

                # 12 : 'v_rill',

        # Dictionary stores the the arrays name used in the output rasters.
        #
        #  self.names is used in the smoderp2d.src.io_functions.post_proc
        #
        self.names = {1: 'cinfil_m',
                      2: 'crainf_m',
                      3: 'cVInM3',
                      4: 'MaxQL3t_1',
                      5: 'cSheetVOutM3',
                      6: 'mvel_m_s',
                      7: 'mshearstr_pa',
                      8: 'MaxWaterRillL',
                      9: 'MaxQRillL3t_1',
                      10: 'cRillVOutL3',
                      11: 'AreaRill',
                      12: 'CumVInL3',
                      13: 'SurRet',
                      14: 'CumVRestL3',
                      15: 'msurfl_m3_s',
                      16: 'csurvout_m3_s'
                      }
                # 12 : 'MaxVeloRill',

        if (Globals.r is None or Globals.r is None):
            sys.exit("Global variables are not assigned")

        r = self.r
        c = self.c

        # array count stored in the class
        self.n = 13
        # cumulative infiltrated volume [m3]
        self.infiltration = np.zeros([r, c], float)
        # cumulative precipitation volume [m3]
        self.precipitation = np.zeros([r, c], float)
        # maximum surface water level [m]
        self.h_sur = np.zeros([r, c], float)
        # maximum surface discharge [m3s-1]
        self.q_sur = np.zeros([r, c], float)
        # cumulative surface runoff volume [m3]
        self.V_sur = np.zeros([r, c], float)
        # cumulative surface runoff volume [m3]
        self.V_sur_r = np.zeros([r, c], float)
        # maximum surface velocity [ms-1]
        self.v_sur = np.zeros([r, c], float)
        # maximum surface shear stress [Pa]
        self.shear_sur = np.zeros([r, c], float)
        # cumulative surface inflow volume [m3]
        self.inflow_sur = np.zeros([r, c], float)
        # maximum water level in rills [m]
        self.h_rill = np.zeros([r, c], float)
        # maximum discharge in rills [m3s-1]
        self.q_rill = np.zeros([r, c], float)
        # cumulative runoff volume in rills [m3]
        self.V_rill = np.zeros([r, c], float)
        # cumulative runoff volume in rills [m3]
        self.V_rill_r = np.zeros([r, c], float)
        # maximum rill width [m]
        self.b_rill = np.zeros([r, c], float)
        # maximum velocity in rills [ms-1]
        self.v_rill = np.zeros([r, c], float)
        # maximum surface retention [m]
        self.sur_ret = np.zeros([r, c], float)
        # maximal total surface flow [m3/s]
        self.q_sur_tot = np.zeros([r, c], float)
        # cumulative total surface flow [m3/s]
        self.V_sur_tot = np.zeros([r, c], float)

        super(Cumulative, self).__init__()

    # Method is used after each time step to save the desired variables.
    #
    #  Method is called in smoderp2d.src.runoff
    #
    def update_cumulative(self, i, j, surface, subsurface, delta_t):

        sur_arr = surface.arr[i][j]
        self.infiltration[i][j] += sur_arr.infiltration * self.pixel_area
        self.precipitation[i][j] += sur_arr.cur_rain * self.pixel_area
        self.V_sur[i][j] += sur_arr.V_runoff
        self.V_sur_r[i][j] += sur_arr.V_rest
        self.V_sur_tot[i][j] += sur_arr.V_rest + sur_arr.V_runoff
        self.inflow_sur[i][j] += surface.inflow_curr
        self.sur_ret[i][j] += sur_arr.cur_sur_ret * self.pixel_area

        q_sheet = sur_arr.V_runoff / delta_t
        q_rill = sur_arr.V_runoff_rill / delta_t
        q_tot = q_sheet + q_rill
        if q_tot > self.q_sur_tot[i][j]:
            self.q_sur_tot[i][j] = q_tot

        if sur_arr.state == 0:
            if sur_arr.h_total_new > self.h_sur[i][j]:
                self.h_sur[i][j] = sur_arr.h_total_new
                self.q_sur[i][j] = q_sheet

        elif (sur_arr.state == 1) or (sur_arr.state == 2):
            self.V_rill[i][j] += sur_arr.V_runoff_rill
            self.V_rill_r[i][j] += sur_arr.V_rill_rest
            if sur_arr.h_total_new > self.h_sur[i][j]:
                self.h_sur[i][j] = sur_arr.h_total_new
                self.q_sur[i][j] = q_sheet

            elif sur_arr.h_rill > self.h_rill[i][j]:
                self.h_rill[i][j] = sur_arr.h_rill
                self.b_rill[i][j] = sur_arr.rillWidth
                self.q_rill[i][j] = q_rill

        self.update_cumulative_sur(
            i,
            j,
            subsurface.arr[i][j],
            subsurface.q_subsurface)
