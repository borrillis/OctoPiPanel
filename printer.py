from collections import deque


class Printer:

    def __init__(self):
        self.HotEndTemp = 0.0
        self.BedTemp = 0.0
        self.HotEndTempTarget = 0.0
        self.BedTempTarget = 0.0
        self.HotHotEnd = False
        self.HotBed = False
        self.Paused = False
        self.Printing = False
        self.JobLoaded = False
        self.Completion = 0  # In percent
        self.PrintTimeLeft = 0
        self.Height = 0.0
        self.FileName = "Nothing"

        # Lists for temperature data
        self.HotEndTempList = deque([0] * 285)
        self.BedTempList = deque([0] * 285)