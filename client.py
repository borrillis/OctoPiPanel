import requests


class OctoPiClient:

    def __init__(self, server_url, api_key):
        addkey = '?apikey={0}'.format(api_key)
        apiurl_printhead = '{0}/api/printer/printhead'.format(server_url)
        apiurl_tool = '{0}/api/printer/tool'.format(server_url)
        apiurl_bed = '{0}/api/printer/bed'.format(server_url)
        apiurl_job = '{0}/api/job'.format(server_url)
        apiurl_status = '{0}/api/printer?apikey={1}'.format(server_url, api_key)
        apiurl_connection = '{0}/api/connection'.format(server_url)

    def getprinterstatus(self):
        req = requests.get(self.apiurl_status)

    # Send API-data to OctoPrint
    def _sendAPICommand(self, url, data):
        headers = { 'content-type': 'application/json', 'X-Api-Key': self.apikey }
        r = requests.post(url, data=json.dumps(data), headers=headers)
        print r.text

    def _home_xy(self):
        data = { "command": "home", "axes": ["x", "y"] }

        # Send command
        self._sendAPICommand(self.apiurl_printhead, data)

        return

    def _home_z(self):
        data = { "command": "home", "axes": ["z"] }

        # Send command
        self._sendAPICommand(self.apiurl_printhead, data)

        return

    def _z_up(self):
        data = { "command": "jog", "x": 0, "y": 0, "z": 25 }

        # Send command
        self._sendAPICommand(self.apiurl_printhead, data)

        return


    def _heat_bed(self):
        # is the bed already hot, in that case turn it off
        if self.HotBed:
            data = { "command": "target", "target": 0 }
        else:
            data = { "command": "target", "target": 50 }

        # Send command
        self._sendAPICommand(self.apiurl_bed, data)

        return

    def _heat_hotend(self):
        # is the bed already hot, in that case turn it off
        if self.HotHotEnd:
            data = { "command": "target", "targets": { "tool0": 0   } }
        else:
            data = { "command": "target", "targets": { "tool0": 190 } }

        # Send command
        self._sendAPICommand(self.apiurl_tool, data)

        return

    def _start_print(self):
        # here we should display a yes/no box somehow
        data = { "command": "start" }

        # Send command
        self._sendAPICommand(self.apiurl_job, data)

        return

    def _abort_print(self):
        # here we should display a yes/no box somehow
        data = { "command": "cancel" }

        # Send command
        self._sendAPICommand(self.apiurl_job, data)

        return

    # Pause or resume print
    def _pause_print(self):
        data = { "command": "pause" }

        # Send command
        self._sendAPICommand(self.apiurl_job, data)

        return