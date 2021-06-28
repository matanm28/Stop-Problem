def parse_args():
  import argparse
  import os

  parser = argparse.ArgumentParser(description='Convert Excel to JSON')
  parser.add_argument(
    '-f', '--force',
    help='Overwrite destination file if it already exists')
  parser.add_argument(
    '-o', '--outfile',
    help='Destination file (.json)')
  parser.add_argument(
    '-q', '--quiet',
    action='store_true',
    default=False,
    help='Be quiet')
  parser.add_argument(
    'src',
    nargs='+',
    type=str,
    help='source file (.xlsx)')

  return parser.parse_args()

def records_for_json(df):
  columns = [str(k) for k in df.columns]
  return [dict(zip(columns, row)) for row in df.values]

def main():
  import os
  import simplejson as json
  import pandas as pd

  class PandasJsonEncoder(json.JSONEncoder):
    def default(self, obj):
      import datetime
      if any(isinstance(obj, cls) for cls in (datetime.time, datetime.datetime, pd.Timestamp)):
        return obj.isoformat()
      elif pd.isnull(obj):
        return None
      else:
        return super(PandasJsonEncoder, self).default(obj)

  args = parse_args()

  for src in args.src:
    if args.outfile:
      dst = args.outfile
    else:
      filename, _ = os.path.splitext(os.path.basename(src))
      dst = f'{filename}.json'

    all_sheet_data = []

    for sheet_name in pd.ExcelFile(src).sheet_names:
      sheet = pd.read_excel(src, sheet_name=sheet_name)
      records = records_for_json(sheet)
      all_sheet_data.append({ 'sheet_name': sheet_name, 'records': records })

    mode = 'w' if args.force else 'x'
    with open(dst, mode) as f:
      json.dump(all_sheet_data, f, ignore_nan=True, cls=PandasJsonEncoder, indent=4)

    if not args.quiet:
      arrow = '\u2192'
      print(f'{src} {arrow} {dst}')

if __name__ == '__main__':
  main()