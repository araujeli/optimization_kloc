class BasicFunctions:
    def __init__(
        self,
    ):
        """
        This class generate a solution using a greedy heuristic.

        Args:
        """

    def swap(self, list_to_change, position_1, position_2):
        data_1 = list_to_change[position_1]
        list_to_change[position_1] = list_to_change[position_2]
        list_to_change[position_2] = data_1
        return list_to_change