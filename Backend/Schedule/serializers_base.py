from rest_framework import serializers


def to_camel_case(string):
    """将snake_case转换为camelCase"""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def to_snake_case(string):
    """将camelCase转换为snake_case"""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class CamelCaseModelSerializer(serializers.ModelSerializer):
    """自定义ModelSerializer,自动处理camelCase和snake_case的转换"""
    
    def to_representation(self, instance):
        """将输出字段名从snake_case转换为camelCase"""
        ret = super().to_representation(instance)
        return self._convert_nested_keys(ret)
    
    def _convert_nested_keys(self, data):
        """递归转换嵌套对象的字段名"""
        if isinstance(data, dict):
            converted = {}
            for key, value in data.items():
                camel_key = to_camel_case(key)
                if isinstance(value, dict):
                    converted[camel_key] = self._convert_nested_keys(value)
                elif isinstance(value, list):
                    converted[camel_key] = [self._convert_nested_keys(item) if isinstance(item, dict) else item for item in value]
                else:
                    converted[camel_key] = value
            return converted
        return data

    def to_internal_value(self, data):
        """将输入字段名从camelCase转换为snake_case"""
        # 如果是字典，进行字段名转换
        if isinstance(data, dict):
            new_data = {}
            for key, value in data.items():
                # 修复转换逻辑：对于camelCase格式的字段名也要进行转换
                snake_key = to_snake_case(key)
                if isinstance(value, dict):
                    new_data[snake_key] = self._convert_dict_values(value)
                elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
                    new_data[snake_key] = [self._convert_dict_values(item) for item in value]
                else:
                    new_data[snake_key] = value
            data = new_data
        
        return super().to_internal_value(data)
    
    def _convert_dict_values(self, data):
        """转换嵌套字典中的字段名"""
        if isinstance(data, dict):
            new_data = {}
            for key, value in data.items():
                snake_key = to_snake_case(key) if not ('_' in key or key.islower()) else key
                if isinstance(value, dict):
                    new_data[snake_key] = self._convert_dict_values(value)
                elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
                    new_data[snake_key] = [self._convert_dict_values(item) for item in value]
                else:
                    new_data[snake_key] = value
            return new_data
        return data