""" CommandResults class used to return data to war room """


class CommandResults:
    def __init__(self, content_format=None, entry_type=None, outputs_prefix=None, outputs_key_field=None, outputs=None, readable_output=None) -> None:
        self.outputs_prefix = outputs_prefix
        self.outputs_key_field = outputs_key_field
        self.outputs = outputs
        self.readable_output = readable_output
        self.content_format = content_format
        self.entry_type = entry_type
