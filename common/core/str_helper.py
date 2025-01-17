import logging
import math
import uuid
import re
import os

logger = logging.getLogger(__name__)


class StrHelper:
    def __init__(self):
        super(StrHelper, self).__init__()

    @classmethod
    def hide_mobile(cls, is_hide, mobile):
        if not mobile:
            return ''
        if is_hide == '1':
            mobile = '*******{}'.format(mobile[-4:])
        return mobile

    @classmethod
    def assert_is_numberic_str(cls, s):
        try:
            int(s)
        except BaseException as ve:
            logger.error('is_numberic_str s: {}, error: {}'.format(s, ve))
            raise AssertionError('考场号需要为数字.')

    @classmethod
    def set_zero_if_null(cls, s):
        if not s:
            return 0
        elif math.isnan(s):
            return 0
        else:
            return s

    @classmethod
    def is_numberic_str(cls, s):
        numberic = True
        try:
            int(s)
        except BaseException as ve:
            numberic = False
        return numberic

    @classmethod
    def is_float_str(cls, s):
        is_float = True
        try:
            float(s)
        except BaseException as ve:
            is_float = False
        return is_float

    @classmethod
    def is_positive_float_str(cls, s):
        try:
            result = float(s)
            if result > 0:
                return True
            else:
                return False
        except BaseException as ve:
            is_float = False
        return is_float

    @classmethod
    def is_positive_or_zero_integer(cls, value):
        try:
            int_value = int(value)
            if isinstance(value, float):
                return False
            if int_value >= 0:
                return True
        except ValueError:
            pass
        return False

    @classmethod
    def is_positive_integer(cls, value):
        try:
            int_value = int(value)
            if isinstance(value, float):
                return False
            if int_value > 0:
                return True
        except ValueError:
            pass
        return False

    @classmethod
    def remove_all_space(cls, s):
        s = s or ''
        s = str(s).strip()
        s = s.replace(" ", "")
        s = s.replace(" ", "")
        return s

    @classmethod
    def remove_space(cls, s):
        s = s or ''
        s = str(s).strip()
        return s

    @classmethod
    def get_short_id(cls):
        array = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                 "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                 "u", "v", "w", "x", "y", "z",
                 "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                 "U", "V", "W", "X", "Y", "Z"
                 ]
        id = str(uuid.uuid4()).replace("-", '')  # 注意这里需要用uuid4
        buffer = []
        for i in range(0, 8):
            start = i * 4
            end = i * 4 + 4
            val = int(id[start:end], 16)
            buffer.append(array[val % 62])
        return "".join(buffer)

    @classmethod
    def get_comma_splited_key(cls, a, b):
        """

        :param a: key
        :param b: another key
        :return: comma_splited_key, 'a, b'
        """
        new_key = '{}, {}'.format(a, b)
        return new_key

    @classmethod
    def get_comma_splited_key_multiple(cls, a, b, c):
        """

        :param a: key
        :param b: another key
        :param c:
        :return: comma_splited_key, 'a, b, c'
        """
        new_key = '{}, {}'.format(a, b, c)
        return new_key

    @classmethod
    def is_email_valid(cls, email):
        """校验邮箱是否合法(必须有@和.符号)"""
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
            return False
        else:
            return True

    @classmethod
    def get_file_key_by_name(cls, name):
        prefix, suffix = os.path.splitext(name)
        key = '{}!!!{}{}'.format(prefix, cls.get_short_id(), suffix)
        return key

    @classmethod
    def is_at_most_one_decimal_place(cls, s):
        if s.count('.') == 0:
            return s.isdigit() and int(s) > 0
        elif s.count('.') == 1:
            parts = s.split('.')
            # Check that parts[0] (before decimal) is a digit and not 0, unless parts[1] (after decimal) is not 0
            # Also, check that parts[1] is at most 1 digit
            return parts[0].isdigit() and (int(parts[0]) > 0 or int(parts[1]) > 0) and (
                        len(parts[1]) <= 1 and parts[1].isdigit())
        else:
            return False

    @classmethod
    def replace_newline(cls, s):
        if not s:
            return s
        else:
            return s.replace('\n', '\\n')

    @classmethod
    def replace_with_newline(cls, s):
        if not s:
            return s
        else:
            return s.replace('\\n', '\n')

    @classmethod
    def to_camel_case(cls, snake_str):
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @classmethod
    def generate_random_string(cls, k=6):
        # Generate a random string of 6 digits
        import random
        import string
        return ''.join(random.choices(string.digits, k=k))

    @classmethod
    def assert_unique(cls, model, code, name, pk, extra_queryset=None, external_code=None):
        """
        model valid_objects needed
        :param externalCode:
        :param extra_queryset:
        :param queryset:
        :param model:
        :param code:
        :param name:
        :param pk:
        :return:
        """
        if extra_queryset is not None:
            queryset = extra_queryset
        else:
            queryset = model.valid_objects.valid_queryset().exclude(pk=pk)
        if code:
            assert not queryset.filter(code=code).exists(), '编号已存在, 请重新输入.'
        if external_code:
            assert not queryset.filter(externalCode=external_code).exists(), '外部编号已存在, 请重新输入.'
        if name:
            assert not queryset.filter(name=name).exists(), '名称已存在, 请重新输入.'

    @classmethod
    def get_dot_transformed_list(cls, input_list):
        # Step 1: Initialize the transformed list
        transformed_list = []

        # Step 2 & 3: Loop through the input list and replace '.' with '__'
        for item in input_list:
            transformed_item = item.replace('.', '__')
            transformed_list.append(transformed_item)

        # Step 5: Return the transformed list
        return transformed_list

    @classmethod
    def decode_json_strings(cls, obj):
        import json
        if isinstance(obj, dict):
            return {k: cls.decode_json_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [cls.decode_json_strings(item) for item in obj]
        elif isinstance(obj, str):
            try:
                # Wrap the string in quotes and use json.loads to decode Unicode escapes
                return json.loads(f'"{obj}"')
            except json.JSONDecodeError:
                # If it's not a JSON string, return it as is
                return obj
        else:
            return obj


class UrlHelper:
    def __init__(self):
        super(UrlHelper, self).__init__()

    @classmethod
    def extract_image_name(cls, url):
        from urllib.parse import urlparse
        from urllib.parse import unquote
        # Parse the URL to get the path
        parsed_url = urlparse(url)
        # Split the path and get the last part
        image_name = parsed_url.path.split('/')[-1]
        return unquote(image_name)

    @classmethod
    def extract_image_guid_from_key(cls, url):
        from urllib.parse import urlparse
        from urllib.parse import unquote
        # Parse the URL to get the path
        parsed_url = urlparse(url)
        # Split the path and get the last part
        split_list = parsed_url.path.split('%2F')
        image_guid = split_list[-2]
        return image_guid
