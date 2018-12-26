# Ticket to Ride Graph Analyzer

This script loads a given file and performs graph analysis relevant to Ticket to Ride.

# Usage
Run `make` in the directory and install whatever relevant packages you need.

# Output
critical_paths.csv - the top rail links that connect the most ticket cards, as
computed by adding up all tickets that take the shortest path through the
link. Each link is weighted by the probability of getting the cards to complete
this path. Lower weights are cheaper, where 0 weight is a single card paths.
The cost_per_ticket field gives cost divided by the number of tickets that pass
through that link.

ticket_important_paths.csv - The most important path for each destination,
given by the above critical_paths and weighted shorted paths.

# Data Sources
https://boardgames.stackexchange.com/questions/8637/where-can-i-find-an-exhaustive-inventory-of-cards-in-ticket-to-ride
https://boardgamegeek.com/image/299000/ticket-ride
