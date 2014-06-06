import datetime
from appassure.session import AppAssureSession, AppAssureError
from appassure.core.IAgentsManagement import IAgentsManagement
from appassure.core.IRecoveryPointsManagement import IRecoveryPointsManagement


class Manager(object):
    def __init__(self, server, port, username, password, tz_offset):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        if tz_offset >= 0:
            self.tz_offset = int(tz_offset)
            self.subtract = False
        else:
            self.tz_offset = -int(tz_offset)
            self.subtract = True

    def get_machines(self):
        try:
            with AppAssureSession(self.server, self.port, self.username,
                    self.password) as session:
                agents = IAgentsManagement(session).getAgents().agent

                machines = {}
                for agent in agents:
                    latest = agent.agentRecoveryPointsInfo.newestTimeStamp
                    if not latest.startswith('0001'):
                        machines[agent.id] = {
                            'name': agent.displayName,
                            'latest': self._humanize_time(latest),
                            # See FIXME below in get_recovery_points()
                            'button': self._get_button(True),
                        }
                return machines
        except AppAssureError:
            return dict()

    def get_recovery_points(self, machine):
        try:
            with AppAssureSession(self.server, self.port, self.username,
                    self.password) as session:
                summaries = IRecoveryPointsManagement(session).getAllRecoveryPoints(machine).recoveryPointSummary

                recovery_points = {}
                for summary in summaries:
                    recovery_points[summary.id] = {
                        'contents': ', '.join([ image.volumeDisplayName for image in
                            summary.volumeImages.volumeImageSummary
                        ]),
                        'date': self._humanize_time(summary.timeStamp),
                        'button': self._get_button(True if 'true' in [
                            # FIXME: The AppAssure API seems to report this
                            # incorrectly.
                            image.isMounted for image in summary.volumeImages.volumeImageSummary
                        ] else False),
                    }
                return (summaries[0].agentHostName, recovery_points)
        except AppAssureError:
            return dict()


    def _get_button(self, mounted):

        class Button(object):
            # Allows Chameleon to print unescaped HTML.
            def __init__(self, button_type, text):
                self.button_type = button_type
                self.text = text

            def __html__(self):
                return '<a href="" class="btn btn-xs btn-%s">%s</a>' % (
                        self.button_type, self.text)

        if mounted:
            button = Button('danger', 'Unmount')
        else:
            button = Button('primary', 'Mount')
        return button

    def _humanize_time(self, string):
        utc = datetime.datetime.strptime(string[:19],
                "%Y-%m-%dT%H:%M:%S")
        if self.subtract:
            time = utc - datetime.timedelta(0, self.tz_offset*60*60)
        else:
            time = utc + datetime.timedelta(0, self.tz_offset*60*60)
        """More humanish:
        time = time.strftime("%I:%M:%S %p - %a, %b %d")
        # Strip off some extra 0's
        if time.startswith('0'):
            time = time[1:]
        if time[len(time)-2:-1] == '0':
            time = time[:len(time)-2] + time[-1:]
        return time
        """
        # Sorts correctly
        return time.isoformat().replace('T', ' ')

    def _any_true(self, list_):
        return True if 'true' in list_ else False
