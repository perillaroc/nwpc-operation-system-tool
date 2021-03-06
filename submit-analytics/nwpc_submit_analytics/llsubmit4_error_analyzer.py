#!/cma/g3/wangdp/usr/local/bin/python3
import subprocess
import re
import datetime
import json
from collections import defaultdict

import click


def get_system_from_path(path):
    if path == "/":
        return None
    if not path.startswith('/'):
        return None
    index = path.find('/', 1)
    return path[1: index]


def run_command(command):
    pipe = subprocess.Popen([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error_output = pipe.communicate()
    output_string = None
    if output is not None:
        output_string = output.decode()
    error_output_string = None
    if error_output is not None:
        error_output_string = error_output.decode()
    return output_string, error_output_string


def parse_error_log(log_string):
    p = re.compile('^\[(.*)\]\[(.*)\](.*): (.*) (.*) (.*) (.*)$')
    m = p.match(log_string)
    date_string = m.group(1)
    command = m.group(2)
    message = m.group(3)
    job_script = m.group(4)
    path = m.group(5)
    total_tries = m.group(6)
    current_try_no = m.group(7)
    record = dict()
    record['date'] = datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%Z')
    record['command'] = command
    record['message'] = message
    record['info'] = {
        'job_script': job_script,
        'path': path,
        'total_tries': total_tries,
        'current_try_no': current_try_no
    }
    return record


def get_record_field_value(record, name):
    def get_date_hour(x):
        cur_datetime = x['date']
        cur_date = cur_datetime.date()
        zero_time = datetime.time(cur_datetime.hour)
        cur_hour = datetime.datetime.combine(cur_date, zero_time)
        return cur_hour.strftime("%Y-%m-%d %H:%M:%S")

    field_mapper = {
        'month': lambda x: x['date'].strftime("%Y-%m"),
        'date': lambda x: x['date'].strftime("%Y-%m-%d"),
        'weekday': lambda x: x['date'].weekday(),
        'system': lambda x: get_system_from_path(x['info']['path']),
        'date-hour': get_date_hour,
        'hour': lambda x: x['date'].hour,
    }

    if name in field_mapper:
        return field_mapper[name](record)
    else:
        raise Exception('name unsupported', name)


@click.group()
def cli():
    """
DESCRIPTION
    Analytic llsubmit4 error log."""
    pass


@cli.command('info', help='get log file info')
@click.option('-f', '--file', 'log_file_path', required=True, help="log file path")
@click.option("--pretty-print/--no-pretty-print", default=False, help="print pretty result.")
def info(log_file_path, pretty_print):
    """
    get log file info
    """

    command = "head -n 1 {log_file_path}".format(log_file_path=log_file_path)
    output_string, error_string = run_command(command)
    if len(error_string) > 0:
        result = {
            'app': 'llsubmit4_error_analyzer',
            'type': 'range',
            'timestamp': datetime.datetime.now().timestamp(),
            'error': 'head_command_error',
            'data': {
                'error_message': 'error in executing head command.',
                'output': {
                    'std_out': output_string,
                    'std_err': error_string
                },
                'request': {
                    'log_file_path': log_file_path,
                }
            }
        }

        if pretty_print:
            print(json.dumps(result, indent=4))
        else:
            print(json.dumps(result))
        return

    record = parse_error_log(output_string)
    start_date = record['date']

    command = "tail -n 1 {log_file_path}".format(log_file_path=log_file_path)
    output_string, error_string = run_command(command)
    if len(error_string) > 0:
        result = {
            'app': 'llsubmit4_error_analyzer',
            'type': 'range',
            'timestamp': datetime.datetime.now().timestamp(),
            'error': 'tail_command_error',
            'data': {
                'error_message': 'error in executing tail command.',
                'output': {
                    'std_out': output_string,
                    'std_err': error_string
                },
                'request': {
                    'log_file_path': log_file_path,
                }
            }
        }

        if pretty_print:
            print(json.dumps(result, indent=4))
        else:
            print(json.dumps(result))
        return

    record = parse_error_log(output_string)
    end_date = record['date']

    command = "wc -l {log_file_path}".format(log_file_path=log_file_path)
    output_string, error_string = run_command(command)
    if len(error_string) > 0:
        result = {
            'app': 'llsubmit4_error_analyzer',
            'type': 'range',
            'timestamp': datetime.datetime.now().timestamp(),
            'error': 'tail_command_error',
            'data': {
                'error_message': 'error in executing wc command.',
                'output': {
                    'std_out': output_string,
                    'std_err': error_string
                },
                'request': {
                    'log_file_path': log_file_path,
                }
            }
        }

        if pretty_print:
            print(json.dumps(result, indent=4))
        else:
            print(json.dumps(result))

        return

    line_count = int(output_string.strip().split(' ')[0])

    # with open(log_file_path, 'r') as log_file:
    #     for line in log_file:
    #         record = parse_error_log(line)
    #         print(record['date'])

    result = {
        'app': 'llsubmit4_error_analyzer',
        'type': 'info',
        'timestamp': datetime.datetime.now().timestamp(),
        'data': {
            'range': {
                'start_date_time': start_date.strftime('%Y-%m-%dT%H:%M:%S%Z'),
                'end_date_time': end_date.strftime('%Y-%m-%dT%H:%M:%S%Z'),
                'count': line_count
            },
            'request': {
                'log_file_path': log_file_path,
            }
        }
    }
    if pretty_print:
        print(json.dumps(result, indent=4))
    else:
        print(json.dumps(result))


@cli.command('count', help='count errors in error log file.')
@click.option("-f", "--file", "log_file_path", required=True, help="log file path")
@click.option("--begin-date", help="begin date, YYYY-MM-DD")
@click.option("--end-date", help="end date, YYYY-MM-DD")
@click.option("--begin-time", help="begin time, hh:mm:ss")
@click.option("--end-time", help="end time, hh:mm:ss")
@click.option("--type", "count_type", required=True,
              type=click.Choice(['month', 'date', 'weekday', 'date-hour', 'hour', 'system']),
              help="count type", )
@click.option("--pretty-print/--no-pretty-print", default=False, help="print pretty result.")
def count(log_file_path, begin_date, end_date, begin_time, end_time, count_type, pretty_print):
    """
    count errors in error log file.
    """
    if begin_date:
        begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    if end_date:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    count_result = defaultdict(int)
    try:
        with open(log_file_path, 'r') as log_file:
            for line in log_file:
                record = parse_error_log(line)
                # check date
                if begin_date:
                    if record['date'].date() < begin_date.date():
                        continue
                if end_date:
                    if record['date'].date() >= end_date.date():
                        continue

                count_result[get_record_field_value(record, count_type)] += 1

    except FileNotFoundError as e:
        result = {
            'app': 'llsubmit4_error_analyzer',
            'type': 'count',
            'error': 'file_not_found',
            'timestamp': datetime.datetime.now().timestamp(),
            'data': {
                'error_message': 'file is not found',
                'request': {
                    'log_file_path': log_file_path,
                    'begin_date': begin_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'count_type': count_type
                }
            }
        }
        if pretty_print:
            print(json.dumps(result, indent=4))
        else:
            print(json.dumps(result))
        return

    result = {
        'app': 'llsubmit4_error_analyzer',
        'type': 'count',
        'timestamp': datetime.datetime.now().timestamp(),
        'data': {
            # 'count_type': count_type,
            # 'begin_date': begin_date.strftime('%Y-%m-%d'),
            # 'end_date': end_date.strftime('%Y-%m-%d'),
            # 'count_result': count_result,
            'request': {
                'log_file_path': log_file_path,
                'begin_date': begin_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'count_type': count_type
            },
            'response': {
                'count_result': count_result,
            }
        }
    }

    if pretty_print:
        print(json.dumps(result, indent=4))
    else:
        print(json.dumps(result))


@cli.command('grid', help='get grid result.')
@click.option("-f", "--file", "log_file_path", required=True, help="log file path")
@click.option("--begin-date", help="begin date, YYYY-MM-DD")
@click.option("--end-date", help="end date, YYYY-MM-DD")
@click.option("--begin-time", help="begin time, hh:mm:ss")
@click.option("--end-time", help="end time, hh:mm:ss")
@click.option("--x-type", "x_type", required=True,
              type=click.Choice(['hour', 'weekday']),
              help="x axis type")
@click.option("--y-type", "y_type", required=True,
              type=click.Choice(['weekday', 'system', 'date']),
              help="y axis type")
@click.option("--pretty-print/--no-pretty-print", default=False, help="print pretty result.")
def grid(log_file_path, begin_date, end_date, begin_time, end_time, x_type, y_type, pretty_print):
    """
    get grid result.
    """
    if begin_date:
        begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    if end_date:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    grid_result = dict()
    try:
        with open(log_file_path, 'r') as log_file:
            for line in log_file:
                record = parse_error_log(line)
                # check date
                if begin_date:
                    if record['date'].date() < begin_date.date():
                        continue
                if end_date:
                    if record['date'].date() >= end_date.date():
                        continue

                x_value = get_record_field_value(record, x_type)
                y_value = get_record_field_value(record, y_type)

                if x_value not in grid_result:
                    grid_result[x_value] = dict()
                if y_value not in grid_result[x_value]:
                    grid_result[x_value][y_value] = 0
                grid_result[x_value][y_value] += 1

    except FileNotFoundError:
        result = {
            'app': 'llsubmit4_error_analyzer',
            'type': 'grid',
            'error': 'file_not_found',
            'timestamp': datetime.datetime.now().timestamp(),
            'data': {
                'error_message': 'file is not found',
                'request': {
                    'log_file_path': log_file_path,
                }
            }
        }
        if pretty_print:
            print(json.dumps(result, indent=4))
        else:
            print(json.dumps(result))
        return

    result = {
        'app': 'llsubmit4_error_analyzer',
        'type': 'grid',
        'timestamp': datetime.datetime.now().timestamp(),
        'data': {
            'response': {
                'grid_result': grid_result,
            },
            'request': {
                'log_file_path': log_file_path,
                'x_type': x_type,
                'y_type': y_type,
                'begin_date': begin_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
            }
        }
    }

    if pretty_print:
        print(json.dumps(result, indent=4))
    else:
        print(json.dumps(result))


if __name__ == "__main__":
    cli()
