# Ticket to Ride Graph Analyzer

This script loads a given file and performs graph analysis relevant to Ticket to Ride.

# Usage
Run `make` in the directory and install whatever relevant packages you need.

# Output
critical_paths.csv - the top rail links that connect the most ticket cards, as
computed by adding up all tickets that take the shortest path through the
link.

ticket_important_paths.csv - The most important path for each destination,
given by the above critical_paths.
