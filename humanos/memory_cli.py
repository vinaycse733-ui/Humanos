"""Explicit memory commands; JSON output avoids terminal control injection."""
import argparse
import json
import sqlite3
import sys
from pathlib import Path
from .memory import Memory


def main(argv=None):
    parser = argparse.ArgumentParser(description="Manage local HumanOS notes")
    parser.add_argument('--db', type=Path, required=True)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('add', help='Read note from standard input')
    search = commands.add_parser('search')
    search.add_argument('query', nargs='?', default='')
    commands.add_parser('export', help='Write JSON to standard output')
    delete = commands.add_parser('delete')
    delete.add_argument('id', type=int)
    args = parser.parse_args(argv)
    try:
        if not args.db.exists():
            if args.command != 'add':
                raise ValueError('Memory database does not exist')
            args.db.touch(mode=0o600, exist_ok=False)
        memory = Memory(args.db)
        if args.command == 'add':
            result = {'id': memory.add(sys.stdin.read(100001))}
        elif args.command == 'delete':
            result = {'deleted': memory.delete(args.id)}
        else:
            result = memory.search(args.query if args.command == 'search' else '')
        print(json.dumps(result, ensure_ascii=True))
    except (OSError, ValueError, sqlite3.Error) as exc:
        print(f'Memory error: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
