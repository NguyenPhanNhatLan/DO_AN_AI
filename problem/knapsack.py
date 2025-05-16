class KnapsackProblem:
    def __init__(self, items, capacity):
        self.items = items
        self.capacity = capacity

    def fitness(self, individual):
        total_weight = 0
        total_value = 0
        for quantity, item in zip(individual, self.items):
            total_weight += quantity*item['weight']
            total_value += quantity*item['value']
        if total_weight > self.capacity:
            return 0
        return total_value         
      

     

