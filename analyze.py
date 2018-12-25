#!/usr/bin/env python

import argparse
import json
import networkx as nx
import pandas as pd
from pprint import pprint
import os
from scipy.special import comb
import operator as op

# Idea is to weight edges by the probability of acquiring these two cards
# according to https://boardgames.stackexchange.com/questions/8637/where-can-i-find-an-exhaustive-inventory-of-cards-in-ticket-to-ride
# there are 12 each of 8 different colors, plus 14 wilds.
edge_colors = ["orange", "blue", "red", "pink", "blue", "yellow", "green", "black"]
color_counts = [12,         12,     12, 12,     12,     12,         12,     12]
wildcard_counts = 14 
total_card_counts = sum(color_counts) + wildcard_counts
color_probs = [ (c+wildcard_counts) / (float(sum(color_counts))+wildcard_counts) for c in color_counts ]
def edge_probability(weight, colors):
    total_probs = []
    for c in colors:
        if c == 'gray':
            prob = 0
            #count number of ways to make flush with wildcards
            for given_wc in range(weight): # can get a wildcard for up to each weight
                wc_weight = weight - given_wc
                prob += comb(len(edge_colors), 1) * comb(12, wc_weight)

            # plus using entirely wildcards
            prob += comb(14, weight)

            prob /= comb(total_card_counts, weight)
            print "gray prob: {} weight={}".format(prob, weight)
        else:
            prob = comb(12, weight)
            prob /= comb(total_card_counts, weight)
            print "{} prob: {} weight={}".format(c, prob, weight)

        #either event happens so we add
        total_probs.append(prob)

    # sum minus the product
    if len(total_probs) > 1:
        return sum(total_probs) - reduce(op.mul, total_probs)
    return total_probs[0]

def read_graph(filename):
    f = open(filename)
    j = json.load(f)

    g = nx.Graph()

    for (from_, to, weight, colors) in j['routes']:
        # TODO handle colors
        edge_weight = 1-edge_probability( weight, colors )

        g.add_edge(from_, to, weight=edge_weight)
        print "{} <-> {}, colors: {} edge_weight (1-p): {}".format(from_, to, colors, edge_weight)

    j['graph'] = g
    return j

def analyze_critical_junctions(args, graph):
    # compute shortest path for each destination pairs
    # an interesting thing here is that this doesn't consider pairs or sets of
    # complementary destinations, so this might deviate from reality
    g = graph['graph']
    def ticket_path_name(f, t):
        return "{} <-> {}".format(f,t)
    def path_to_pairs(path):
        for pairs in zip(path, path[1:]):
            yield pairs

    tickets_paths = {}
    for (ticket_from, ticket_to, points) in graph['tickets']:
        path = nx.shortest_path(g, ticket_from, ticket_to)

        path_key = ticket_path_name(ticket_from, ticket_to)
        tickets_paths[path_key] = path

        #increment number of tickets for each edge in the path
        for (path_from, path_to) in path_to_pairs(path):
            ed = g.get_edge_data(path_from, path_to)
            if 'tickets' not in ed:
                ed['tickets'] = 0
            ed['tickets'] += 1

    #output most important edges overall
    edges = []
    for (from_, to) in g.edges:
        data = g.get_edge_data(from_, to)
        edges.append( [from_, to, data['weight'], data.get('tickets',0) ] )

    df = pd.DataFrame.from_records(edges, columns=["from", "to", "weight", "tickets"])
    df['cost_to_acquire'] = df['weight'] * df['tickets']
    df = df.sort_values(by=['cost_to_acquire', 'tickets', 'from', 'to'], ascending=False)
    df.to_csv(os.path.join(args.output_dir, 'critical_paths.csv'), index=False)

    # now for each destination, output the important edge
    important_paths = []
    for key,path in tickets_paths.iteritems():
        max_edge = None
        max_tickets = -1
        for (from_, to) in path_to_pairs(path):
            data = g.get_edge_data(from_, to)
            if data['tickets'] > max_tickets:
                max_tickets = data['tickets']
                max_edge = (from_, to)

        important_paths.append([key, ticket_path_name(*max_edge), max_tickets])

    df = pd.DataFrame.from_records(important_paths, columns=["ticket", "important path", "tickets"])
    df = df.sort_values(by=['ticket', 'tickets'], ascending=True)
    df.to_csv(os.path.join(args.output_dir, 'ticket_important_paths.csv'), index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze a Ticket to Ride graph')
    parser.add_argument('--graph', '-g', help='map graph to analyze', required=True)
    parser.add_argument('--output_dir', '-o', help='directory to write analysis to', required=True)

    args = parser.parse_args()

    graph = read_graph(args.graph)

    analyze_critical_junctions(args, graph)
