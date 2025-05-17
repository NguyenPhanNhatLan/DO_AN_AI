from problem.knapsack import KnapsackProblem
import random
import matplotlib.pyplot as plt

class GeneticAlgorithm:
    def __init__(self, problem : KnapsackProblem, populationSize, generations, crossoverType, crossoverRate = 0.8,mutationRate = 0.05):
        self.problem = problem 
        self.populationSize = populationSize
        self.generations = generations
        self.crossoverType = crossoverType
        self.crossoverRate = crossoverRate
        self.mutationRate = mutationRate
        self.population = []
        self.logs = []

    def InitialPopulation(self):   # khởi tạo quần thể ban đầu, mỗi cá thể là số các món đồ được chọn
        for _ in range(self.populationSize):
            individual = []
            for item in self.problem.items:
                selected = random.randint(0, item['Max_quantity'])
                individual.append(selected)
            self.population.append(individual)

    def Selection(self,num_choices=3): # chọn k cá thể ngẫu nhiên từ tập --> tính fitness và chọn cá thể có fitness cao nhất
        selections = random.choices(self.population,k=num_choices)
        selections.sort(key = self.EvaluateFitness, reverse= True)
        return selections[0]
   
    def RouletteWheelSelection(self):
        pass

    def RankSelection():
        pass

    def EvaluateFitness(self, individual): #
        return self.problem.fitness(individual)
    
    def Crossover(self, parent1, parent2):
        if self.crossoverType == 'uniform':
            child1, child2 = self.UniformCrossover(parent1, parent2)
            return child1, child2

        if self.crossoverType == 'one_point':
            return self.OnePointCrossover(parent1,parent2)
        else: 
            raise ValueError("Chọn 'uniform' hoặc 'one_point")

    def OnePointCrossover(self,parent1, parent2):
        if random.random() < self.crossoverRate:
            point = random.randint(1, len(self.problem.items)-1)
            child1 = parent1[:point] + parent2[point:]
            child2 = parent2[:point] + parent1[point:]
            return child1, child2
        return parent1, parent2
    
    def UniformCrossover(self, parent1, parent2):
        child1 = []
        child2 = []
        for gen1, gen2 in zip(parent1, parent2):
            if random.random() < self.crossoverRate:
                child1.append(gen1)
                child2.append(gen2)
            else:
                child1.append(gen2)
                child2.append(gen1)
        return child1,child2

    def Mutate(self, individual):
        for i in range(len(individual)):
            if random.random() < self.mutationRate:
                individual[i] = random.randint(0, self.problem.items[i]['Max_quantity'])


    def run(self):
        self.InitialPopulation()
        population = self.population
        for generation in range(self.generations):
            fitnesses = [self.EvaluateFitness(individual) for individual in population] #fitness của các cá thể trong quần thể hiện tại 
            bestFitness = max(fitnesses)
            avgFitness = sum(fitnesses)/len(fitnesses)
            worstFitness = min(fitnesses)
            self.logs.append({"generation" : generation, 'best': bestFitness, 'avg': avgFitness, 'worst': worstFitness})
            bestIndividual = max(population, key= self.EvaluateFitness)
            new_population = []
            while len(new_population) < self.populationSize:
                parent1 = self.Selection(num_choices=3) #chọn cha mẹ 
                parent2 = self.Selection(num_choices=3)
                child1, child2 = self.Crossover(parent1, parent2)
                self.Mutate(child1) # đột biến các cá thể con được sinh ra với xác suất  cố định 
                self.Mutate(child2)
                new_population.extend([child1,child2])
            population = new_population[:self.populationSize - 1] + [bestIndividual]
        return self.logs
    
# products = [
#     {"name": "Laptop", "weight": 3.0, "value": 1000.0, "Max_quantity": 1},
#     {"name": "Smartphone", "weight": 0.5, "value": 700.0, "Max_quantity": 2},
#     {"name": "Book", "weight": 1.0, "value": 40.0, "Max_quantity": 5},
#     {"name": "Headphones", "weight": 0.3, "value": 150.0, "Max_quantity": 3},
#     {"name": "Camera", "weight": 1.5, "value": 600.0, "Max_quantity": 1}
# ]

# problem = KnapsackProblem(products,10)
# ga = GeneticAlgorithm(problem= problem, populationSize= 50,generations = 100,crossoverType='uniform', mutationRate= 0.05)
# solver = ga.run()
# for item in solver:
#     print(item)

# generations = [log["generation"] for log in solver]
# best_fitness = [log["best"] for log in solver]
# avg_fitness = [log["avg"] for log in solver]
# worst_fitness = [log["worst"] for log in solver]

# plt.figure(figsize=(10, 6))
# plt.plot(generations, best_fitness, label="Best Fitness", color='green')
# plt.plot(generations, avg_fitness, label="Average Fitness", color='blue')
# plt.plot(generations, worst_fitness, label="Worst Fitness", color='red')

# plt.title("Tiến hoá qua các thế hệ")
# plt.xlabel("Thế hệ")
# plt.ylabel("Giá trị Fitness")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()









