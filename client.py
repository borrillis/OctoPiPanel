import json
from threading import Thread
import requests


class OctoPiClient:
    def __init__(self, server_url, api_key):
        self.api_key = api_key
        self.addkey = '?apikey={0}'.format(api_key)
        self.apiurl_printhead = '{0}/api/printer/printhead'.format(server_url)
        self.apiurl_tool = '{0}/api/printer/tool'.format(server_url)
        self.apiurl_bed = '{0}/api/printer/bed'.format(server_url)
        self.apiurl_job = '{0}/api/job'.format(server_url)
        self.apiurl_status = '{0}/api/printer?apikey={1}'.format(server_url, api_key)
        self.apiurl_connection = '{0}/api/connection'.format(server_url)
        self.apiurl_files = '{0}/api/files?apikey={1}'.format(server_url, api_key)
        self.thread = None

    def get_files ( self ):
        req = requests.get(self.apiurl_files, timeout=5)

        if req.status_code == 200:
            ret = json.loads(req.text)
            return ret ['files']
        else:
            return None

    def get_printer_status(self, printer):
        req = requests.get(self.apiurl_status)

        if req.status_code == 200:
            state = json.loads(req.text)

            # Set status flags
           
            if 'temps' in state:
                tempNode = state['temps']
            else:
                tempNode = state['temperature']

            printer.HotEndTemp = tempNode['tool0']['actual']
            printer.BedTemp = tempNode['bed']['actual']
            printer.HotEndTempTarget = tempNode['tool0']['target']
            printer.BedTempTarget = tempNode['bed']['target']

            if not printer.HotEndTempTarget:
                printer.HotEndTempTarget = 0.0

            if not printer.BedTempTarget:
                printer.BedTempTarget = 0.0

            if printer.HotEndTempTarget > 0.0:
                printer.HotHotEnd = True
            else:
                printer.HotHotEnd = False

            if printer.BedTempTarget > 0.0:
                printer.HotBed = True
            else:
                printer.HotBed = False

    def get_job_status(self, printer):
        req = requests.get(self.apiurl_job + self.addkey)

        if req.status_code == 200:
            jobState = json.loads(req.text)

            printer.Completion = jobState['progress']['completion'] or 0
            printer.PrintTimeLeft = jobState['progress']['printTimeLeft'] or 0
            printer.FileName = jobState['job']['file']['name'] or ""

    def get_connection_status(self, printer):
        req = requests.get(self.apiurl_connection + self.addkey)
        if req.status_code == 200:
            connState = json.loads(req.text)

            # Save temperatures to lists
            printer.HotEndTempList.popleft()
            printer.HotEndTempList.append(printer.HotEndTemp)
            printer.BedTempList.popleft()
            printer.BedTempList.append(printer.BedTemp)

            printer.Paused = connState['current']['state'] == "Paused"
            printer.Printing = connState['current']['state'] == "Printing"

    # Send API-data to OctoPrint
    def send_api_command(self, url, data):
        headers = {'content-type': 'application/json', 'X-Api-Key': self.api_key}

        # Only allow executing one action at a time. Should prevent printers running away with queued commands
        if self.thread and self.thread.isAlive():
            return

        self.thread = Thread(target=self.send_request, args=(url, data, headers))
        self.thread.start()

    def send_request(self, url, data, headers):
        requests.post(url, data=json.dumps(data), headers=headers, timeout=0.3)
        return

    def home_xy(self):
        data = {"command": "home", "axes": ["x", "y"]}

        # Send command
        self.send_api_command(self.apiurl_printhead, data)

        return

    def home_x(self):
        data = {"command": "home", "axes": ["x"]}

        # Send command
        self.send_api_command(self.apiurl_printhead, data)

        return

    def home_y(self):
        data = {"command": "home", "axes": ["y"]}

        # Send command
        self.send_api_command(self.apiurl_printhead, data)

        return

    def home_z(self):
        data = {"command": "home", "axes": ["z"]}

        # Send command
        self.send_api_command(self.apiurl_printhead, data)

        return

    def jog_axis(self, x=0, y=0, z=0):
        data = {"command": "jog", "x": x, "y": y, "z": z}

        # Send command
        self.send_api_command(self.apiurl_printhead, data)

        return

    def z_up(self):
        data = {"command": "jog", "x": 0, "y": 0, "z": 25}

        # Send command
        self.send_api_command(self.apiurl_printhead, data)

        return


    def heat_bed(self):
        # is the bed already hot, in that case turn it off
        if self.HotBed:
            data = {"command": "target", "target": 0}
        else:
            data = {"command": "target", "target": 50}

        # Send command
        self.send_api_command(self.apiurl_bed, data)

        return

    def heat_hotend(self):
        # is the bed already hot, in that case turn it off
        if self.HotHotEnd:
            data = {"command": "target", "targets": {"tool0": 0}}
        else:
            data = {"command": "target", "targets": {"tool0": 190}}

        # Send command
        self.send_api_command(self.apiurl_tool, data)

        return

    def start_print(self):
        # here we should display a yes/no box somehow
        data = {"command": "start"}

        # Send command
        self.send_api_command(self.apiurl_job, data)

        return

    def abort_print(self):
        # here we should display a yes/no box somehow
        data = {"command": "cancel"}

        # Send command
        self.send_api_command(self.apiurl_job, data)

        return

    # Pause or resume print
    def pause_print(self):
        data = {"command": "pause"}

        # Send command
        self.send_api_command(self.apiurl_job, data)

        return