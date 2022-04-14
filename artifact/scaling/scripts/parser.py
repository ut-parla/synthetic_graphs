import argparse

parse = argparse.ArgumentParser(description='Parse and extract actual/expected runtime')
parse.add_argument('-actual', metavar='actual', type=str, help='The output file of run.py')
parse.add_argument('-expect', metavar='expect', type=str, help='The output file of viz.py')
parse.add_argument('-output', metavar='output', type=str, help='The output file of this script')
args = parse.parse_args()

"""
@param ap actual data path
@param ep expected data path
@param op output path of parsing
"""
def parse(ap: str, ep: str, op: str):
  # Parse time information.
  with open(ap) as f:
    actual_summary = f.readlines()
    actual_summary = actual_summary[-2:-1]
  with open(ep) as f:
    expect_summary = f.readlines()
    expect_summary = expect_summary[-2:-1]

  actual_summary = actual_summary[0].split('| ')[1]
  actual_summary = actual_summary.split(' = ')[1].split('\n')[0]
  expect_summary = expect_summary[0].split(': ')[1]
  expect_summary = expect_summary.split(' seconds')[0]

  print("Actual summary:", actual_summary)
  print("Expected summary:", expect_summary)

  # Parse file name for labels.
  label = ap.split('/')[-1].split('.out')[0]
  print("Label:", label)

  with open(op, "a+") as f:
    f.write(label+","+actual_summary+","+expect_summary+"\n")


if __name__ == '__main__':
  print("Output of run.py (actual data): ", args.actual)
  print("Output of viz.py (expected data): ", args.expect)
  print("Output path: ",  args.output)
  parse(args.actual, args.expect, args.output)
