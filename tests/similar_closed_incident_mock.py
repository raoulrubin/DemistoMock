from DemistoMock import DemistoMock

class SampleMock(DemistoMock):
    def __init__(self) -> None:
        super().__init__()
        self.init()

    def load(self):
        testdata = { 'emailbody': 'Now is the time for all good men to come to the aid of the country',
                     'emailsubject': 'Test Subject'}
        self.internalIncident.load(0, testdata)

    def init(self):
        self.load()
        self.internalArgs.set("maxResults", 1)
        self.internalArgs.set("timeField", "origination")
        self.internalArgs.set('threshold', 9.0)
        self.internalArgs.set('textFields', 'emailbody,emailsubject')
        self.internalArgs.set('minTextLength', 10)
        self.internalArgs.set('timeFrameHours', 1.0)
        self.internalArgs.set('preProcessText', True)
        self.internalArgs.set('maximumNumberOfIncidents', 100)