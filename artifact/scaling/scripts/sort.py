import argparse

parse = argparse.ArgumentParser(description='Sort runtime')
parse.add_argument('-input', metavar='output', type=str, help='The output file of this script')
args = parse.parse_args()

ctype_order = [ "independent", "serial", "random", "reduce" ]
dtype_order = [ "lazy", "eager" ]
mem_size_order = [ "50%", "30%", "1%" ]
column_order = [ "1g", "2g", "4g" ]



def sort(ip: str):
  with open(ip) as f:
    results = f.readlines()
    #for line in results:
    #  splitted = line.split(',')
    #  benchname = splitted[0]
    #  runtime = float(splitted[1])
    #  print("Bench:", benchname, " runtime:", runtime)

    print_str = ""
    for mem_size in mem_size_order:
      for workload in ctype_order:
        for target_type in dtype_order:
          for column in column_order:
            print(workload, " ", target_type, " ", mem_size, " ", column, " ")
            for line in results:
              if workload in line and target_type in line and mem_size in line and \
                column in line:
                splitted = line.split(",")
                benchname = splitted[0]
                runtime = float(splitted[1])
                print_str += str(runtime) + ","
                print("\tBench:", benchname, " runtime:", runtime)
          print_str += "\n"

    print_str += "Lower bound\n"
    for mem_size in mem_size_order:
      for workload in ctype_order:
        for target_type in dtype_order:
          for column in column_order:
            print(workload, " ", target_type, " ", mem_size, " ", column, " ")
            for line in results:
              if workload in line and target_type in line and mem_size in line and \
                column in line:
                splitted = line.split(",")
                benchname = splitted[0]
                runtime = float(splitted[2])
                print_str += str(runtime) + ","
                print("\tBench:", benchname, " lower_bound:", runtime)
          print_str += "\n"
    print(print_str)

if __name__ == "__main__":
  sort(args.input)
      

