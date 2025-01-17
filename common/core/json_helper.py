import json
from typing import List


class JsonHelper:
    def __init__(self):
        super(JsonHelper, self).__init__()


    @classmethod
    def get_loaded_list(cls, str_val) -> List:
        str_val = str_val or "[]"
        lst = json.loads(str_val)
        return lst

    @classmethod
    def get_loaded_dict(cls, str):
        """
        :param str: json str
        :return: dict()
        """
        request_data = json.loads(str or '{}')
        return request_data
