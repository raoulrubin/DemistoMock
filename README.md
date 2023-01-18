# DemistoMock

Mock object for testing demisto (XSOAR) automations. 

Create a mock object:
  from DemistoMock import DemistoMock
  
  # sample_mock.py
  class SampleMock(DemistoMock):
      def __init__(self) -> None:
          super().__init__()
          self.init()

      def init(self):
      self.internalIncident.load(0, {'name': 'test inncident 0', 'emailto': 'test@test.com'})
      self.internalArgs.set("maxResults", 100)

  # automation.py
  from sample_mock import SampleMock
  from DemistoMock import register_module_line, __line__, return_error, is_error, get_error
  from DemistoMock.markdown import formats, entryTypes, tableToMarkdown
  
  register_module_line('automation', 'start', __line__())
  
  demisto = SampleMock()
  
  incident = demisto.incidents()[0]
  
  maxresults = demisto.args()['maxResults']
  ...
  
