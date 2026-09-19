from logic_engine import KnowledgeBase
from agent import SearchAgent


def test_forward_chaining():
    kb = KnowledgeBase()
    kb.tell_rule(["TargetVisible", "HasDust"], "SafeToEngage")
    kb.tell_rule(["SafeToEngage", "BloodseekerMissing"], "Retreat")

    kb.clear_facts()
    kb.tell_fact("TargetVisible")
    kb.tell_fact("HasDust")
    kb.forward_chain()
    assert "SafeToEngage" in kb.facts
    assert "Retreat" not in kb.facts

    kb.clear_facts()
    kb.tell_fact("TargetVisible")
    kb.tell_fact("HasDust")
    kb.tell_fact("BloodseekerMissing")
    kb.forward_chain()
    assert "Retreat" in kb.facts


def test_a_star_knowledge_base_filter():
    agent = SearchAgent()
    tile_percepts = {
        (1, 0): {
            "TargetVisible": True,
            "HasDust": True,
            "BloodseekerMissing": True,
        }
    }
    path = agent.a_star_search((0, 0), (2, 0), [], (3, 1), tile_percepts)
    assert (1, 0) in agent.infeasible_tiles
    assert path is None


if __name__ == "__main__":
    test_forward_chaining()
    test_a_star_knowledge_base_filter()
    print("All Logic Engine and A* Knowledge Base tests passed!")
