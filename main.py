import pygame
import random, math, copy
import brain as neural_brain
import numpy as np
import time

SCREEN_WIDTH = 2800
SCREEN_HEIGHT = 1600

class coordinate:
    def __init__(self, x=0, y=0, a=0):
        self.x = x
        self.y = y
        self.a = a

class individuo:
    def __init__(self, type=0):
        self.coord = coordinate()
        self.rays = [-60, -40, -20, +20, +40, +60]
        self.raycasted = []
        self.brain = neural_brain.brain([(6+6+2+1+1), 4, (1+1)])
        self.speed_x = 0
        self.speed_y = 0
        self.accelleration = 0
        self.type = type
        self.energy = 200
        self.creation = time.time()
        self.last_eat = 0
        self.score = 0
    def move_x(self, much):
        self.coord.x = (self.coord.x + much) % SCREEN_WIDTH
    def move_y(self, much):
        self.coord.y = (self.coord.y + much) % SCREEN_HEIGHT

lista_individui = []

for _ in range(50):
    ind = individuo()
    ind.move_x(random.randint(0,+1000))
    ind.move_y(random.randint(0,+1000))
    ind.coord.a = random.randint(0,360)
    lista_individui.append(ind)
for _ in range(90):
    ind = individuo(1)
    ind.move_x(random.randint(0,+1600))
    ind.move_y(random.randint(0,+1600))
    ind.coord.a = random.randint(0,360)
    lista_individui.append(ind)

def disegna_individui():
    #pygame.draw.rect(dis,(0,0,255),[200,50,10,10])
    for individuo in lista_individui:
        color = (255,0,0)
        if(individuo.type == 1):
            color = (0,255,0)
        pygame.draw.circle(window, color, [individuo.coord.x, individuo.coord.y], 10, 0)
        #draw graphical indicator of where is is pointing
        #draw_ray(individuo.coord, 15)

    for individuo in lista_individui:
        individuo.raycasted = []
        search_for = (0, 255, 0, 255)
        if(individuo.type == 1):
            search_for = (255, 0, 0, 255)
        for ray in individuo.rays:
            coord = copy.copy(individuo.coord)
            coord.a = ray + coord.a
            individuo.raycasted.append(raycast(coord, 15, 220, 4, search_for))

def death_ray(start_coord, shift, distance):
    computed_cos = math.cos(math.radians(start_coord.a))
    computed_sin = math.sin(math.radians(start_coord.a))
    victim_coord = False
    for dist in range(distance):
        x = int(start_coord.x + computed_cos * (dist+shift)) % SCREEN_WIDTH
        y = int(start_coord.y + computed_sin * (dist+shift)) % SCREEN_HEIGHT
        if(window.get_at((x,y)) == (0, 255, 0, 255) and victim_coord == False):
            victim_coord = (x,y)
        pygame.draw.rect(window,(0,0,255),[x,y,1,1])
    return victim_coord

def raycast(start_coord, shift, distance, interval, search_for):
    computed_cos = math.cos(math.radians(start_coord.a))
    computed_sin = math.sin(math.radians(start_coord.a))
    dist = shift
    while(dist < distance):
        x = int(start_coord.x + computed_cos * dist) % SCREEN_WIDTH
        y = int(start_coord.y + computed_sin * dist) % SCREEN_HEIGHT
        dist += interval
        #print(window.get_at((x,y)))
        if(window.get_at((x,y)) == search_for):
            return dist
        if(do_show):
            pygame.draw.rect(window,(250,0,0),[x,y,1,1])
    return -400

def compute_brains():
    for individuo in lista_individui:
        input_data = []
        input_data = input_data + individuo.raycasted + individuo.rays
        input_data = input_data + [individuo.speed_x, individuo.speed_y]
        input_data.append(individuo.coord.a)
        input_data.append(individuo.energy)
        output = individuo.brain.compute_output(input_data)
        individuo.accelleration = output[0]
        if(individuo.accelleration > 2):
            individuo.accelleration = 2
        individuo.coord.a += output[1] % 360

#compute the next frame location
#consider accelleration and friction
def make_move():
    for individuo in lista_individui:
        individuo.speed_x += math.cos(math.radians(individuo.coord.a)) * individuo.accelleration
        individuo.speed_y += math.sin(math.radians(individuo.coord.a)) * individuo.accelleration
        individuo.speed_x *= 0.2
        individuo.speed_y *= 0.2
        individuo.coord.x = (individuo.coord.x - individuo.speed_x ) % SCREEN_WIDTH
        individuo.coord.y = (individuo.coord.y - individuo.speed_y ) % SCREEN_HEIGHT

def check_deaths():
    global lista_individui, max_predator_life
    to_delete_indexes = []
    for posizione in range(len(lista_individui)):
        individuo = lista_individui[posizione]
        result = death_ray(individuo.coord, 10, 9)
        if(result != False and individuo.type==0):
            (x,y) = result
            #now check most close
            point1 = np.array((x,y))
            for i in range(len(lista_individui)):
                vittima = lista_individui[i]
                if(vittima.type == 1):
                    point2 = np.array((vittima.coord.x, vittima.coord.y))
                    dist = np.linalg.norm(point1 - point2)
                    if(dist <= 10):
                        individuo.last_eat = 30
                        individuo.energy += 250
                        individuo.score += 1
                        if(individuo.energy > 500):
                            individuo.energy = 500
                        to_delete_indexes.append(i)
                        break
        if(individuo.energy < 0 and individuo.type==0):
            to_delete_indexes.append(posizione)
            if(individuo.score > max_predator_score):
                max_predator_score = elapsed
                best_predator = individuo
                print(max_predator_score)
                for id, node in individuo.brain.nodes.items():
                    print("#",id, " ", node.value)
                print("CONNECTIONS")
                for connection in individuo.brain.connections:
                    print("#",connection.from_id, " -> #", connection.to_id, " ", connection.weight)
            break
    cache_list = []
    for i in range(len(lista_individui)):
        if i not in to_delete_indexes:
            cache_list.append(lista_individui[i])
    lista_individui = cache_list

def compute_resources():
    for individuo in lista_individui:
        if(individuo.type == 0):
            individuo.energy -= 1
        else:
            individuo.energy += 1
        individuo.energy -= abs(individuo.accelleration) * 0.0008
        if(individuo.last_eat > 0):
            individuo.last_eat -= 1

def make_childrens():
    global lista_individui
    nuova_lista = []
    #check for every prey if can have children
    lunghezza = len(lista_individui)
    for il in range(lunghezza):
        individuoo = copy.copy(lista_individui[il])
        if(individuoo.type == 0 and individuoo.energy > 410 and individuoo.last_eat == 0):
            print("energua maggiore")
            nuovo_individuo = individuo(0)
            nuovo_individuo.brain = neural_brain.mutation_of(copy.deepcopy(individuoo.brain))
            nuovo_individuo.rays = copy.deepcopy(individuoo.rays)
            nuovo_individuo.coord = copy.deepcopy(individuoo.coord)
            nuovo_individuo.move_y(random.randint(-50,+50))
            nuovo_individuo.move_x(random.randint(-50,+50))
            nuovo_individuo.move_y(random.randint(-50,+50))
            nuova_lista.append(nuovo_individuo)
            nuova_lista.append(individuoo)
            randomize_rays(nuovo_individuo.rays)
            individuoo.energy = 310
            individuoo.last_eat = 600
            continue
        elif(individuoo.type == 1 and individuoo.energy > 380):
            print("energua maggiore", individuoo.energy)
            nuovo_individuo = individuo(1)
            nuovo_individuo.brain = neural_brain.mutation_of(copy.copy(individuoo.brain))
            nuovo_individuo.coord = copy.copy(individuoo.coord)
            individuoo.energy = 200
            nuova_lista.append(individuoo)
            nuovo_individuo.move_x(random.randint(-50,+50))
            nuovo_individuo.move_y(random.randint(-50,+50))
            randomize_rays(nuovo_individuo.rays)
            nuova_lista.append(nuovo_individuo)
            continue
        else:
            nuova_lista.append(individuoo)
    lista_individui = nuova_lista

def randomize_rays(rays):
    to_randomise = np.random.randint(0, 20)
    if to_randomise >= len(rays)-1:
        return
    if(to_randomise == 0):
        rays[0] = np.random.randint(-360, rays[0])
    elif(to_randomise == 5):
        rays[5] = np.random.randint(360, rays[5])
    else:
        rays[to_randomise] = np.random.randint(rays[to_randomise-1], rays[to_randomise+1])

predatori = 0
max_predator_score = 0
best_predator = None

def many_predators():
    global predatori
    predatori = 0
    for individu in lista_individui:
        if(individu.type == 0):
            predatori += 1
do_show = True
do_fast = False

window=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.update()
pygame.display.set_caption('Snake game by Edureka')
game_over=False
pygame.init()
my_font = pygame.font.SysFont('font.ttf', 30)

while not game_over:
    for event in pygame.event.get():
        #print(event)
        if event.type==pygame.QUIT:
            game_over=True
        elif event.type==pygame.MOUSEMOTION:
            pass
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                do_show = not do_show
            elif event.key == pygame.K_RIGHT:
                do_fast = not do_fast
            #lista_individui[0].coord.x = event.pos[0]
            #lista_individui[0].coord.y = event.pos[1]
    oggetto = pygame.time.Clock()
    if(do_fast):
        oggetto.tick(280)
    else:
        oggetto.tick(40)
    window.fill((255, 255, 255))
    disegna_individui()
    check_deaths()
    compute_brains()
    compute_resources()
    make_move()
    make_childrens()
    many_predators()
    if(predatori == 0): #disabilitare se si vuole più realistico
        lista_individui.append(best_predator)
    text_surface = my_font.render(str(predatori) + ' - ' + str(len(lista_individui)-predatori) + ' - '+ str(len(lista_individui)), False, (0, 0, 0))
    window.blit(text_surface, (40, 10))
    pygame.display.update()
