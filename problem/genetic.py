from problem.knapsack import KnapsackProblem
import random

class GeneticAlgorithm:
    def __init__(
        self, 
        problem: KnapsackProblem, 
        populationSize, 
        generations, 
        crossoverType, 
        crossoverRate=0.8, 
        mutationRate=0.05
    ):
        self.problem        = problem 
        self.populationSize = populationSize
        self.generations    = generations
        self.crossoverType  = crossoverType
        self.crossoverRate  = crossoverRate
        self.mutationRate   = mutationRate
        self.population     = []
        self.logs           = []

    def initial_population(self):
        self.population = [
            [random.randint(0, item['Max_quantity']) for item in self.problem.items]
            for _ in range(self.populationSize)
        ]

    def evaluate_fitness(self, individual):
        return self.problem.fitness(individual)

    def selection(self, num_choices=3):
        candidates = random.choices(self.population, k=num_choices)
        candidates.sort(key=self.evaluate_fitness, reverse=True)
        return candidates[0]

    def crossover(self, parent1, parent2):
        if self.crossoverType == 'uniform':
            return self.uniform_crossover(parent1, parent2)
        elif self.crossoverType == 'one_point':
            return self.one_point_crossover(parent1, parent2)
        else:
            return parent1, parent2

    def one_point_crossover(self, parent1, parent2):
        if random.random() < self.crossoverRate:
            cut_point = random.randint(1, len(self.problem.items) - 1)
            return (
                parent1[:cut_point] + parent2[cut_point:],
                parent2[:cut_point] + parent1[cut_point:]
            )
        return parent1, parent2

    def uniform_crossover(self, parent1, parent2):
        child1, child2 = [], []
        for gene1, gene2 in zip(parent1, parent2):
            if random.random() < self.crossoverRate:
                child1.append(gene1)
                child2.append(gene2)
            else:
                child1.append(gene2)
                child2.append(gene1)
        return child1, child2

    def mutate(self, individual):
        for i in range(len(individual)):
            if random.random() < self.mutationRate:
                individual[i] = random.randint(0, self.problem.items[i]['Max_quantity'])

    def run(self, log_callback=None):
        self.initial_population()
        population = self.population

        for generation in range(self.generations):
            fitnesses = [self.evaluate_fitness(ind) for ind in population]
            best_fitness     = max(fitnesses)
            avg_fitness      = sum(fitnesses) / len(fitnesses)
            worst_fitness    = min(fitnesses)
            best_individual  = max(population, key=self.evaluate_fitness)

            log = {
                "generation"     : generation + 1,
                "best"           : best_fitness,
                "avg"            : avg_fitness,
                "worst"          : worst_fitness,
                "bestIndividual" : best_individual
            }
            self.logs.append(log)

            if log_callback and (generation + 1) % 10 == 0:
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
            population = new_population[:self.populationSize - 1] + [best_individual]

        return self.logs
