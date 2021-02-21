from collections import defaultdict
from typing import List

from dpmModule.kernel.core import (
    BuffSkillWrapper,
    SummonSkillWrapper,
    GraphElement,
    AbstractSkillWrapper,
    utilities,
)
from dpmModule.kernel.policy import AbstractRule, NameIndexedGraph


class ConditionRule(AbstractRule):
    """
    For both GraphElements A,B and check_function, use A if check_function(B) returns True.
    두 GraphElement A,B와 check_function에 대해, check_function(B)가 True를 리턴하면 A를 사용합니다.
    """

    def __init__(self, state_element, checking_element, check_function) -> None:
        self._state_element_name = state_element
        self._checking_element_name = checking_element
        self._check_function = check_function

    def get_related_elements(
        self, reference_graph: NameIndexedGraph
    ) -> List[GraphElement]:
        return [reference_graph.get_element(self._state_element_name)]

    def check(
        self,
        caller: AbstractSkillWrapper,
        reference_graph: NameIndexedGraph,
        context=None,
    ) -> bool:
        return self._check_function(
            reference_graph.get_element(self._checking_element_name)
        )


class ComplexConditionRule(AbstractRule):
    """
    For GraphElement A, List[GraphElement] B and check_function, use A if check_function(A, *B) returns True.
    GraphElement A, List[GraphElement] B와 check_function에 대해, check_function(A, *B)가 True를 리턴하면 A를 사용합니다.
    """

    def __init__(
        self, state_element: str, checking_elements: List[str], check_function
    ) -> None:
        self._state_element_name = state_element
        self._checking_element_names = checking_elements
        self._check_function = check_function

    def get_related_elements(
        self, reference_graph: NameIndexedGraph
    ) -> List[GraphElement]:
        return [reference_graph.get_element(self._state_element_name)]

    def check(
        self,
        caller: AbstractSkillWrapper,
        reference_graph: NameIndexedGraph,
        context=None,
    ) -> bool:
        return self._check_function(
            caller,
            *[
                reference_graph.get_element(name)
                for name in self._checking_element_names
            ],
        )


class UniquenessRule(AbstractRule):
    """
    If the given element is not on, use is prohibited.
    주어진 Element가 on 상태가 아니면 사용을 금지합니다.
    """

    def get_related_elements(
        self, reference_graph: NameIndexedGraph
    ) -> List[GraphElement]:
        return reference_graph.filter_elements(
            lambda x: isinstance(x, BuffSkillWrapper)
        ) + reference_graph.filter_elements(lambda x: isinstance(x, SummonSkillWrapper))

    def check(
        self,
        caller: AbstractSkillWrapper,
        reference_graph: NameIndexedGraph,
        context=None,
    ) -> bool:
        if caller.uniqueFlag:
            return not caller.is_active()
        else:
            return True


class ConcurrentRunRule(AbstractRule):
    """
    For two GraphElements A and B, it is forced to use only when A is using B.
    두 GraphElement A,B에 대해, A가 B를 사용중일 때만 사용하도록 강제합니다.
    """

    def __init__(self, state_element: str, checking_element: str, **kwargs):
        self._state_element_name: str = utilities.skill_name_by_lang(state_element, kwargs.get('lang'))
        self._checking_element_name: str = utilities.skill_name_by_lang(checking_element, kwargs.get('lang'))

    def get_related_elements(
        self, reference_graph: NameIndexedGraph
    ) -> List[GraphElement]:
        return [reference_graph.get_element(self._state_element_name)]

    def check(
        self,
        caller: AbstractSkillWrapper,
        reference_graph: NameIndexedGraph,
        context=None,
    ) -> bool:
        return reference_graph.get_element(self._checking_element_name).is_active()


class ReservationRule(AbstractRule):
    """
    For two GraphElements A,B, force A to use only when B is available.
    두 GraphElement A,B에 대해, A가 B가 사용가능할 때만 사용하도록 강제합니다.
    """

    def __init__(self, state_element: str, checking_element: str, **kwargs):
        self._state_element_name: str = utilities.skill_name_by_lang(state_element, kwargs.get('lang'))
        self._checking_element_name: str = utilities.skill_name_by_lang(checking_element, kwargs.get('lang'))

    def get_related_elements(
        self, reference_graph: NameIndexedGraph
    ) -> List[GraphElement]:
        return [reference_graph.get_element(self._state_element_name)]

    def check(
        self,
        caller: AbstractSkillWrapper,
        reference_graph: NameIndexedGraph,
        context=None,
    ) -> bool:
        return reference_graph.get_element(self._checking_element_name).is_usable()


class SynchronizeRule(AbstractRule):
    """
    When B is on, A can be used when the remaining time of B (buff or minion) is more than time(ms) (direction=1) / less than (direction=-1). If B is off, you can use A.
    B가 켜져있다면, B(버프 또는 소환수) 의 남은 시간이 time(ms) 이상(direction=1) / 이하(direction=-1) 일 때 A를 사용할 수 있습니다. B가 꺼져있다면, A를 사용할 수 있습니다.
    """

    def __init__(
        self, target_element: str, timer_element: str, time: float, direction: int = 1
    ):
        self._target_element = target_element
        self._timer_element = timer_element
        self.time: float = time
        self.direction: int = direction

    def get_related_elements(self, reference_graph) -> List[GraphElement]:
        return [reference_graph.get_element(self._target_element)]

    def check(
        self,
        caller: AbstractSkillWrapper,
        reference_graph: NameIndexedGraph,
        context=None,
    ) -> bool:
        timer: AbstractSkillWrapper = reference_graph.get_element(self._timer_element)
        if not timer.is_not_active():
            if not timer.is_time_left(self.time, self.direction):
                if not timer.is_time_left(caller.skill.cooltime, 1):
                    return False
        return True


class MutualRule(AbstractRule):
    """
    Avoid using A when B is available.
    A를 B가 사용 가능할 때는 사용하지 않도록 합니다.
    """

    def __init__(self, target_element: str, state_element: str):
        self._target_element_name: str = target_element
        self._state_element_name: str = state_element

    def get_related_elements(
        self, reference_graph: NameIndexedGraph
    ) -> List[GraphElement]:
        return [reference_graph.get_element(self._target_element_name)]

    def check(
        self,
        caller: AbstractSkillWrapper,
        reference_graph: NameIndexedGraph,
        context=None,
    ) -> bool:
        if not reference_graph.get_element(self._state_element_name).is_usable():
            return True
        return False


class InactiveRule(AbstractRule):
    """
    Avoid using A when B is being used.
    A를 B가 사용되고 있을 때는 사용하지 않도록 합니다.
    """

    def __init__(self, target_element: str, state_element: str, **kwargs):
        self._target_element_name: str = utilities.skill_name_by_lang(target_element, kwargs.get('lang'))
        self._state_element_name: str = utilities.skill_name_by_lang(state_element, kwargs.get('lang'))

    def get_related_elements(
        self, reference_graph: NameIndexedGraph
    ) -> List[GraphElement]:
        return [reference_graph.get_element(self._target_element_name)]

    def check(
        self,
        caller: AbstractSkillWrapper,
        reference_graph: NameIndexedGraph,
        context=None,
    ) -> bool:
        return reference_graph.get_element(self._state_element_name).is_not_active()


class DisableRule(AbstractRule):
    """
    Disable the use of the given GraphElement.
    주어진 GraphElement를 사용하지 못하도록 합니다.
    """

    def __init__(self, target_element: str):
        self.target_element = target_element

    def get_related_elements(self, reference_graph: NameIndexedGraph):
        return [reference_graph.get_element(self.target_element)]

    def check(
        self,
        caller: AbstractSkillWrapper,
        reference_graph: NameIndexedGraph,
        context=None,
    ) -> bool:
        return False


class RuleSet(defaultdict):
    def __init__(self) -> None:
        super(RuleSet, self).__init__(list)

    BASE = "RuleSet.BASE"
    DENSE = "RuleSet.DENSE"
    OPTIMISTIC = "RuleSet.OPTIMISTIC"
    PESSIMISTIC = "RuleSet.PESSIMISTIC"
    CONFIDENT = "RuleSet.CONFIDENT"

    def add_rule(self, rule: AbstractRule, tag: str) -> bool:
        self[tag].append(rule)
        return True

    def get_rules(self, tag: str) -> List[AbstractRule]:
        return list(self[tag])
