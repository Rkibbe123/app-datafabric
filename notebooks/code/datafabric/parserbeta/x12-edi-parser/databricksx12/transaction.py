from databricksx12.edi import *
from databricksx12.format import *

# """
#  Base class for all transactions (ST/SE Segments) 

#   Building a Spark DataFrame using toJson()
#   - @param "funcs" define which functions to use to flatten a transaction. Default is to use all "fx_*" definitions 
#   - @self.fields is a key/value pair dict which stores the function name (minus fx_ prefix) and return value
#      - @self.fields converted to a pyspark DataFrame for analytics
    
# """
# class Transaction(EDI):

#     #
#     # @param segments is expected as an array of segments starting with ST, ending with SE
#     #
    # def __init__(self,segments, delim_cls = AnsiX12Delim, transaction_type=None):
    #     self.data = segments
    #     self.format_cls = delim_cls
    #     self.transaction_type = transaction_type

#     def __getstate__(self):
#         """
#         Return state values to be pickled.
#         Called by pickle.dumps() and cloudpickle.dumps()
#         """
#         return {
#             'data': self.data,
#             'format_cls': self.format_cls,
#             'transaction_type': self.transaction_type
#         }

#     def __setstate__(self, state):
#         """
#         Restore state from the unpickled state values.
#         Called by pickle.loads() and cloudpickle.loads()
#         """
#         self.data = state['data']
#         self.format_cls = state['format_cls']
#         self.transaction_type = state['transaction_type']

# ############################################
class Transaction(EDI):
    def __init__(self, segments, delim_cls=AnsiX12Delim, transaction_type=None):
        self.data = segments
        self.format_cls = delim_cls
        self.transaction_type = transaction_type

        # Initialize ST segment fields
        self.transaction_set_identifier_code = None
        self.transaction_set_control_number = None
        self.implementation_convention_reference = None

        # Parse ST segment if available
        self._parse_st_segment()

    def _parse_st_segment(self):
        for segment in self.data:
            if segment.segment_name() == "ST":
                self.transaction_set_identifier_code = segment.element(1)
                self.transaction_set_control_number = segment.element(2)
                self.implementation_convention_reference = segment.element(3)
                break

    def __getstate__(self):
        return {
            'data': self.data,
            'format_cls': self.format_cls,
            'transaction_type': self.transaction_type,
            'transaction_set_identifier_code': self.transaction_set_identifier_code,
            'transaction_set_control_number': self.transaction_set_control_number,
            'implementation_convention_reference': self.implementation_convention_reference
        }

    def __setstate__(self, state):
        self.data = state['data']
        self.format_cls = state['format_cls']
        self.transaction_type = state['transaction_type']
        self.transaction_set_identifier_code = state.get('transaction_set_identifier_code')
        self.transaction_set_control_number = state.get('transaction_set_control_number')
        self.implementation_convention_reference = state.get('implementation_convention_reference')
