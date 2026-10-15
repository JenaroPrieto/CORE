import pycer_filter

server = pycer_filter.PyOfflineServer()

declaration = """
CREATE STREAM ExampleStream {
    EVENT Ex { value: int }
}
"""

server.declare_stream(declaration)

def fiz(event):
    value = event[0]
    result = value % 3 == 0;
    return result

def buz(event):
    value = event[0]
    result = value % 5 == 0;
    return result

server.add_filter("Ex", "fiz", 'boolean', fiz)
server.add_filter("Ex", "buz", 'boolean', buz)

server.activate_stream()

query = """
SELECT * FROM ExampleStream
WHERE Ex AS foo; Ex AS bar; Ex AS foobar
FILTER foo[fiz = 1] AND bar[buz = 1] AND foobar[fiz = 1 AND buz = 1 ]
WITHIN 10 minutes
"""

server.add_query(query)

events = [
        [
            "Ex",
            [
                x
            ]
        ] for x in range(16)
        ]

server.send_events(events)
output = server.get_output()
print(output)
