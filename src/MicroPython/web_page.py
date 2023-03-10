import time

import json
import uasyncio as asyncio

import hue
import programs
from programs import ProgCol
from hue import col_list
import drive
from util import run_gc
from bootstrap import style, form_class, checkbox_class, form_rgb


class DirectException(Exception):
    pass


def process_post(post):
    if 'speed' in post:
        programs.SPEED = int(post['speed'])

    new_colors = []
    for color in col_list():
        if color in post:
            if post[color] == 'on':
                new_colors.append(color)

    if 'rgb' in post:
        if post['rgb'] == 'on':
            new_colors.append('rgb')

    if len(new_colors) > 0:
        programs.ProgCol.color_list = new_colors

    if 'program' in post:
        print(programs.CURR_PROG )
        programs.CURR_PROG = post['program']
        print(programs.CURR_PROG)

    if 'mode' in post:
        ProgCol.mode = post['mode']

    if 'r' in post and 'g' in post and 'b' in post:
        hue.set_rgb(int(post['r']), int(post['g']), int(post['b']))


def body():
    html = f'<html><head>{style}</head><body> Hello From Pixeltree <br />'
    html += f'<div class="form-group">{form()}</div></body></html>'
    return html


def header():
    return ('HTTP/1.1 200 OK\n'
            'Content-Type: text/html\n'
            'Connection: close\n\n')


async def json_response(writer):
    await writer.awrite('HTTP/1.1 200 OK\n')
    await writer.wait_closed()


def color_checkbox():
    html = '<table>'
    for color in col_list():
        checked = ''
        if color in programs.ProgCol.color_list:
            checked = 'checked'
        html += f'<tr><td> {color} </td><td><input type="checkbox" {checkbox_class} name="{color}" {checked}></td></tr>'
    checked = ''
    if 'rgb' in programs.ProgCol.color_list:
        checked = 'checked'
    html += f'<tr><td> RGB </td><td><input type="checkbox" name="rgb" {checked} {form_class}></td></tr></table>'
    return html


def program_select():
    html = f'<select name = "program" {form_class}><option value="{programs.CURR_PROG}">{programs.CURR_PROG}</option>'
    for prog in programs.programs:
        if prog in ('direct', 'run_frame'):
            continue
        html += f'<option value="{prog}">{prog}</option>'
    html += '</select>'
    return html


def mode_select():
    html = f'<select name = "mode" {form_class}><option value="{ProgCol.mode}">{ProgCol.mode}</option>'
    html += f'<option value="next">next</option>'
    html += f'<option value="random">random</option>'
    html += '</select>'
    return html


def rgb():
    html = 'RGB = '
    html += f'<input type="text" size="1" {form_rgb} name="r" value="{hue.RGB[1]}">'
    html += f'<input type="text" size="1" {form_rgb} name="g" value="{hue.RGB[0]}">'
    html += f'<input type="text" size="1" {form_rgb} name="b" value="{hue.RGB[2]}">'
    return html


def form():
    html = f'<form method="post"><input type="text" {form_class} name="speed" value="{programs.SPEED}"><br />'
    html += f'{program_select()}<br />{mode_select()}<br /><br />{color_checkbox()}<br />{rgb()}'
    html += f'<br /><br /><button class="btn btn-primary" type="submit">Submit</button></form>'
    return html


async def send_page(writer):
    """
    Send a Http web page to the provided connection.
    :param writer: object to dump webpage to
    :return:
    """
    await writer.awrite(header())
    await writer.awrite(body())


async def report_fail(writer, fail):
    """
    Send a Http web page to the provided connection.
    :param writer: object to dump webpage to
    :return:
    """
    print(f"REPORTING FAIL {fail}")
    response = 'HTTP/1.1 500 Internal Server Error\nContent-Type: text/html\nConnection: close\n\n'
    response += f"REQUEST failed. <br />{fail}"
    await writer.awrite(response)
    await asyncio.sleep(0.2)
    await writer.wait_closed()


async def parse_request(reader):
    read = await reader.read(1024)

    if read[0:3] == b'GET':
        return {'type': 'GET'}

    if read[0:4] != b'POST':
        raise RuntimeError('Request should be GET or POSt')

    results = {'type': 'POST'}

    data = read.split(b'\r\n\r\n')

    for line in data[0].split(b'\r\n'):
        if line.startswith('Content-Length'):
            results['Content-Length'] = int(str(line).split(': ', 1)[1][:-1])
        if line.startswith('Content-Type'):
            results['Content-Type'] = str(line).split(': ', 1)[1][:-1]

    data = data[1]

    if results['Content-Type'] == 'application/octet-stream':
        await drive.frame_stream(data, reader)
        return {'frame': True}

    timer = time.ticks_ms()
    while len(data) < results['Content-Length']:
        if time.ticks_diff(time.ticks_ms(), timer) > 1000:
            raise TimeoutError('Reading data took to long')
        data += await reader.read(1024)

    if results['Content-Type'] == 'application/json':
        results['json'] = json.loads(data)
    else:
        results['post'] = {}
        for line in data.split(b'&'):
            split = line.split(b'=')
            results['post'][split[0].decode('ascii')] = split[1].decode('ascii')

    return results


async def serve(reader, writer):
    """
    :param reader: Stream providing data
    :param writer: Stream to return data
    :return:
    """
    result = {}
    try:
        result = await parse_request(reader)
    except Exception as e:
        await report_fail(writer, e)
        return

    try:
        if 'frame' in result:
            await json_response(writer)
            await run_gc()
            return

        if 'json' in result:
            drive.direct(result['json'])
            await json_response(writer)
            await run_gc()
            return

        if 'post' in result:
            process_post(result['post'])

        await send_page(writer)
        await run_gc(200)
        await writer.wait_closed()

    except Exception as e:
        print(f"Unexpected exception : {e}")
