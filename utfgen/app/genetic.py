import datetime
import six
import sys
sys.modules['sklearn.externals.six'] = six
import mlrose
import random
from collections import defaultdict
from collections import Counter

from .models import Disciplina, ProfessorHorario, Professor

population_size = 10
mutation_prob = 0.1
max_iterations = 500
global_population = []
allowed_schedule = ["7:30:00", "8:20:00", "9:10:00", "10:20:00", "11:10:00", "13:00:00", "13:50:00", "14:40:00", "15:50:00", "16:40:00", "19:00:00", "19:50:00"]
professor_availability = []
professor_list = []
subject_list = []

def callGenetic():
    # population = initialize_individual()
    global global_population
    global professor_availability
    global professor_list
    global subject_list

    professor_availability = ProfessorHorario.objects.all()
    professor_list = Professor.objects.all()
    subject_list = Disciplina.objects.all()
    global_population = initialize_individual([1,1,1,1,1,1, 1, 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])

    best_state = genetic_algorithm()
    print(list(best_state))

    return refresh_grade(global_population, list(best_state))

def genetic_algorithm():
    fitness = mlrose.CustomFitness(fitness_function)

    problem = mlrose.DiscreteOpt(length=25, fitness_fn=fitness, maximize=False, max_val=(len(allowed_schedule)-1))

    best_state, best_fitness = mlrose.genetic_alg(problem, pop_size=population_size, mutation_prob=mutation_prob, max_attempts=max_iterations)

    return best_state

def initialize_individual(timeList):
    periods = 4  # Número de períodos
    max_courses_per_period = 10  # Número máximo de disciplinas por período

    individual = [[] for _ in range(periods)]  # Lista de listas para os períodos

    # Percorre os períodos
    for period in range(periods):
        # Lista de disciplinas disponíveis para o período
        available_courses = get_available_courses(period+1)

        # Percorre os horários do período
        for _ in range(max_courses_per_period):
            if available_courses:
                # Seleciona aleatoriamente uma disciplina disponível
                selected_course = random.choice(available_courses)

                # Adiciona a disciplina ao período
                individual[period].append(selected_course)

                # Remove a disciplina selecionada das disponíveis
                available_courses.remove(selected_course)

    return printGenetic(individual, timeList)

def get_available_courses(period):
    disciplinas_periodo = Disciplina.objects.filter(periodo=period)

    available_courses = []
    for disciplina in disciplinas_periodo:
        available_courses.append(disciplina.tag)

    return available_courses

def fitness_function(timeList):
    global global_population
    fitness_value = 0 
    population = refresh_grade(global_population, timeList)

    fitness_value += check_prerequisite_conflicts(population)
    fitness_value += check_professor_conflicts(population)
    fitness_value += penalty_for_too_many_courses(population)
    fitness_value += penalty_for_invalid_schedule(population)


    return fitness_value

def penalty_for_invalid_schedule(population):
    penalty = 0
    global professor_list

    for professor in professor_list:
        penalty += check_prof_sched(population, professor.nome)
    
    return penalty

def check_prof_sched(individual, name):
    conflicts = 0
    target = {}
    global professor_availability


    for period, schedule in enumerate(individual):
        for subject in schedule:
            if subject['professor'] == name:
                target = subject
    
    for horario in professor_availability:
        if horario.professor.nome == target['professor'] and horario.day == target['day']:
            if parse_time(target['horario_atribuido']) >= horario.horario_from and parse_time(target['horario_atribuido']) <= horario.horario_to:
                return 0
            else:
                conflicts = 8

    return conflicts

def penalty_for_too_many_courses(schedule):
    penalty = 0

    for day_schedule in schedule:
        penalty += higlighting_number([item['day'] for item in day_schedule])

    return penalty

def higlighting_number(lista):
    contagem = Counter(lista)
    mais_frequentes = contagem.most_common()
    maior_frequencia = mais_frequentes[0][1]  # Frequência do número mais comum

    contagem_mais_comum = len([numero for numero, frequencia in mais_frequentes if frequencia == maior_frequencia])

    return contagem_mais_comum


def get_subject_by_code(tag):
    global subject_list

    for subject in subject_list:
        if subject.tag == tag:
            return subject

def check_professor_conflicts(individual):
    conflicts = 0
    professor_schedule = defaultdict(list)

    for period, schedule in enumerate(individual):
        for subject in schedule:
            subjectObj = get_subject_by_code(subject['disciplina'])
            professor = subjectObj.professor

            for prev_subject in professor_schedule[professor]:
                if has_time_conflict(subject, prev_subject):
                    conflicts += 1

            professor_schedule[professor].append(subject)

    return conflicts

def check_for_requirements(mainSubject):
    global subject_list

    for subject in subject_list:
        if mainSubject.requirement != None:
            if subject.id == mainSubject.requirement.id:
                return subject
        
    return None

def check_prerequisite_conflicts(individual):
    conflicts = 0

    for period, schedule in enumerate(individual):
        for subject in schedule:
            subjectObj = get_subject_by_code(subject['disciplina'])
            prerequisites = check_for_requirements(subjectObj)

            if prerequisites != None:
                obj = get_by_population(individual, prerequisites.tag)

                if has_time_conflict(subject, obj):
                    conflicts += 1

    return conflicts

def get_by_population(list, tag):
    for dicionario in list:
        for period in dicionario:
            if period['disciplina'] == tag:
                valor = period

    return valor

def has_time_conflict(time1, time2):
    start_time1 = parse_time(time1["horario_atribuido"])
    start_time2 = parse_time(time2["horario_atribuido"])

    end_time1 = calculate_end_time(start_time1, time1["carga"])
    end_time2 = calculate_end_time(start_time2, time2["carga"])

    return overlaps(start_time1, end_time1, start_time2, end_time2)

def parse_time(time_str):
    time_components = str(time_str).split(":")
    hours = int(time_components[0])
    minutes = int(time_components[1])
    seconds = int(time_components[2])
    return datetime.time(hours, minutes, seconds)

def calculate_end_time(start_time, carga):
    num_classes = carga // 30
    class_duration = datetime.timedelta(minutes=50)
    return (datetime.datetime.combine(datetime.date.today(), start_time) +
            num_classes * class_duration).time()

def overlaps(start_time1, end_time1, start_time2, end_time2):
    time_range1 = (start_time1, end_time1)
    time_range2 = (start_time2, end_time2)

    return max(time_range1) > min(time_range2) and max(time_range2) > min(time_range1)
    

def printGenetic(population, timeList):
    assigned_schedule = []
    index = 0
    for period, schedule in enumerate(population, start=1):
        period_schedule = []
        for subject in schedule:
            subData = Disciplina.objects.filter(tag=subject)[0]
            professor = subData.professor

            period_schedule.append({
                "disciplina": subject,
                "periodo": subData.periodo,
                "professor": professor.nome,
                "horario_atribuido": allowed_schedule[timeList[index]],
                "day": random.randint(1, 5),
                "carga":subData.carga
            })
            index += 1
        assigned_schedule.append(period_schedule)

    return assigned_schedule

def refresh_grade(population, timeList):
    index = 0
    for period, schedule in enumerate(population, start=1):
        for subject in schedule:
            subject['horario_atribuido'] = allowed_schedule[timeList[index]]
            index += 1

    return population




# def assign_subject_time(available_times):
#     assigned_time = None
    
#     # Verifica se existem horários disponíveis para a disciplina
#     if available_times:
#         # Itera pelos dias da semana em ordem aleatória
#         days = list(available_times.keys())
#         random.shuffle(days)
        
#         # Percorre os dias em ordem aleatória
#         for day in days:
#             if day in available_times:
#                 # Obtém os horários disponíveis para o dia atual
#                 available_times_day = available_times[day]
                
#                 if available_times_day:
#                     # Escolhe um horário aleatório disponível para o dia atual
#                     assigned_time = random.choice(available_times_day)
#                     available_times_day.remove(assigned_time)
#                     break  # Interrompe o loop ao atribuir um horário
    
#     return assigned_time







