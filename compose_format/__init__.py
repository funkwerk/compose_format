from ruamel.yaml import RoundTripDumper, RoundTripLoader, dump, load
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.scalarstring import SingleQuotedScalarString


class ComposeFormat:
    TOPLEVEL_ORDER = ['version', 'services', 'volumes', 'networks', 'secrets']
    SERVICE_ORDER = [
        'image', 'command', 'entrypoint', 'container_name',
        'links', 'volumes_from', 'volumes', 'volume_driver', 'tmpfs',
        'build',
        'expose', 'ports',
        'net', 'network_mode', 'networks',
        'deploy',
        'labels',
        'devices',
        'read_only',
        'healthcheck',
        'env_file', 'environment',
        'secrets',
        'cpu_shares', 'cpu_quota', 'cpuset', 'domainname', 'hostname', 'ipc',
        'mac_address', 'mem_limit', 'memswap_limit', 'privileged', 'shm_size',
        'depends_on', 'extends', 'external_links',
        'stdin_open', 'user', 'working_dir',
        'extra_hosts', 'restart', 'ulimits', 'tty', 'dns', 'dns_search', 'pid',
        'security_opt', 'cap_add', 'cap_drop', 'cgroup_parent', 'logging', 'log_driver', 'log_opt',
        'stopsignal', 'stop_signal', 'stop_grace_period',
        'sysctls', 'userns_mode',
        'autodestroy', 'autoredeploy',
        'deployment_strategy', 'sequential_deployment', 'tags', 'target_num_containers',
        'roles',
    ]
    DEPLOY_ORDER = [
        'placement', 'replicas', 'mode',
        'update_config',
        'resources',
        'restart_policy',
        'labels',
    ]
    HEALTHCHECK_ORDER = [
        'test',
        'interval', 'timeout', 'retries',
        'disable',
    ]
    BUILD_ORDER = [
        'context',
        'dockerfile',
        'target',
        'args'
    ]
    ORDERS = {
        'version': TOPLEVEL_ORDER,
        'services': TOPLEVEL_ORDER,
        'image': SERVICE_ORDER,
        'dockerfile': BUILD_ORDER,
        'placement': DEPLOY_ORDER,
        'replicas': DEPLOY_ORDER,
        'test': HEALTHCHECK_ORDER,
    }
    NON_SORTABLE_ARRAYS = [
        'entrypoint',
        'command',
        'test',
    ]

    def __init__(self):
        pass

    def format(self, path, replace=False, strict=True):
        with open(path, 'r') as file:
            data = file.read()
        original = data
        formatted = self.format_string(data, replace=replace, strict=strict)

        if replace:
            with open(path, 'w') as file:
                file.write(formatted)
        else:
            print(formatted)
        return original == formatted

    def format_string(self, data, replace=False, strict=True):
        data = self.reorder(load(data, RoundTripLoader), strict=strict)
        formatted = dump(data, Dumper=RoundTripDumper, indent=2, width=120)

        return formatted.strip() + '\n'

    @staticmethod
    def reorder(data, strict=True):
        if type(data) is CommentedMap:
            order = ComposeFormat.order_map(list(data.keys()))
            keys = list(data.keys())

            while ComposeFormat.sorted_by_order(keys, order, strict) != keys:
                for a, b in zip(ComposeFormat.sorted_by_order(keys, order, strict), keys):
                    if a == b:
                        continue
                    data.move_to_end(b)
                    break
                keys = list(data.keys())
            for key, item in data.items():
                if key in ComposeFormat.NON_SORTABLE_ARRAYS:
                    continue
                ComposeFormat.reorder(item, strict)
            return data
        if type(data) is CommentedSeq:
            for i, value in enumerate(data):
                if type(value) is not CommentedMap:
                    data[i] = ComposeFormat.fix_sexadecimal_numbers(value)
            data.sort()
            return data
        return data

    @staticmethod
    def fix_sexadecimal_numbers(value):
        import re

        SEXADECIMAL_NUMBER = '(?P<left>\d+):(?P<right>\d+)'
        match = re.match(SEXADECIMAL_NUMBER, value)
        if not match or int(match.group('left')) > 60 or int(match.group('right')) > 60:
            return value
        return SingleQuotedScalarString('{0}:{1}'.format(match.group('left'), match.group('right')))

    @staticmethod
    def order_map(keys):
        for key in ComposeFormat.ORDERS.keys():
            if key in keys:
                return ComposeFormat.ORDERS[key]
        return None

    @staticmethod
    def sorted_by_order(keys, order, strict):
        if order is None:
            return sorted(keys)

        def order_function(key):
            if strict:
                assert key in order, 'key: {0} not known'.format(key)

            if key in order:
                return order.index(key)
            return len(order) + ComposeFormat.name_to_order(key)

        return sorted(keys, key=order_function)

    @staticmethod
    def name_to_order(value):
        from functools import reduce

        return reduce(lambda left, right: (left * 256 + right), (ord(char) for char in value))
