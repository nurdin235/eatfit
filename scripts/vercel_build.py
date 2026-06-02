import os
import subprocess
import sys


def enabled(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def run(*args):
    subprocess.run([sys.executable, 'manage.py', *args], check=True)


def database_configured():
    if os.environ.get('DATABASE_URL') or os.environ.get('SUPABASE_DATABASE_URL'):
        return True
    return all(os.environ.get(name) for name in ('DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST'))


def main():
    run('collectstatic', '--noinput')

    if enabled('RUN_DEPLOY_CHECKS', default=True):
        if enabled('DEBUG', default=False):
            run('check')
        else:
            run('check', '--deploy', '--fail-level', 'WARNING')

    if not enabled('RUN_DEPLOY_MIGRATIONS', default=False):
        return

    if not database_configured():
        raise SystemExit(
            'RUN_DEPLOY_MIGRATIONS=True requires DATABASE_URL/SUPABASE_DATABASE_URL '
            'or DB_NAME, DB_USER, DB_PASSWORD, and DB_HOST.'
        )

    run('migrate', '--noinput')

    if enabled('RUN_DEPLOY_SEED', default=True):
        run('seed_eatfit')


if __name__ == '__main__':
    main()
