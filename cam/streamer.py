#!/usr/bin/env python3
import sys
import os
sys.path.insert(0,os.path.abspath("../"))
sys.path.insert(0,os.path.abspath("."))


import asyncio
import websockets
import argparse
import logging

from aiohttp import web
from cam import Broker,host,stream_port,ws_port


logging.basicConfig(level=logging.INFO)
led=Broker()
connected=[]

async def flow(request):
    led.show_success()
    while not request.content.is_eof():
        s=await request.content.readany()
        try:
            if connected:
                for ws in connected:
                        if ws.open:
                            await ws.send(s)
                        else:
                            led.show_error()
                            logging.info('Websocket on {}:{} closed'.format(*ws.local_address))
                            await ws.close()
                            connected.remove(ws)
        except:
            led.show_error()
            logging.error("Error occured on {}:{} ws_socket".format(*ws.local_address))
            await ws.close()
            connected.remove(ws)
    exit()
    return web.Response()


async def handler(websocket,path):
    #add web ws to pull to send data from webcam
    led.show_success()
    connected.append(websocket)
    logging.info('Websocket on {}:{} open'.format(* websocket.local_address))
    # little hack to keep connection opened
    try:
        while True:
            await asyncio.sleep(10)
            if not websocket.open:
                await websocket.close()
                connected.remove(websocket)
                return websocket
    except:
        if websocket in connected: connected.remove(websocket)
    return websocket


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('source',help="Source to supply video.Should be visible at /dev/video{x} where {x}=number of video source")
    parser.add_argument('--host',help="Address to listen on",default=host)
    parser.add_argument('--port',help="Port to listen on",default=stream_port,type=int)
    parser.add_argument('--ws_port', help="Port to listen websocket server on", default=ws_port,type=int)
    args=parser.parse_args()


    if not os.path.exists(args.source):
        raise IOError('Source import is not available')


    try:
        loop = asyncio.get_event_loop()
        # start  webapp
        app = web.Application()
        # add route for accepting request for streaming data form webcam
        app.router.add_route("POST", "/flow", flow)

        stream_server = asyncio.get_event_loop().create_server(app.make_handler(), args.host, args.port)
        ws_server = websockets.serve(handler, args.host, args.ws_port)

        logging.info("Stream server has started up.Listen on http://{}:{}/flow".format(args.host, args.port))
        loop.run_until_complete(stream_server)
        logging.info("Websocket server has started up.Listen on ws://{}:{}/".format(args.host, args.ws_port))
        loop.run_until_complete(ws_server)
        logging.info("Started streaming from webcam")
        loop.run_forever()
    except (KeyboardInterrupt,asyncio.CancelledError) as e:
        logging.info("Server is shutting down.")
        pending = asyncio.Task.all_tasks()
        loop.run_until_complete(asyncio.gather(*pending))
    finally:
        logging.info("Shutdown complete.")
        asyncio.sleep(10)
        loop.stop()