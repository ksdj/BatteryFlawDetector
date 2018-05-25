#!/usr/bin/env python3
# coding:utf-8
# __author__：Corwin.Zhang
# __create_date__：'2017/12/12 16:56'
# __company__：上海洪朴信息科技有限公司
"""
    manage src,eg:start an app.
"""

import logging
import os
import os.path as osp
import click
import sys

from utils import config, initlogging
from client_py.thrift_client import main as client_main
from server_py.thrift_server import main as server_main


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo('Please input subcommand')
        return
    # initlogging(os.path.dirname(os.path.abspath(__file__)) + '/temp/app_mgr.log')
    logging.getLogger().info(
        'invoke command {0}'.format(
            ctx.invoked_subcommand))

@cli.command()
def thrift_client():
    initlogging('thrift_client.log')
    logging.info('start thrift_client server...')
    client_main()
            

@cli.command()
@click.option('--timing','-t', default=1, type=float, help='inidcate the algo timing')
def thrift_server(timing):
    initlogging('thrift_server.log')
    server_main(timing)
      

@cli.command()
def hello():
    print("hello")

if __name__ == '__main__':
    cli(sys.argv[1:])

