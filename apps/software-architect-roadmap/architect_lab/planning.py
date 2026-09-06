"""Supporting skills: explicit assumptions and deterministic decision calculations."""


def weighted_decision(weights, scores):
    if not weights or any(value < 0 for value in weights.values()) or sum(weights.values()) <= 0:
        raise ValueError("positive total weight required")
    for name, score in scores.items():
        if set(score) != set(weights) or any(not 1 <= x <= 5 for x in score.values()):
            raise ValueError(f"invalid scores for {name}")
    return sorted(((name, sum(weights[k] * score[k] for k in weights) / sum(weights.values()))
                   for name, score in scores.items()), key=lambda x: (-x[1], x[0]))


def pert(optimistic, likely, pessimistic):
    if not 0 <= optimistic <= likely <= pessimistic:
        raise ValueError("require 0 <= optimistic <= likely <= pessimistic")
    return (optimistic + 4 * likely + pessimistic) / 6


def critical_path(tasks):
    """Tasks map names to (duration, dependencies). Detect invalid/cyclic input."""
    visiting, ends, paths = set(), {}, {}

    def visit(name):
        if name in ends:
            return
        if name in visiting:
            raise ValueError("cyclic dependencies")
        if name not in tasks:
            raise ValueError(f"unknown dependency: {name}")
        visiting.add(name)
        duration, dependencies = tasks[name]
        if duration < 0:
            raise ValueError("negative duration")
        for parent in dependencies:
            visit(parent)
        longest = max(dependencies, key=lambda x: ends[x], default=None)
        ends[name] = duration + (ends[longest] if longest else 0)
        paths[name] = (paths[longest] if longest else []) + [name]
        visiting.remove(name)

    for task in tasks:
        visit(task)
    if not tasks:
        return {"duration": 0, "path": []}
    last = max(ends, key=ends.get)
    return {"duration": ends[last], "path": paths[last]}


def validate_raci(rows):
    for activity, roles in rows.items():
        if list(roles.values()).count("A") != 1 or "R" not in roles.values():
            raise ValueError(f"{activity}: need exactly one A and at least one R")
        if any(role not in {"R", "A", "C", "I", "-"} for role in roles.values()):
            raise ValueError("unknown RACI role")
    return True
