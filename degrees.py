import csv
import random
import sys

from util import Node, QueueFrontier, StackFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set(),
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set(),
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    source_frontier = shortest_path_to_kevin(source)
    target_frontier = shortest_path_to_kevin(target)

    if source_frontier == None or target_frontier == None:
        return None

    path = []

    for node in source_frontier.frontier[1:]:
        path.append((node.action, node.state))

    target_frontier.frontier[0].action = target_frontier.frontier[-1].action
    target_frontier.frontier.reverse()

    for node in target_frontier.frontier[1:]:
        path.append((node.action, node.state))

    return path


def shortest_path_to_kevin(source):
    """
    Returns the shortest stack (path) source (actor)
    to Kevin Bacon

    If no possible path, returns None
    """

    """
    The main idea is to find shortest path to kevin.
    Which is possible and only takes Six steps at maximum 
    
    At O(6)
    """
    start = Node(state=source, parent=None, action=None)
    frontier = StackFrontier()
    frontier.add(start)
    path_found = False  # 1

    path = StackFrontier()
    path.add(start)
    explored = set()

    for _ in range(6):
        # first finding path source to kevin
        if frontier.empty():
            return None

        node = frontier.remove()
        if node.state == "102":  # Kevin
            return path

        explored.add(node.state)

        neighbors = list(neighbors_for_person(node.state))
        if not neighbors:
            return None

        for movie_id, star_id in neighbors:
            if star_id == "102":  # kevin
                child = Node(state=star_id, parent=node, action=movie_id)
                frontier.add(child)
                path.add(child)
                path_found = True  # 2

                break
        # if kevin not in neighbors then add any neighbor randomly
        if path_found == False:  # 2
            neighbor_added = False  # 3
            while neighbor_added == False:  # 3
                neighbor = random.choice(neighbors)
                actor = neighbor[1]
                movie = neighbor[0]
                if actor not in explored and not frontier.contains_state(actor):
                    child = Node(state=actor, parent=node, action=movie)
                    frontier.add(child)
                    path.add(child)
                    neighbor_added = True  # 3
    return None


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None

    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
