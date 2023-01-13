import sys
import os

# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))

# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)

# adding the parent directory to
# the sys.path.
sys.path.append(parent)
from collections import defaultdict
import pandas as pd
import numpy as np

from logging import warning
from utilities import common

PJ2J = 1e12  # picojoule to joule
NJ2J = 1e9  # nanojoule to joule
BYTE_PER_FLIT = 16
BIT_PER_FLIT = 8 * BYTE_PER_FLIT


class PowerEstimator:
    def __init__(self):
        # Debug
        # Input parameters
        self.statsFilePath = "inputs/2021-08-30_summary.csv"
        self.eParaFilePath = "parameters/Xeon_Phi_4GHz.yaml"
        # Model configurations
        self.instructionsFilePath = "config/instructions.yaml"

        # Load input parameters and model configurations
        # Runtime statistics
        self.statsDf = pd.read_csv(self.statsFilePath, delimiter="\t")
        # Parameters of electronic devices
        self.eParameters = defaultdict(None,
                                       common.loadYaml(self.eParaFilePath))
        # Instructions on how to use interfere the statistics and parameters
        self.instructions = common.nestedDictIterator(
            common.loadYaml(self.instructionsFilePath))
        # Every instruction is decoded in the format of self.columns
        self.columnNames = [
            "ModuleName", "SubmoduleName", "Type", "Energy Consumption (J)"
        ]

        # Energy consumption statistics
        self.energyDf = pd.DataFrame()
        self.stats = None  # Global

    def run(self):
        for _, statsRow in self.statsDf.iterrows():
            # self.stats = statsRow.loc[statsRow.index.str.startswith(
            #     "key")].to_dict()
            self.stats = statsRow.to_dict()
            for instruction in self.instructions:
                newPowerRow = self.buildPowerRow(instruction)
                self.energyDf = pd.concat(
                    [self.energyDf, pd.Series(newPowerRow)],
                    axis=1,
                    ignore_index=True)
        return self.energyDf.T

    def buildPowerRow(self, instruction):
        result = {k: v for k, v in self.stats.items() if k.startswith("key")}
        keys, command = self.decode(instruction)
        value = self.numericalHandle(command)
        for columnName, columnContent in zip(self.columnNames, [*keys, value]):
            result[columnName] = columnContent
        return result

    def numericalHandle(self, command):
        result = np.nan
        try:
            result = eval(command)
        except Exception as e:
            warnMsg = f"Cannot eval the command {command}. "
            warning(warnMsg + str(e))
            result = np.nan
        if result <= 0 or np.isnan(result):
            warnMsg = f"Non-positive result generated from {command}"
            warning(warnMsg)
        return result

    def decode(self, instruction):
        keywords = instruction[:-1]
        pythonCommand = instruction[-1]
        return keywords, pythonCommand

# ------------------------------------------------------------------------------
#                                    Helpers
# ------------------------------------------------------------------------------
# =================================   Cache   ==================================
    def L1IRead(self):
        """L1 instruction cache read power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["L1I read"]                                             \
          * self.eParameters["L1I Cache"]["read power (nJ/op)"]                \
          / NJ2J
        # yapf: enable
        return result

    def L1IWrite(self):
        """L1 instruction cache write power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["L1I write"]                                            \
          * self.eParameters["L1I Cache"]["write power (nJ/op)"]               \
          / NJ2J
        # yapf: enable
        return result

    def L1IStatic(self):
        """L1 instruction cache static power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["L1 cache count"]                                       \
          * self.stats["exec time (ps)"]                                       \
          * self.eParameters["L1I Cache"]["static power (W)"]                  \
          / PJ2J
        # yapf: enable
        return result

    def L1DRead(self):
        """L1 data cache read power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["L1D read"]                                             \
            * self.eParameters["L1D Cache"]["read power (nJ/op)"]              \
            / NJ2J
        # yapf: enable
        return result

    def L1DWrite(self):
        """L1 data cache write power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["L1D write"]                                            \
          * self.eParameters["L1D Cache"]["write power (nJ/op)"]               \
          / NJ2J
        # yapf: enable
        return result

    def L1DStatic(self):
        """L1 data Cache static power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["L1 cache count"]                                       \
          * self.stats["exec time (ps)"]                                       \
          * self.eParameters["L1D Cache"]["static power (W)"]                  \
          / PJ2J
        # yapf: enable
        return result

    def L2Read(self):
        """L2Cache read power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["L2 read"]                                              \
          * self.eParameters["L2 Cache"]["read power (nJ/op)"]                 \
          / NJ2J
        # yapf: enable
        return result

    def L2Write(self):
        """L2Cache write power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["L2 write"]                                             \
          * self.eParameters["L2 Cache"]["write power (nJ/op)"]                \
          / NJ2J
        # yapf: enable
        return result

    def L2Static(self):
        """L2Cache static power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["L2 cache count"]                                       \
          * self.stats["exec time (ps)"]                                       \
          * self.eParameters["L2 Cache"]["static power (W)"]                   \
          / PJ2J
        # yapf: enable
        return result

    def L3Read(self):
        """L3Cache read power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["L3 read"]                                              \
          * self.eParameters["L3 Cache"]["read power (nJ/op)"]                 \
          / NJ2J
        # yapf: enable
        return result

    def L3Write(self):
        """L3Cache write power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["L3 write"]                                             \
          * self.eParameters["L3 Cache"]["write power (nJ/op)"]                \
          / NJ2J
        # yapf: enable
        return result

    def L3Static(self):
        """L3Cache static power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["L3 cache count"]                                       \
          * self.stats["exec time (ps)"]                                       \
          * self.eParameters["L3 Cache"]["static power (W)"]                   \
          / PJ2J
        # yapf: enable
        return result


# ==============================   Processor   =================================
    def procDynamic(self):
        """Processors' dynamic power consumption"""
        # yapf: disable
        result =                                                               \
            self.stats["busy time (ps*num_proc)"]                              \
          * self.eParameters["processor"]["dynamic power (W)"]                 \
          / PJ2J
        # yapf: enable
        return result

    def procStatic(self):
        """Processors' static power consumption"""
        # yapf: disable
        result =                                                               \
           (self.stats["waiting time (ps*num_proc)"]                           \
          + self.stats["busy time (ps*num_proc)"])                             \
          * self.eParameters["processor"]["static power (W)"]                  \
          / PJ2J
        # yapf: enable
        return result
# =========================   Electrical network   =============================

    def eLinkDynamic(self):
        """Electrical links' dynamic power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["bits through electrical link (bit*link)"]              \
          * self.eParameters["on-chip Elink"]["dynamic power (pJ/(bit*link))"] \
          / PJ2J
        # yapf: enable
        return result

    def eLinkStatic(self):
        """Electrical links' static power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["elink count"]                                          \
          * self.stats["exec time (ps)"]                                       \
          * self.eParameters["on-chip Elink"]["static power (W)"]              \
          / PJ2J
        # yapf: enable
        return result

    def eRouterDynamic(self):
        """Electrical routers' dynamic power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["bits through router (bit*router)"]                     \
          * self.eParameters["router"]["dynamic power (pJ/(bit*router))"]      \
          / PJ2J
        # yapf: enable
        return result

    def eRouterStatic(self):
        """Electrical routers' static power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["router count"]                                         \
          * self.stats["exec time (ps)"]                                       \
          * self.eParameters["router"]["static power (W)"]                     \
          / PJ2J
        # yapf: enable
        return result

    def bufferDynamic(self):
        """Buffers' dynamic power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["bits through buffer (bit*buffer)"]                     \
          * self.eParameters["buffer"]["dynamic power (pJ/(bit*buffer))"]      \
          / PJ2J
        # yapf: enable
        return result

    def bufferStatic(self):
        """Buffers' static power (Joule)"""
        # yapf: disable
        result =                                                               \
            self.stats["buffer count"]                                         \
          * self.stats["exec time (ps)"]                                       \
          * self.eParameters["buffer"]["static power (W)"]                     \
          / PJ2J
        # yapf: enable
        return result
