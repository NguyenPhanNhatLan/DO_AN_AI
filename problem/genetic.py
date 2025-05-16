from knapsack import KnapsackProblem
import random

class GeneticAlgorithm:
    def __init__(self, problem : KnapsackProblem, populationSize, generations, crossoverRate=0.8, mutationRate = 0.05):
        self.problem = problem 
        self.populationSize = populationSize
        self.generations = generations
        self.crossoverRate = crossoverRate
        self.mutationRate = mutationRate
        self.population = []
        self.logs = []

    def initialPopulation(self):   
        for _ in range(self.populationSize):
            individual = []
            for item in self.problem.items:
                selected = random.randint(0, item['Max_quantity'])
                individual.append(selected)
            self.population.append(individual)

    def selection(self,num_choices=3):
        selections = random.choices(self.population,k=num_choices)
        selections.sort(key = self.evaluateFitness, reverse= True)
        return selections[0]

    def evaluateFitness(self, individual): #
        return self.problem.fitness(individual)
    

    def crossover(self,parent1, parent2):
        if random.random() < self.crossoverRate:
            point = random.randint(1, len(self.problem.items)-1)
            firstChild = parent1[:point] + parent2[point:]
            secondChild = parent2[:point] + parent1[point:]
            return firstChild, secondChild
        return parent1, parent2
    def mutate(self, individual):
        for i in range(len(individual)):
            if random.random() < self.mutationRate:
                individual[i] = random.randint(0, self.problem.items[i]['Max_quantity'])

    def run(self):
        self.initialPopulation()
        population = self.population
        for generation in range(self.generations):
            fitnesses = [self.evaluateFitness(individual) for individual in population]
            bestFitness = max(fitnesses)
            avgFitness = sum(fitnesses)/len(fitnesses)
            worstFitness = min(fitnesses)
            self.logs.append({"generation": generation, "best": bestFitness, "average": avgFitness, "worst": worstFitness})

            new_population = []
            while len(new_population) < self.populationSize:
                parent1 = self.selection(num_choices=3)
                parent2 = self.selection(num_choices=3)
                child1, child2 = self.crossover(parent1, parent2)
                self.mutate(child1)
                self.mutate(child2)
                new_population.extend([child1,child2])
            population = new_population[:self.populationSize]

        return self.logs









