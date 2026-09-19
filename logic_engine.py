class KnowledgeBase:
    """Simple propositional Knowledge Base with forward chaining."""

    def __init__(self):
        self.facts = set()
        self.rules = []

    def tell_fact(self, fact: str):
        self.facts.add(fact)

    def tell_rule(self, premise_list, conclusion: str):
        self.rules.append((list(premise_list), conclusion))

    def clear_facts(self):
        self.facts.clear()

    def forward_chain(self):
        """Apply rules repeatedly until no new facts can be derived."""
        new_facts_added = True
        while new_facts_added:
            new_facts_added = False
            for premises, conclusion in self.rules:
                if conclusion not in self.facts and all(p in self.facts for p in premises):
                    self.facts.add(conclusion)
                    new_facts_added = True
        return self.facts
