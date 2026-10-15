import pycer

class PyOfflineServer():
    def __init__(self):
        self.pycer_server = pycer.PyOfflineServer()
        self.filters = {}

    def declare_stream(self, declaration):
        self.declaration_string = declaration
        return

    def add_filter(self, event_name, att_name, ret_type, fun):
        event_index = self.declaration_string.find(f'EVENT {event_name}')
        atts_end = self.declaration_string.find('}', event_index)
        self.declaration_string = self.declaration_string[:atts_end - 1] + f', {att_name}: {ret_type} ' + self.declaration_string[atts_end - 1:]
        if event_name in self.filters:
            self.filters[event_name].append(fun)
        else:
            self.filters[event_name] = [ fun ]

    def activate_stream(self):
        self.pycer_server.declare_stream(self.declaration_string)

    def add_query(self, query):
        self.pycer_server.add_query(query)

    att_conversion = {
            "int"       :   pycer.PyIntValue,
            "boolean"   :   pycer.PyBoolValue,
            "string"    :   pycer.PyStringValue,
            "double"    :   pycer.PyDoubleValue
            }

    def send_events(self, events):
        processed_events = []
        for e in events:
            event_index = self.declaration_string.index(f'EVENT {e[0]}')
            event_num = self.declaration_string.count('EVENT', 0, event_index)
            for f in self.filters[e[0]]:
                e[1].append(f(e[1]))
            processed_atts = []
            att_index_end = event_index
            for a in e[1]:
                att_index_start = self.declaration_string.index(
                        ': ',
                        att_index_end
                        )
                att_index_start = att_index_start + 2
                att_index_end = self.declaration_string.index(
                        ' ',
                        att_index_start
                        )
                if self.declaration_string[att_index_end - 1] == ',':
                    att_index_end = att_index_end - 1
                processed_atts.append(
                        self.att_conversion[self.declaration_string[ att_index_start:att_index_end].lower()]( a )
                        )
            processed_events.append(pycer.PyEvent(
                event_num,
                processed_atts
                ))
        self.pycer_server.send_events(processed_events)

    def get_output(self):
        return self.pycer_server.get_output()
