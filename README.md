# DemistoMock

Mock object for testing PaloAlto XSOAR (demisto) automation code.

To build:

     pip install .

Create a mock object sample_mock.py:

    from DemistoMock import DemistoMock  
    class SampleMock(DemistoMock):
      def __init__(self) -> None:
          super().__init__()
          self.init()

      def init(self):
          self.internalIncident.load(0, {'name': 'test incident 0', 'emailto': 'test@test.com'})
          self.internalArgs.set("maxResults", 100)

Here is the consuming automation file automation.py:

    from sample_mock import SampleMock
    from DemistoMock import register_module_line, __line__, return_error, is_error, get_error
    from DemistoMock.markdown import formats, entryTypes, tableToMarkdown
    demisto = SampleMock()
    
    register_module_line('automation', 'start', __line__())
    
    incident = demisto.incidents()[0]
    maxresults = demisto.args()['maxResults']
    demisto.executeCommand('setIncident', {'max_results' : maxresults})
    ...
  
