import json
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse

from .models import Professor, Disciplina, ProfessorHorario
from .genetic import callGenetic, initialize_individual

# Create your views here.
def index(request):
    return render(request, 'grid/grid.html')

def professor(request):
    list = {
        "professores": Professor.objects.all()
    }

    return render(request, 'grid/professor.html', list)

def disciplinas(request):
    list = {
        "disciplinas": Disciplina.objects.all()
    }
    return render(request, 'grid/disciplinas.html', list)

def getTimeAvaliable(request, id):
    try:
        professor = Professor.objects.get(id=id)
        horarios = ProfessorHorario.objects.filter(professor=professor).order_by('day')

        horarios_list = []
        for horario in horarios:
            horarios_list.append({
                'id': horario.id,
                'dia_semana': horario.day,
                'hora_from': horario.horario_from,
                'hora_to': horario.horario_to
            })

        return JsonResponse({'horarios': horarios_list, "prof": professor.nome})
    except ProfessorHorario.DoesNotExist:
        return JsonResponse({'error': 'Objeto não encontrado'}, status=404)
    
def deleteTimeAvaliable(request, id):
    try:
        horario = ProfessorHorario.objects.get(id=id)
        horario.delete()
        
        return JsonResponse({'message': 'Registro excluído com sucesso'})
    except ProfessorHorario.DoesNotExist:
        return JsonResponse({'error': 'Objeto não encontrado'}, status=404)
    
def getSubject(request, id):
    try:
        obj = Disciplina.objects.get(id=id)
        objRequirement = []

        if obj.requirement:
            objRequirement = get_object_or_404(Disciplina, id=obj.requirement.id)
            objRequirement = objRequirement.id
        else:
            objRequirement = None
        
        objAll = Disciplina.objects.all()

        data = {
            'id': obj.id,
            'nome': obj.nome,
            'carga': obj.carga,
            'relacao': objRequirement,
            'dificuldade': obj.dificuldade
        }

        subject_list = []
        for subject in objAll:
            subject_list.append({
                'id': subject.id,
                'nome': subject.nome
            })
        
        return JsonResponse({'disciplina': data, 'lista': subject_list})
    except ProfessorHorario.DoesNotExist:
        return JsonResponse({'error': 'Objeto não encontrado'}, status=404)
    
def genetic(request):
    try:
        return JsonResponse({'result': callGenetic()})
    except ProfessorHorario.DoesNotExist:
        return JsonResponse({'error': 'Objeto não encontrado'}, status=404)
    
def registerTime(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            timeFrom = data.get('timeFrom')
            timeTo = data.get('timeTo')
            day = data.get('day')
            idProf = data.get('idProf')

            professor = Professor.objects.get(id=idProf)
            horario = ProfessorHorario()
            horario.horario_from = timeFrom
            horario.horario_to = timeTo
            horario.day = day
            horario.professor = professor
            horario.save()
        
        return JsonResponse({'message': 'Registro adicionado com sucesso'})
    except ProfessorHorario.DoesNotExist:
        return JsonResponse({'error': 'Objeto não encontrado'}, status=404)
    
def editSubject(request, id):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)

            requiriments = Disciplina.objects.get(id=data.get('requiriments'))
            disciplina = Disciplina.objects.get(id=id)
            disciplina.carga = data.get('timeConsumed')
            disciplina.dificuldade = data.get('difficulty')
            disciplina.requirement = requiriments
            
            disciplina.save()
        
        return JsonResponse({'message': 'Registro editado com sucesso'})
    except ProfessorHorario.DoesNotExist:
        return JsonResponse({'error': 'Objeto não encontrado'}, status=404)