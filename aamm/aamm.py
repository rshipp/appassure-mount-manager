import datetime
from collections import OrderedDict
from urllib import quote_plus
from bs4 import BeautifulSoup

from appassure.session import AppAssureSession, AppAssureError
from appassure.core.IAgentsManagement import IAgentsManagement
from appassure.core.IRecoveryPointsManagement import IRecoveryPointsManagement
from appassure.core.ILocalMountManagement import ILocalMountManagement
from appassure.unofficial.Events import Events

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

    #
    # Public methods.
    #

    def get_machines(self):
        try:
            with AppAssureSession(self.server, self.port, self.username,
                    self.password) as session:
                agents = IAgentsManagement(session).getAgents().agent

                machines = {}
                machines['data'] = []
                for agent in agents:
                    latest = agent.agentRecoveryPointsInfo.newestTimeStamp
                    if not latest.startswith('0001'):
                        machines['data'].append({
                            "name": agent.displayName,
                            "date": self._humanize_time(latest),
                            # See FIXME below in get_recovery_points()
                            "button": '', #self._get_button(False),
                            "link": '<a href="%s/%s">%s</a>' % (agent.id,
                                agent.displayName, agent.displayName),
                            "id": agent.id,
                            })
                return machines
        except AppAssureError:
            return dict()

    def get_recovery_points(self, machine):
        try:
            with AppAssureSession(self.server, self.port, self.username,
                    self.password) as session:
                summaries = IRecoveryPointsManagement(session).getAllRecoveryPoints(machine).recoveryPointSummary

                recovery_points = {}
                recovery_points['data'] = []
                for summary in summaries:
                    recovery_points['data'].append({
                        'id': summary.id,
                        'contents': ', '.join([ image.volumeDisplayName for image in
                            summary.volumeImages.volumeImageSummary
                        ]),
                        'date': self._humanize_time(summary.timeStamp),
                        'button': self._get_button(True if 'true' in [
                                # FIXME: The AppAssure API seems to report this
                                # incorrectly.
                                image.isMounted for image in summary.volumeImages.volumeImageSummary
                            ] else False, '/%s/%s/%s/%s' % (
                                machine,
                                summaries[0].agentHostName,
                                summary.id[37:],
                                ' '.join([ str(quote_plus(image.id))
                                    for image in summary.volumeImages.volumeImageSummary
                                ]).replace(machine, '')
                                )),
                        'mounted': False,
                    })
                return (summaries[0].agentHostName, recovery_points)
        except AppAssureError:
            return (str(), dict())

    def mount_recovery_point(self, recovery_point_id, agent_id,
            agent_name, volume_ids):
        """recovery_point_time should be in _humanize_time almost-ISO format."""
        timestamp = recovery_point_id[:-4]
        recovery_point_id = agent_id + '-' + recovery_point_id
        volume_ids = [ agent_id + vid for vid in volume_ids ]
        data = OrderedDict([
            ('agentIds', {
                'agentId': [ agent_id ],
            }),
            ('force', 'true'),
            ('isNightlyJob', 'false'),
            ('mountPoint', 'C:\ProgramData\AppRecovery\MountPoints\%s-%s' % (
                agent_name, timestamp)
            ),
            ('recoveryPoint', recovery_point_id),
            ('type', 'ReadOnly'),
            ('volumeImagesToMount', {
                'string xmlns="http://schemas.microsoft.com/2003/10/Serialization/Arrays"':
                    volume_ids,
            }),
        ])
        with AppAssureSession(self.server, self.port, self.username,
                self.password) as session:
            try:
                return ILocalMountManagement(session).startMount(data)
            except AppAssureError as e:
                return e[1].text

    def dismount_recovery_points(self, agent):
        with AppAssureSession(self.server, self.port, self.username,
                self.password) as session:
            try:
                return ILocalMountManagement(session).dismountAllAgent(agent)
            except AppAssureError as e:
                return e[1].text

    def get_progress(self, task_id):
        with AppAssureSession(self.server, self.port, self.username,
                self.password) as session:
            try:
                events = Events(session).taskMonitor(task_id).text
                percent = BeautifulSoup(events).td.td.text
                if not percent.endswith('%'):
                    return ''
                return percent
            except AppAssureError as e:
                return e[1].text
            except (ValueError, AttributeError) as e:
                return str(e)


    #
    # Private methods.
    #

    def _get_button(self, mounted, href=''):

        formatter = '<a href="%s" class="btn btn-xs btn-%s" data-toggle="modal" data-target="#mountModal">%s</a>'

        if mounted:
            button = formatter % (href, 'danger', 'Unmount')
        else:
            button = formatter % (href, 'primary', 'Mount')
        return button

    def _humanize_time(self, string):
        utc = datetime.datetime.strptime(string[:19],
                "%Y-%m-%dT%H:%M:%S")
        if self.subtract:
            time = utc - datetime.timedelta(0, self.tz_offset*60*60)
        else:
            time = utc + datetime.timedelta(0, self.tz_offset*60*60)
        # Sorts correctly:
        return time.isoformat().replace('T', ' ')

    def _any_true(self, list_):
        return True if 'true' in list_ else False
