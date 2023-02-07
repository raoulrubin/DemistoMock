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


def createContext(ctx: any, removeNull=True):
    return {}


def return_outputs(md_, ec_, raw_response, ignore_auto_extract=True):
    return ""

def set_integration_context(data):
    pass

def date_to_timestamp(d, date_format='%Y-%m-%dT%H:%M:%S'):
    pass

def get_integration_context():
    return {}

def argToBoolean(a):
    return a != None

def UpdateRemoteSystemArgs(a):
    pass

def pascalToSpace():
    pass


def GetModifiedRemoteDataResponse(a):
    pass

def update_last_run_object(
        last_run=0,
        incidents=None,
        fetch_limit=0,
        start_fetch_time=False,
        end_fetch_time=False,
        look_back=False,
        created_time_field='occurred',
        id_field='name',
        date_format=""):
        pass

def LOG():
    pass

def camelize_string(additional_field) :
    pass

def dict_safe_get(data, nested_additional_field_list):
    pass