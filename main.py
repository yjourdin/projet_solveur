"""main.py"""

from itertools import combinations, product
from typing import (
    Callable,
    Collection,
    Iterable,
    KeysView,
    Literal,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
    overload,
)


IntDomain = MutableSet[int]
EncodingDomain = MutableSet[Tuple[int]]
Domain = Union[IntDomain, EncodingDomain]

Variable = str


class Constraint:
    """A binary constraint"""

    def __init__(
        self,
        variable_1: Variable,
        variable_2: Variable,
        valid_tuples: MutableSet[
            Tuple[Union[int, Sequence[int]], Union[int, Sequence[int]]]
        ],
    ) -> None:
        self.variables = (variable_1, variable_2)
        self.valid_tuples = valid_tuples


class CSP:
    """A Constraint Satisfactiony Problem"""

    def __init__(self) -> None:
        self.primary_variables: MutableSet[Variable] = set()
        self.domains: MutableMapping[Variable, Domain] = {}
        self.constraints: MutableSequence[Constraint] = []
        self.encoding_variables_count: int = 0

    def variables(self) -> KeysView[Variable]:
        """Return all the variables used in the CSP

        Returns:
            KeysView[Variable]: Variables used in the CSP
        """
        return self.domains.keys()

    def constraints_concerning_variable(
        self, variable: Variable
    ) -> MutableSequence[Constraint]:
        """Return the constraints using a specific variable

        Args:
            variable (Variable): Variable concerned

        Returns:
            MutableSequence[Constraint]: Constraints using the variable
        """
        result = []
        for constraint in self.constraints:
            if variable in constraint.variables:
                result.append(constraint)
        return result

    def variable_with_minimal_domain(self) -> Variable:
        """Return the variable with the minimal domain

        Returns:
            Variable: Variable with the minimal domain
        """
        return min(self.domains.keys(), key=lambda k: len(self.domains[k]))

    def variable_most_constrained(self) -> Variable:
        """Return the variable the most constrained

        Returns:
            Variable: Variable the most constrained
        """
        return max(
            self.variables(), key=lambda v: len(self.constraints_concerning_variable(v))
        )

    def add_variable(self, name: str, domain: Iterable[int]) -> None:
        """Add a variable into the CSP

        Args:
            name (str): Name of the variable
            domain (Iterable[int]): Domain of the variable
        """
        self.primary_variables.add(name)
        self.domains.update({name: set(domain)})

    def add_variables(self, names: Iterable[str], domain: Iterable[int]) -> None:
        """Add variables into the CSP

        Args:
            names (Iterable[str]): Names of the variables
            domain (Iterable[int]): Domain of the variables
        """
        for name in names:
            self.add_variable(name, domain)

    def __add_binary_extensional_constraint(
        self,
        variable_1: Variable,
        variable_2: Variable,
        valid_tuples: Iterable[Tuple[int, int]],
    ) -> None:
        """Add a binary constraint with valid tuples

        Args:
            variable_1 (str): Name of the first variable
            variable_2 (str): Name of the second variable
            valid_tuples (Iterable[Tuple[int, int]]): Tuples of values
                for the variables which satisfy the constraint
        """
        constraint = Constraint(variable_1, variable_2, set(valid_tuples))
        self.constraints.append(constraint)

    def __add_binary_constraint_from_function(
        self,
        variable_1: Variable,
        variable_2: Variable,
        function: Callable[[int, int], bool],
    ) -> None:
        """Add a binary constraint with a truth function

        Args:
            variable_1 (Variable): Name of the first variable
            variable_2 (Variable): Name of the second variable
            function (Callable[[int, int], bool]): Function which return
                if the values for the variables satisfy the constraint
        """
        tuples = product(
            cast(IntDomain, self.domains[variable_1]),
            cast(IntDomain, self.domains[variable_2]),
        )
        valid_tuples = {tuple for tuple in tuples if function(*tuple)}
        self.__add_binary_extensional_constraint(variable_1, variable_2, valid_tuples)

    def __add_extensional_constraint(
        self, variables: Collection[Variable], valid_tuples: Iterable[Sequence[int]]
    ) -> None:
        """Add a constraint with valid tuples

        Args:
            variables (Collection[Variable]): Names of the variables
            valid_tuples (Iterable[Sequence[int]]): Tuples of values
                for the variables which satisfy the constraint
        """
        self.encoding_variables_count += 1
        encoding_variable = "X" + str(self.encoding_variables_count)
        self.domains.update(
            {encoding_variable: cast(EncodingDomain, set(valid_tuples))}
        )
        for i, variable in enumerate(variables):
            valid_pairs: MutableSet = set()
            for valid_tuple in valid_tuples:
                valid_pairs.add((valid_tuple[i], valid_tuple))
            constraint = Constraint(variable, encoding_variable, valid_pairs)
            self.constraints.append(constraint)

    def __add_constraint_from_function(
        self,
        variables: Collection[Variable],
        function: Callable[[*Tuple[int, ...]], bool],
    ) -> None:
        """Add a constraint with a truth function

        Args:
            variables (Collection[Variable]): Names of the variables
            function (Callable[..., bool]): Function which return
                if the values for the variables satisfy the constraint
        """
        tuples = product(*[self.domains[v] for v in variables])
        valid_tuples = {tuple for tuple in tuples if function(*tuple)}
        self.__add_extensional_constraint(variables, valid_tuples)

    @overload
    def add_constraint(
        self,
        variables: Tuple[Variable, Variable],
        truth_table: Iterable[Tuple[int, int]],
    ) -> None:
        ...

    @overload
    def add_constraint(
        self,
        variables: Tuple[Variable, Variable],
        truth_table: Callable[[int, int], bool],
    ) -> None:
        ...

    @overload
    def add_constraint(
        self,
        variables: Collection[Variable],
        truth_table: Iterable[Sequence[int]],
    ) -> None:
        ...

    @overload
    def add_constraint(
        self,
        variables: Collection[Variable],
        truth_table: Callable[[*Tuple[int, ...]], bool],
    ) -> None:
        ...

    def add_constraint(
        self,
        variables: Collection[Variable],
        truth_table: Union[Iterable[Sequence[int]], Callable[[*Tuple[int, ...]], bool]],
    ) -> None:
        """Add a constraint into the CSP

        Args:
            variables (Collection[Variable]): Names of the variables
            truth_table (Union[Iterable[Sequence[int]], Callable[[): _description_

        Raises:
            AttributeError: Valid tuples must be a subset of cartesian product of variables domains
            AttributeError: Valid tuples must contain integers
            AttributeError: Size of valid tuples must match the number of variables used
            AttributeError: Variables used in constraint must be first added into the CSP
            AttributeError: Variables must be strings
        """
        if all((isinstance(x, Variable) for x in variables)):
            if set(variables) <= self.primary_variables:
                N = len(variables)
                if isinstance(truth_table, Iterable):
                    if all((x == N for x in map(len, truth_table))):
                        if all(
                            isinstance(x[0], int) & isinstance(x[1], int)
                            for x in truth_table
                        ):
                            if set(truth_table) <= set(
                                product(*[self.domains[v] for v in variables])
                            ):
                                if N == 2:
                                    self.__add_binary_extensional_constraint(
                                        *cast(Tuple[Variable, Variable], variables),
                                        cast(Iterable[Tuple[int, int]], truth_table)
                                    )
                                else:
                                    self.__add_extensional_constraint(
                                        cast(Collection[Variable], variables),
                                        cast(Iterable[Sequence[int]], truth_table),
                                    )
                            else:
                                raise AttributeError(
                                    "Valid tuples must be a subset of cartesian product of variables domains"
                                )
                        else:
                            raise AttributeError("Valid tuples must contain integers")
                    else:
                        raise AttributeError(
                            "Size of valid tuples must match the number of variables used"
                        )
                elif isinstance(truth_table, Callable):
                    if N == 2:
                        self.__add_binary_constraint_from_function(
                            *cast(Tuple[Variable, Variable], variables),
                            cast(Callable[[int, int], bool], truth_table)
                        )
                    else:
                        self.__add_constraint_from_function(
                            cast(Collection[Variable], variables),
                            cast(Callable[[*Tuple[int, ...]], bool], truth_table),
                        )
            else:
                raise AttributeError(
                    "Variables used in constraint must be first added into the CSP"
                )
        else:
            raise AttributeError("Variables must be strings")

    def diff(self, variables: Iterable[Variable]) -> None:
        """Add a constraint to enforce that variables specified have different values

        Args:
            variables (Iterable[Variable]): Names of the variables

        Raises:
            AttributeError: Variables used in constraint must be first added into the CSP
        """
        if set(variables) <= self.primary_variables:
            for pair in combinations(variables, 2):
                valid_tuples = {
                    (value1, value2)
                    for value1 in cast(IntDomain, self.domains[pair[0]])
                    for value2 in cast(IntDomain, self.domains[pair[1]])
                    if value1 != value2
                }
                self.__add_binary_extensional_constraint(*pair, valid_tuples)
        else:
            raise AttributeError(
                "Variables used in constraint must be first added into the CSP"
            )

    def all_diff(self) -> None:
        """Add the allDifferent constraint"""
        self.diff(self.primary_variables)

    def weighted_sum(
        self,
        variables: Optional[Collection[Variable]] = None,
        weights: Optional[Sequence[float]] = None,
        operator: Literal["<", "=", ">"] = "=",
        value: float = 1,
    ):
        """Add a weighted sum constraint

        Args:
            variables (Optional[Collection[Variable]], optional): Names of the variables. Defaults to None.
            weights (Optional[Sequence[float]], optional): Weights in the sum. Defaults to None.
            operator (Literal[, optional): Operator to compare the sum to a value. Defaults to "=".
            value (float, optional): The value to compare the sum with. Defaults to 1.

        Raises:
            AttributeError: Variables and Weights must have the same length
        """
        if variables is None:
            variables = self.primary_variables
        N = len(variables)
        if weights is None:
            weights = [1] * N
        if len(variables) == len(weights):
            possible_tuples = product(*[self.domains[v] for v in variables])
            valid_tuples = set()
            for possible_tuple in possible_tuples:
                s = sum((weights[i] * possible_tuple[i] for i in range(N)))
                if operator == "<":
                    if s < value:
                        valid_tuples.add(possible_tuple)
                elif operator == "=":
                    if s == value:
                        valid_tuples.add(possible_tuple)
                else:
                    if s > value:
                        valid_tuples.add(possible_tuple)
            self.__add_extensional_constraint(variables, valid_tuples)
        else:
            raise AttributeError("Variables and Weights must have the same length")

    def backtrack(
        self,
        variable_choice_strategy: Literal[
            "lexicographic",
            "random",
            "domain",
            "constraint",
            "dynamic-constraint",
            "bound",
            "impact",
        ] = "lexicographic",
        value_choice_strategy: Literal[
            "random", "support", "less-filtering"
        ] = "random",
    ):
        """Backtrack algorithm

        Args:
            variable_choice_strategy (Literal[
                "lexicographic",
                "random",
                "domain",
                "constraint",
                "dynamic-constraint",
                "bound",
                "impact"): Strategy used to choose the next variable. Defaults to "lexicographic".
            value_choice_strategy (Literal[
                "random",
                "support",
                "less-filtering"): Strategy used to choose the next value. Defaults to "random".
        """
        pass
