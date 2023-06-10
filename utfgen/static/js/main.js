let baseUrl = "http://127.0.0.1:8000/";
let currentPeriod = 1;
let intervalId
var hours = 0;
var minutes = 0;
var seconds = 0;
let blocked = false;

window.onload = function () {
    let btnTable = document.querySelectorAll(".btnTable");
    let timeAvaliableModal = document.getElementById("timeAvaliableModal");
    let subjectModal = document.getElementById("SubjectModal");
    let timeAvaliableTable = document.getElementById("timeAvaliableTable");
    let timeProfName = document.getElementById("timeProfName");
    let btnCloseModal = document.getElementById("btnCloseModal");
    let btnAddTime = document.getElementById("btnAddTime");


    btnTable.forEach((item) => {
        item.onclick = async () => {
            let id = item.dataset.id;
            let role = item.dataset.role;

            if (role === "prof") {
                timeAvaliableModal.style.display = "flex";
                document.getElementById("idProd").value = id;

                let resp = await getTimeAvaliable(id);
                let html = "";

                if (resp.horarios.length > 0) {
                    resp.horarios.forEach((item) => {
                        html += `
                    <tr>
                        <td>${dayOfTheWeek(item.dia_semana)}</td>
                        <td>${item.hora_from}</td>
                        <td>${item.hora_to}</td>
                        <td><button onclick="deleteTimeAvaliable(this)" data-id="${item.id}">Deletar</button></td>
                    </tr>`;
                    })
                } else {
                    html = `<tr class="notFound">
                            <td colspan="4">Nenhum horario encontrado</td>
                        </tr>`;
                }

                timeProfName.innerHTML = `Prof ${resp.prof}`;
                timeAvaliableTable.innerHTML = html;
            } else {
                subjectModal.style.display = "flex";
                document.getElementById("idSubject").value = id;
                let resp = await getSubject(id);
                let selectHTML = ''

                console.log(resp);

                if (resp.disciplina.relacao === null) {
                    selectHTML += `<option value='none'>Escolha uma opção (opcional)</option>`
                }

                document.querySelector('.time-control[name=timeConsumed]').value = resp.disciplina.carga;
                document.querySelector('.time-control[name=difficulty]').value = resp.disciplina.dificuldade;

                resp.lista.forEach((item) => {
                    selectHTML += `<option value='${item.id}'>${item.nome}</option>`
                })

                document.getElementById("requirementList").innerHTML = selectHTML;

                if (resp.disciplina.relacao !== null) document.getElementById("requirementList").value = resp.disciplina.relacao;

            }
        }
    });

    btnCloseModal.onclick = () => {
        if (timeAvaliableModal) timeAvaliableModal.style.display = "none";
        if (subjectModal) subjectModal.style.display = "none";
    }

    btnAddTime.onclick = async () => {
        let role = btnAddTime.dataset.role;

        if (role === "prof") {
            let timeInputFrom = document.querySelector('.time-control[name=from]').value;
            let timeInputTo = document.querySelector('.time-control[name=to]').value;
            let timeInputDay = document.querySelector('.time-control[name=day]').value;
            let idProf = document.getElementById("idProd").value;

            if (timeInputFrom.length === 0 || timeInputTo.length === 0 || timeInputDay.length === 0) {
                alert("Preencha todos os campos");
                return;
            }

            try {
                let resp = await fetch(baseUrl + "registerTime/", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        timeFrom: timeInputFrom,
                        timeTo: timeInputTo,
                        day: timeInputDay,
                        idProf: idProf
                    })
                });

                resp = await resp.json();
                alert(resp.message);
            } catch (error) {
                console.error(error);
            }
        } else {
            let timeConsumed = document.querySelector('.time-control[name=timeConsumed]').value;
            let difficulty = document.querySelector('.time-control[name=difficulty]').value;
            let idSubject = document.getElementById("idSubject").value;

            if (timeConsumed.length === 0 || difficulty.length === 0) {
                alert("Preencha todos os campos");
            }

            try {
                let resp = await fetch(baseUrl + "editSubject/" + idSubject + "/", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        timeConsumed: timeConsumed,
                        difficulty: difficulty,
                        requiriments: document.getElementById("requirementList").value
                    })
                });

                resp = await resp.json();
                alert(resp.message);
            } catch (error) {
                console.error(error);
            }
        }
    }
}

async function deleteTimeAvaliable(element) {
    if (confirm("Tem certeza que deseja deletar esse item")) {
        let parent = element.parentElement.parentElement;
        let count = element.parentElement.parentElement.querySelectorAll('td').length;
        let id = element.dataset.id;
        parent.remove();

        let resp = await fetch(baseUrl + `deleteTimeAvaliable/${id}/`);
        resp = await resp.json();

        alert(resp.message);

        if (count === 0 || count === undefined) {
            html = `<tr class="notFound">
                            <td colspan="4">Nenhum horario encontrado</td>
                        </tr>`;
            timeAvaliableTable.innerHTML = html;
        }
    }
}

function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        .split('=')[1];
    return cookieValue;
}

function dayOfTheWeek(id) {
    switch (id) {
        case 1: return "Seg";
        case 2: return "Ter";
        case 3: return "Qua";
        case 4: return "Qui";
        case 5: return "Sex";
    }
}

function periodNav(element) {
    let direction = element.dataset.direction;
    let sdf = document.getElementById("df");
    let slider = document.getElementById("slider");
    let position = (slider.style.transform.length === 0) ? 0 : parseInt(slider.style.transform.split(/\D+/).join(""), 10);
    let periodTitle = document.getElementById("periodCount");

    if (!element.classList.contains("disabled")) {
        if (direction == "left") {
            position = -position + 25;
            currentPeriod -= 1;
        } else {
            position = -position - 25;
            console.log(currentPeriod)
            currentPeriod += 1;
            console.log(currentPeriod)
        }

        slider.style.transform = `translateX(${position}%)`;
        periodTitle.innerHTML = currentPeriod + "º";

        if (currentPeriod == 2) {
            if (document.querySelector(".btnPeriodMove.disabled")) document.querySelector(".btnPeriodMove.disabled").classList.remove("disabled");
        } else if (currentPeriod == 4) {
            document.querySelectorAll(".btnPeriodMove")[1].classList.add("disabled");
        } else if (currentPeriod == 1) {
            document.querySelectorAll(".btnPeriodMove")[0].classList.add("disabled");
        } else {
            if (document.querySelector(".btnPeriodMove.disabled")) document.querySelector(".btnPeriodMove.disabled").classList.remove("disabled");
        }


    }

}

function loading_counter(start) {
    if (start) {
        document.getElementById("time").innerHTML = "00:00:00";
        intervalId = setInterval(updateTimer, 1000);
    }else{
        stopTimer();
    }
}

function updateTimer() {
    seconds++;
    if (seconds === 60) {
        seconds = 0;
        minutes++;
        if (minutes === 60) {
            minutes = 0;
            hours++;
        }
    }

    var formattedTime =
        pad(hours) + ":" + pad(minutes) + ":" + pad(seconds);
    document.getElementById("time").innerHTML = formattedTime
}

function pad(value) {
    return value < 10 ? "0" + value : value;
  }

function stopTimer() {
    clearInterval(intervalId);
    hours = 0;
    minutes = 0;
    seconds = 0;
    intervalId = null;
  }

async function generateGrade() {
    if(blocked){
        console.log("Aguarde...")
        return;
    }

    try {
        document.getElementById('loading').style.display = "flex";
        document.getElementById('grade').style.height = "calc(100% - 80px)";
        document.querySelectorAll('.period').forEach(item => item.style.display = "none");
        document.getElementById('slider').style.transition = "none";
        document.getElementById("navButtons").style.display = "none";
        document.getElementById('slider').removeAttribute('style');
        document.getElementById('slider').style.transform = "translateX(0)";
        loading_counter(true);
        blocked = true;
        let resp = await fetch(baseUrl + `genetic/`);
        resp = await resp.json();
        let html = '';

        for (i = 1; i <= 4; i++) {
            document.querySelector("#period" + i).innerHTML = `
                <div class="collumn Seg"></div>
                <div class="collumn Ter"></div>
                <div class="collumn Qua"></div>
                <div class="collumn Qui"></div>
                <div class="collumn Sex"></div>
            `;
        }

        resp.result.forEach((item) => {
            item.forEach((subject) => {
                html = `<div class="item">
                            <p class="time">${dayOfTheWeek(subject.day)} ${subject.horario_atribuido}</p>
                            <div class="tag">
                                <ul>
                                    <li>Professor: ${(subject.professor.length > 16) ? subject.professor.slice(0, 16) : subject.professor}</li>
                                    <li>Disciplina: ${subject.disciplina}</li>
                                </ul>
                            </div>
                        </div>`;

                document.querySelector("#period" + subject.periodo + " .collumn." + dayOfTheWeek(subject.day)).innerHTML += html;
            })
        })

        loading_counter(false);
        blocked = false;

        document.getElementById("navButtons").style.display = "flex";
        document.getElementById('slider').style.transition = "transform 1s";
        document.getElementById('loading').style.display = "none";
        document.getElementById('grade').style.height = "100%";
        document.querySelectorAll('.period').forEach(item => item.style.display = "flex");

        return resp;
    } catch (e) {
        console.log("Error: " + e);
    }
}

async function getTimeAvaliable(id) {
    try {
        let resp = await fetch(baseUrl + `getTimeAvaliable/${id}`);
        resp = await resp.json();

        return resp;
    } catch (e) {
        console.log("Error: " + e);
    }
}

async function getSubject(id) {
    try {
        let resp = await fetch(baseUrl + `getSubject/${id}`);
        resp = await resp.json();

        return resp;
    } catch (e) {
        console.log("Error: " + e);
    }
}