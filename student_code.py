import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact])
        ####################################################
        # Student code goes here
        if isinstance(fact, Fact):
            if fact not in self.facts:
                return 
            else:
                Index = self.facts.index(fact)
                fact = self.facts[Index]
        elif isinstance(fact,Rule):
            if fact not in self.rules:
                return
            else:
                Index = self.rules.index(fact)
                fact = self.rules[Index]

        if len(fact.supported_by) == 0:
            if isinstance(fact, Fact):
                self.facts.remove(fact)
            elif isinstance(fact,Rule):
                if fact.asserted:
                    return
                else:
                    self.rules.remove(fact)
                
            for i in fact.supports_facts:
                for j in i.supported_by:
                    if fact in j:
                        i.supported_by.remove(j)
                self.kb_retract(i)

            for i in fact.supports_rules:
                for j in i.supported_by:
                    if fact in j:
                        i.supported_by.remove(j)
                self.kb_retract(i)
            
                            
                    
                    
                

class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing            
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Student code goes here
        bind = match(fact.statement, rule.lhs[0])
        if bind:
            if len(rule.lhs) == 1:
                Output_statement = instantiate(rule.rhs, bind)
                Output_fact = Fact(Output_statement)
                if Output_fact in kb.facts:
                    index = kb.facts.index(Output_fact)
                    Output_fact = kb.facts[index]
                if [fact, rule] not in Output_fact.supported_by:
                    Output_fact.supported_by.append([fact,rule])
                fact.supports_facts.append(Output_fact)
                rule.supports_facts.append(Output_fact)
                if Output_fact not in kb.facts:
                    kb.kb_assert(Output_fact)
            else:
                lhs_list = []
                for stateoflhs in rule.lhs[1:]:
                    lhs_list.append(instantiate(stateoflhs, bind))
                rhs_list = instantiate(rule.rhs, bind)
                Output_rule = Rule([lhs_list, rhs_list])
                if Output_rule in kb.rules:
                    index = kb.rules.index(Output_rule)
                    Output_rule = kb.rules[index]
                if [fact, rule] not in Output_rule.supported_by:
                    Output_rule.supported_by.append([fact,rule])
                fact.supports_rules.append(Output_rule)
                rule.supports_rules.append(Output_rule)
                if Output_rule not in kb.rules:
                    kb.kb_assert(Output_rule)                
                
            
