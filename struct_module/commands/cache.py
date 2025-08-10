from struct_module.commands import Command
import os
from pathlib import Path
import shutil

class CacheCommand(Command):
  def __init__(self, parser):
    super().__init__(parser)
    parser.add_argument('action', choices=['inspect', 'clear'], help='Inspect cache contents or clear cache')
    parser.add_argument('--cache-dir', type=str, default=os.path.expanduser('~/.struct/cache'), help='Path to cache directory')
    parser.set_defaults(func=self.execute)

  def execute(self, args):
    cache_dir = Path(args.cache_dir)
    if args.action == 'inspect':
      if not cache_dir.exists() or not any(cache_dir.iterdir()):
        print('Cache is empty.')
        return
      for path in cache_dir.iterdir():
        if path.is_file():
          print(f"{path}: {path.stat().st_size} bytes")
    elif args.action == 'clear':
      if cache_dir.exists():
        shutil.rmtree(cache_dir)
      cache_dir.mkdir(parents=True, exist_ok=True)
      print('Cache cleared.')
