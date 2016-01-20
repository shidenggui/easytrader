import dill
import click
import anyjson as json
import easytrader

ACCOUNT_OBJECT_FILE = 'account.session'


@click.command()
@click.option('--use', help='指定券商 [ht, yjb]')
@click.option('--prepare', type=click.Path(exists=True), help='指定登录账户文件路径')
@click.option('--get', help='调用 easytrader 中对应的变量')
@click.option('--do', help='调用 easytrader 中对应的函数名')
@click.argument('params', nargs=-1)
def main(prepare, use, do, get, params):
    if get is not None:
        do = get
    if prepare is not None and use in ['ht', 'yjb']:
        user = easytrader.use(use)
        user.prepare(prepare)
        with open(ACCOUNT_OBJECT_FILE, 'wb') as f:
            dill.dump(user,f)
    if do is not None:
        with open(ACCOUNT_OBJECT_FILE, 'rb') as f:
            user = dill.load(f)

        if len(params) > 0:
            result = getattr(user, do)(*params)
        else:
            result = getattr(user, do)

        json_result = json.dumps(result)
        click.echo(json_result)


if __name__ == '__main__':
    main()
