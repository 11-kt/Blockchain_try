import argparse
from Application import start_work


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('num_node', type=str, help='if num_node is zero, then node generate genesis')
    parser.add_argument('nonce_type', type=str, help="nonce generation type")

    args = parser.parse_args()

    start_work(args.num_node, args.nonce_type)
