from typing import List
import sys

mock_results = None
mock_error = None


def __line__():
    return sys._getframe(1).f_lineno


def get_error():
    return mock_error


def is_error():
    return mock_error is not None


def register_module_line(name, operation, line):
    print(f'Automation:{name} Operation:{operation} Line:{line}')


def return_results(results):
    global mock_results
    mock_results = results
    print('Results:', results)


def return_error(err):
    global mock_error
    mock_error = err
    print(err)


class IncidentMock:
    def __init__(self) -> None:
        self.incident_data = []

    def load(self, id: int, custom_fields: object):
        self.incident_data.append({'id': id, 'CustomFields': custom_fields})

    def set(self, obj):
        custom = self.incident_data[0]['CustomFields']
        for prop_name in obj:
            custom[prop_name] = obj[prop_name]

    def get(self):
        return self.incident_data


class ArgsMock:
    def __init__(self) -> None:
        self.data = dict()

    def get(self, name: str, defval=None) -> any:
        if name in self.data:
            return self.data[name]
        return defval

    def set(self, name: str, value: any) -> None:
        self.data[name] = value

    def __getitem__(self, item: str):
        if item in self.data:
            return self.data[item]
        raise IndexError("property not in mock")



class CommandsMock:
    def __init__(self, incident: IncidentMock) -> None:
        self.commands: CommandsMock = {'setIncident': self.setIncident}
        self.incident: IncidentMock = incident

    def defaut(self, cmd, obj):
        print(cmd, obj)

    def setIncident(self, cmd: str, obj: object):
        self.incident.set(obj)

    def execute(self, cmd: str, obj: object):
        func = self.defaut if cmd not in self.commands else self.commands[cmd]
        func(cmd, obj)


class DemistoMock(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DemistoMock, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.internalIncident = IncidentMock()
        self.internalArgs = ArgsMock()
        self.internalCommands = CommandsMock(self.internalIncident)

    def incident(self):
        return self.incident_data[0]

    def fetch_results(self, data: any):
        print("Resuts", data)
        
    def results(self, data: any):
        print('results:', data)

    def args(self):
        return self.internalArgs

    def executeCommand(self, cmd: str, obj):
        self.internalCommands.execute(cmd, obj)

    def incidents(self):
        return self.internalIncident.get()
