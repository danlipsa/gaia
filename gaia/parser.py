import argparse
import json
from six import string_types
from gaia.processes import create_process
from gaia.inputs import *


class GaiaRequestParser(object):
    """
    Generate processes and inputs from a JSON object
    :return a GaiaProcess object
    """

    process = None
    data = None

    def __init__(self, process_name, data=None, parse=True, parent=None):
        """
        Create an instance of GaiaRequestParser
        """
        self.process = create_process(process_name, parent=parent)
        if data and parse:
            self.parse(data)

    def parse(self, data):
        """
        Generate process and input objects from JSON data
        """
        if isinstance(data, string_types):
            data = json.loads(data)
        process_inputs = data['data_inputs']
        self.process.args = data['args'] if 'args' in data else None
        self.process.inputs = []
        for input in process_inputs:
            io = create_io(self.process, input, process_inputs[input])
            self.process.inputs.append(io)
        return self.process


def is_vector(filename):
    try:
        return os.path.splitext(filename)[1] in formats.VECTOR
    except IndexError:
        return False


def create_io(process, name, data):
    if data['type'] == 'file':
        io = VectorFileIO(name, **data) if is_vector(
            data['uri']) else RasterFileIO(name, **data)
        return io
    elif data['type'] == 'process':
        process_name = data['process']['name']
        parser = GaiaRequestParser(process_name,
                                   data=data['process'], parent=process.id)
        return ProcessIO(name, process=parser.process)
    # elif data['type'] == 'girder':
    #     return GirderIO(**data)
    # elif data['type'] == 'wfs':

    #     return WfsIO(**data)
    # elif data['type'] == 'wfs':
    #     return WpsIO(**data)
    # elif data['type'] == 'raw':
    #     return GaiaIO(**data)
    # elif data['type'] == 'pg':
    #     return PostgisIO(**data)
    else:
        raise NotImplementedError()


def parse_request(process, request_json):
    """
    Parse a JSON request using GaiaRequestParser
    """
    parser = GaiaRequestParser(process, data=request_json, parse=True)
    parser.process.compute()
    return parser.process


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run geospatial process.')
    parser.add_argument('process')
    parser.add_argument('--jsonstr', default=None,
                        help='String representation of JSON request')
    parser.add_argument('--jsonfile', default=None,
                        help='sum the integers (default: find the max)')
    args = parser.parse_args()

    jsondata = None
    if args.jsonstr:
        jsondata = json.loads(args.jsonstr)
    elif args.jsonfile:
        with open(args.jsonfile) as infile:
            jsondata = json.load(infile)
    else:
        print "You must supply either a JSON string or file"
    if jsondata:
        process = parse_request(args.process, jsondata)
        print "Result saved to {}".format(process.output.uri)
