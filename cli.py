# -*- coding: utf-8 -*-

import json
import better_exceptions
import click
import dill

import easytrader

ACCOUNT_OBJECT_FILE = 'account.session'


@click.command()
@click.option('--use', help='指定券商 [ht, yjb, yh]')
@click.option('--prepare', type=click.Path(exists=True), help='指定登录账户文件路径')
@click.option('--get', help='调用 easytrader 中对应的变量')
@click.option('--do', help='调用 easytrader 中对应的函数名')
@click.option('--debug', default=False, help='是否输出 easytrader 的 debug 日志')
@click.argument('params', nargs=-1)
def main(prepare, use, do, get, params, debug):
    if get is not None:
        do = get
    if prepare is not None and use in ['ht_client', 'yjb', 'yh_client','yh','ht', 'gf', 'xq']:
        user = easytrader.use(use, debug)
        user.prepare(prepare)
        with open(ACCOUNT_OBJECT_FILE, 'wb') as f:
            dill.dump(user, f)
    if do is not None:
        with open(ACCOUNT_OBJECT_FILE, 'rb') as f:
            user = dill.load(f)

        if get is not None:
            result = getattr(user, do)
        else:
            result = getattr(user, do)(*params)

        json_result = json.dumps(result, indent=4, ensure_ascii=False, sort_keys=True)
        click.echo(json_result)


if __name__ == '__main__':
    main()
