from problem.knapsack import KnapsackProblem
import random
import copy

class GeneticAlgorithm:
    def __init__(
        self, 
        problem: KnapsackProblem, 
        populationSize, 
        generations, 
        crossoverType, 
        selectionType, 
        mutationType,
        crossoverRate=0.8, 
        mutationRate=0.05
    ):
        self.problem        = problem
        self.populationSize = populationSize
        self.generations    = generations
        self.crossoverType  = crossoverType
        self.crossoverRate  = crossoverRate
        self.mutationType = mutationType
        self.selectionType = selectionType
        self.mutationRate   = mutationRate
        self.population     = []
        self.logs           = []

    def initial_population(self):
        self.population = [
            [random.randint(0, item['Max_quantity']) for item in self.problem.items]
            for _ in range(self.populationSize)
        ]
    
    def selection(self, num_choices=3):
        if self.selectionType == 'tournament':
            return self.tournament_selection(num_choices)
        elif self.selectionType == 'random':
            return self.random_selection()
        elif self.selectionType == 'roulette':
            return self.roulette_wheel_selection()
        else:
            raise ValueError("Phương pháp selection không hợp lệ. Chọn 'tournament', 'random' hoặc 'roulette'.")

    def evaluate_fitness(self, individual):
        return self.problem.fitness(individual)

    def tournament_selection(self, num_choices=3):
        candidates = random.choices(self.population, k=num_choices)
        candidates.sort(key=self.evaluate_fitness, reverse=True)
        return candidates[0]

    def random_selection(self):
        return random.choice(self.population)

    def roulette_wheel_selection(self):
        fitness_values = [self.evaluate_fitness(ind) for ind in self.population]
        total_fitness = sum(fitness_values)

        if total_fitness == 0:
            return random.choice(self.population)

        probabilities = [f / total_fitness for f in fitness_values]
        cumulative_probabilities = []
        cumulative = 0
        for p in probabilities:
            cumulative += p
            cumulative_probabilities.append(cumulative)

        r = random.random()
        for i, cumulative_p in enumerate(cumulative_probabilities):
            if r <= cumulative_p:
                return self.population[i]

    def crossover(self, parent1, parent2):
        if self.crossoverType == 'uniform':
            return self.uniform_crossover(parent1, parent2)
        elif self.crossoverType == 'one_point':
            return self.one_point_crossover(parent1, parent2)
        elif self.crossoverType == 'two_points':
            return self.two_points_crossover(parent1, parent2)
        else:
            return parent1, parent2

    def one_point_crossover(self, parent1, parent2):
        if len(self.problem.items) < 2:
        # Không thể cắt nếu có ít hơn 2 gene → giữ nguyên
            return parent1[:], parent2[:]
        if random.random() < self.crossoverRate:
            cut_point = random.randint(1, len(self.problem.items) - 1)
            return (
                parent1[:cut_point] + parent2[cut_point:],
                parent2[:cut_point] + parent1[cut_point:]
            )
        return parent1, parent2

    def two_points_crossover(self, parent1, parent2):
        if random.random() < self.crossoverRate:
            point1 = random.randint(1, len(parent1) - 2)
            point2 = random.randint(point1 + 1, len(parent1) - 1)
            child1 = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
            child2 = parent2[:point1] + parent1[point1:point2] + parent2[point2:]
            return child1, child2
        return parent1, parent2

    def uniform_crossover(self, parent1, parent2):
        if random.random() > self.crossoverRate:
            return parent1, parent2  # không crossover thì giữ nguyên
            
        child1, child2 = [], []
        for gene1, gene2 in zip(parent1, parent2):
            if random.random() < 0.5:  # swap probability
                child1.append(gene2)
                child2.append(gene1)
            else:
                child1.append(gene1)
                child2.append(gene2)
        return child1, child2

    def mutate(self, individual):
        if self.mutationType == 'uniform':
            return self.uniform_mutate(individual)
        elif self.mutationType == 'scramble':
            return self.scramble_mutate(individual)
        else:
            return individual

    def uniform_mutate(self, individual):
        for i in range(len(individual)):
            if random.random() < self.mutationRate:
                individual[i] = random.randint(0, self.problem.items[i]['Max_quantity'])
        return individual

    def scramble_mutate(self, individual):
        if random.random() < self.mutationRate:
            start = random.randint(0, len(individual) - 2)
            end = random.randint(start + 1, len(individual) - 1)
            segment = individual[start:end + 1]
            random.shuffle(segment)
            individual[start:end + 1] = segment
        return individual

    def run(self, log_callback=None):
        self.initial_population()
        population = self.population

        for generation in range(self.generations):
            fitnesses = [self.evaluate_fitness(ind) for ind in population]
            best_fitness     = max(fitnesses)
            avg_fitness      = sum(fitnesses) / len(fitnesses)
            worst_fitness    = min(fitnesses)
            best_individual = copy.deepcopy(max(population, key=self.evaluate_fitness))

            log = {
                "generation"     : generation + 1,
                "best"           : best_fitness,
                "avg"            : avg_fitness,
                "worst"          : worst_fitness,
                "bestIndividual" : best_individual
            }
            self.logs.append(log)

            if log_callback and (generation + 1) % 10 == 0: #callback này giống như 1 cách để gọi cập nhật biểu đồ song song với chạy thuật toán 
                log_callback(log)

            new_population = []
            while len(new_population) < self.populationSize:
                parent1 = self.selection()
                parent2 = self.selection()
                child1, child2 = self.crossover(parent1, parent2)
                self.mutate(child1)
                self.mutate(child2)
                new_population.extend([child1, child2])

            # Giữ lại best cá thể để elitism
            new_population = new_population[:self.populationSize - 1]

            # Thêm cá thể tốt nhất trở lại quần thể
            self.population = new_population + [best_individual]
            population = self.population  # Cập nhật lại population cho thế hệ sau

            # new_population = new_population[:self.populationSize]
            # self.population = new_population
            # population = self.population  

        return self.logs