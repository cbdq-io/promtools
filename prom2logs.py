#!/usr/bin/env python
"""
Extract Prometheus metrics and expose them as logs.

The following environment variables can be configured:

- LOG_LEVEL (optional) The log level if set to WARNING or higher no
  logs will be produced.  Default is INFO.
- METRIC_REGEX_LIST (optional) A CSV list of regex expressions to compare
  against to identify which metrics should be logged.  Defaults to "^.*$".
- PROM_API_ENDPOINT (optional) The endpoint for the Prometheus endpoint,
  defaults to http://localhost:9090/api/v1

Additional optional environment variables:

- FANOUT_METRICS (optional) Fan out certain metrics per discovered instance.
  Format:
    "<container type>:<metric regex>:<discovery query>|<container type>:<metric regex>:<discovery query>|..."
  Example:
    FANOUT_METRICS="router:^process_resident_memory_bytes$:message_processing_seconds_count|archivist:^process_resident_memory_bytes$:archivist_file_count_created"

  For fanned out metrics, the emitted prefix will be:
    "<container type><suffix>_<metric> <value>"

  The suffix is 5 digits:
    - first 3 digits: last octet of the instance IP, zero-padded (e.g. 8 -> 008)
    - last 2 digits: last 2 digits of the port, zero-padded (e.g. 8001 -> 01)
  Example:
    instance "10.86.0.8:8001" => router00801_process_resident_memory_bytes <value>
"""
import logging
import json
import os
import re
import time
import urllib.request


PROG = os.path.basename(__file__)
METRIC_REGEX_LIST = os.environ.get('METRIC_REGEX_LIST', '^.*$')
PROM_API_ENDPOINT = os.environ.get('PROM_API_ENDPOINT', 'http://localhost:9090/api/v1')
FANOUT_METRICS = os.environ.get('FANOUT_METRICS', '')

logging.basicConfig()
logger = logging.getLogger(PROG)
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logger.setLevel(level=log_level)
logger.debug(f'Log level is "{log_level}".')
logger.debug(f'METRIC_REGEX_LIST is "{METRIC_REGEX_LIST}".')
logger.debug(f'PROM_API_ENDPOINT is "{PROM_API_ENDPOINT}".')
logger.debug(f'FANOUT_METRICS is "{FANOUT_METRICS}".')


def get_metrics_of_interest(metric_regex_list: str) -> list[str]:
    """
    Get a list of metrics that are of interest to us.

    Parameters
    ----------
    metric_regex_list : str
      A CSV list of regular expressions to compare the list of metrics that
      we get from Prometheus.  If the expression matches a metric name, add
      that metric as a metric of interest.

    Returns
    -------
    list[str]
      The metrics of interest.
    """
    metrics_of_interest = []
    regular_expressions = metric_regex_list.split(',')
    url = f'{PROM_API_ENDPOINT}/label/__name__/values'

    try:
        with urllib.request.urlopen(url) as stream:
            data = json.load(stream)

        all_metrics = data['data']
    except Exception as ex:
        logger.error(ex)
        all_metrics = []

    for metric in all_metrics:
       for regex in regular_expressions:
           if re.search(regex, metric):
               metrics_of_interest.append(metric)
               break

    return metrics_of_interest


def get_query_results(url: str, data: str) -> list:
    try:
        req = urllib.request.Request(url=url, data=data.encode())

        with urllib.request.urlopen(req) as stream:
            data = json.load(stream)

        return data.get('data', {}).get('result', [])
    except Exception as ex:
        logger.error(ex)
        return []


def get_query_response(url: str, data: str) -> float:
    try:
        req = urllib.request.Request(url=url, data=data.encode())

        with urllib.request.urlopen(req) as stream:
            data = json.load(stream)

        results = data.get('data', {}).get('result', [])
        total = 0.0

        for item in results:
            try:
                value = item['value'][1]
                total += float(value)
            except (KeyError, ValueError, TypeError):
                continue

        return str(int(total)) if total.is_integer() else str(total)

    except Exception as ex:
        logger.error(ex)
        return None


def build_instance_suffix(instance: str) -> str:
    # instance expected as "<ip>:<port>"
    try:
        ip, port_str = instance.rsplit(':', 1)
        octets = ip.split('.')
        if len(octets) != 4:
            return None

        # last octet, zero-padded to 3 digits
        last_octet = f'{int(octets[3]):03d}'

        # last 2 digits of port, zero-padded
        port_last2 = f'{int(port_str) % 100:02d}'

        return f'{last_octet}{port_last2}'
    except Exception as ex:
        logger.error(ex)
        return None


def parse_fanout_metrics(spec: str) -> list[dict]:
    """
    Parse FANOUT_METRICS into a list of dicts:
    [{"type": "...", "fanout_regex": "...", "discovery_query": "..."}]
    """
    groups = []
    if not spec:
        return groups

    for part in spec.split('|'):
        part = part.strip()
        if not part:
            continue

        try:
            container_type, fanout_regex, discovery_query = part.split(':', 2)
            container_type = container_type.strip()
            fanout_regex = fanout_regex.strip()
            discovery_query = discovery_query.strip()

            if not container_type or not fanout_regex or not discovery_query:
                continue

            # sanity check regex early so a bad regex doesn't break later
            re.compile(fanout_regex)

            groups.append({
                'type': container_type,
                'fanout_regex': fanout_regex,
                'discovery_query': discovery_query,
            })
        except Exception as ex:
            logger.error(ex)
            continue

    return groups


def build_fanout_instance_map(prom_query_url: str, container_type: str, discovery_query: str) -> dict[str, str]:
    """
    discovery_query is a PromQL query. We use the returned series' 'instance' label
    to map instance -> "<container_type><suffix>" (e.g. router00800).
    """
    instance_map = {}
    data = f'query={discovery_query}'
    results = get_query_results(prom_query_url, data)

    for item in results:
        try:
            instance = item.get('metric', {}).get('instance')
            if not instance:
                continue

            suffix = build_instance_suffix(instance)
            if not suffix:
                continue

            instance_map[instance] = f'{container_type}{suffix}'
        except Exception as ex:
            logger.error(ex)
            continue

    return instance_map


def get_fanout_groups_for_metric(metric_name: str, groups: list[dict]) -> list[dict]:
    matches = []
    for g in groups:
        try:
            if re.search(g['fanout_regex'], metric_name):
                matches.append(g)
        except Exception as ex:
            logger.error(ex)
            continue
    return matches


while True:
    metrics_of_interest = get_metrics_of_interest(METRIC_REGEX_LIST)
    logger.debug(f'metrics_of_interest "{",".join(metrics_of_interest)}".')
    url = f'{PROM_API_ENDPOINT}/query'

    fanout_groups = parse_fanout_metrics(FANOUT_METRICS)
    fanout_instance_maps = {}

    for g in fanout_groups:
        try:
            fanout_instance_maps[g['type']] = build_fanout_instance_map(
                url, g['type'], g['discovery_query']
            )
        except Exception as ex:
            logger.error(ex)
            continue

    logger.debug(f'fanout_instance_maps "{json.dumps(fanout_instance_maps)}".')

    for metric in metrics_of_interest:
        fanout_groups_for_metric = get_fanout_groups_for_metric(metric, fanout_groups)

        # If the metric is configured for fanout (possibly by multiple rules),
        # emit one log line per discovered instance per matching rule.
        if fanout_groups_for_metric:
            data = f'query={metric}'
            results = get_query_results(url, data)

            for g in fanout_groups_for_metric:
                try:
                    ctype = g['type']
                    instance_map = fanout_instance_maps.get(ctype, {})
                    if not instance_map:
                        continue

                    for item in results:
                        try:
                            instance = item.get('metric', {}).get('instance')
                            if not instance:
                                continue

                            name = instance_map.get(instance)
                            if not name:
                                continue

                            value = item['value'][1]
                            logger.info(f'{name}_{metric} {value}')
                        except Exception as ex:
                            logger.error(ex)
                            continue
                except Exception as ex:
                    logger.error(ex)
                    continue

            # Important: don't also emit the summed version if we fanned out
            continue

        # Default stable behaviour: sum across all series
        data = f'query={metric}'
        value = get_query_response(url, data)
        logger.info(f'{metric} {value}')

    time.sleep(60)
