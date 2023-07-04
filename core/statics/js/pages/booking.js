

let docsCardsList = [];
let docsPerSpecializaiton = {};
let docsPerHospital = {};
let previousSelectedHospital = '';
let formCheckInputs = $('#booking .form-check .form-check-input');
const myModal = $('#exampleModal');
let confirmingAppointmentBtn = $('#confirm-appointment-btn')
let ConfirmingAppointmentBtnInfo = confirmingAppointmentBtn.find('.btn-text')
let appointmentFailMssg = $('#exampleModal .alert-danger')
let appointmentSuccessMssg = $('#exampleModal .alert-success')
let dateTimeInputFeild = $('#id_appointment_date_time')


// Generate a doctor card from the provided information
function generateCardFromInfo(id, fname, lname, spec, hospital, isRecomanded){
    const doctorBluePrint = `
    <div id="doctor-id-${id}" class="doctor-wrapper pt-3 pb-3 card flex-row justify-content-center ${ !isRecomanded? 'd-none': 'active'}">
        <div class="basic-info card text-center border-0">
            <img class="doctor-image shadow-lg rounded-circle card-img-top align-self-center" src="${DJANGO_STATIC_URL}images/default_doctor.png" alt="doctor">
            <h5 class="card-title">${fname} ${lname}</h5>
            <p class="card-text">${spec}</p>
        </div>
        <div class="more-info card justify-content-center border-0">
            <div class="flex flex-column text-nowrap">
                <span class="info-title fw-bold">Specialization</span>
                <p class="info-content text-muted">${spec}</p>
            </div>
            <div class="flex flex-column text-nowrap">
                <span class="info-title fw-bold">Hospital</span>
                <p class="info-content text-muted">${hospital}</p>
            </div>
            <div>
                <i class="bi bi-arrow-right"></i>
                <button type="button" class="btn btn-primary make-appointment-btn" data-bs-toggle="modal" data-bs-target="#exampleModal">
                    Schedule
                </button>
            </div>
        </div>
    </div>
    `
    return $($.parseHTML(doctorBluePrint)[1].outerHTML);
}

function generateDocsCards(){
    for(const hospitalId of Object.keys(hospitalsInfo)){
        for(let i = 0; i < hospitalsInfo[hospitalId].docs.length; i++){
            let doc = hospitalsInfo[hospitalId].docs[i]
            console.log(window.recomanded_doctor == doc.id)

            let generatedDoc = generateCardFromInfo(
                doc.id,
                doc.f_name,
                doc.l_name,
                specelization_map[doc.specialization], 
                hospitalsInfo[hospitalId].hospital_name,
                window.recomanded_doctor == doc.id
            )
            
            docsCardsList.push(generatedDoc);
            docsPerSpecializaiton[doc.specialization] = docsPerSpecializaiton[doc.specialization] || []
            docsPerSpecializaiton[doc.specialization].push(generatedDoc)
            docsPerHospital[hospitalId] = docsPerHospital[hospitalId] || []
            docsPerHospital[hospitalId].push(generatedDoc)
        }
    }
    $('.right-side .doctors-list-wrapper').append(docsCardsList);
}


function intersectedDocs(cardsList1, cardsList2){
    var intersection = $.grep(cardsList1, function(item) {
        return cardsList2.toArray().includes(item);
      });
    return intersection;
}


function showSuitableDocCards(cards){
    for(let card of docsCardsList)
        card.addClass('d-none')
    for(let card of cards)
        card.removeClass('d-none')
}



function getAppliedSpecFilter(){
    let checkedBoxes = $('#booking .form-check .form-check-input:checked')
    return {
        cardsShouldAppear: checkedBoxes.map(function(){
            return docsPerSpecializaiton[$(this).val()];
        }),
        checkedBoxesCount: checkedBoxes.length
    }
}



generateDocsCards();

$(document).ready(function() {
    if(window.recomanded_doctor)
        myModal.modal('show');
});


$('#myModal').on('shown.bs.modal', function () {
    $('#myInput').trigger('focus')
});

$('#booking .doctor-wrapper').click( function(event) {
    var clickedElement = $(this);
    if (!event.target.classList.contains('make-appointment-btn')) {
        $('#booking .doctor-wrapper').not(clickedElement).removeClass('active');
        clickedElement.toggleClass('active');
    }
});


formCheckInputs.change(function(){
    let hospitalId = $('#id_hospitals').val()
    let {cardsShouldAppear, checkedBoxesCount} =  getAppliedSpecFilter()
    let appliedHospitalFilter = docsPerHospital[hospitalId] || []
    if(cardsShouldAppear.length > 0)
        cardsShouldAppear = intersectedDocs(appliedHospitalFilter, cardsShouldAppear)
    else if(appliedHospitalFilter.length && cardsShouldAppear.length == 0)
        cardsShouldAppear = checkedBoxesCount? []: appliedHospitalFilter
    else
        cardsShouldAppear = []   
    showSuitableDocCards(cardsShouldAppear)
})

$('#div_id_hospitals .form-select').change(function(){
    let hospitalId = $(this).val()
    let cardsShouldAppear = docsPerHospital[hospitalId] || []
    let appliedSpecFilter =  getAppliedSpecFilter()

    if(appliedSpecFilter.length > 0){
        cardsShouldAppear = intersectedDocs(appliedSpecFilter, cardsShouldAppear)
    }
    showSuitableDocCards(cardsShouldAppear)
})



confirmingAppointmentBtn.click(bookAppointment);



function putInState(state){
    switch (state) {
        case 102://processing
            confirmingAppointmentBtn.off('click');
            confirmingAppointmentBtn.addClass('processing-state');
            break;
        case 200://success
            ConfirmingAppointmentBtnInfo.text("Succeded")
            confirmingAppointmentBtn
            .removeClass('processing-state btn-danger btn-primary')
            .addClass('success-state btn-success')
            confirmingAppointmentBtn.off('click');
            appointmentFailMssg.addClass('d-none')
            appointmentSuccessMssg.removeClass('d-none')
            confirmingAppointmentBtn.find('.bi-check-circle').addClass('d-inline')
            break;
        default://fail
            ConfirmingAppointmentBtnInfo.text("Try again")
            confirmingAppointmentBtn
            .removeClass('processing-state btn-primary')
            .addClass('btn-danger')
            appointmentFailMssg.removeClass('d-none')
            confirmingAppointmentBtn.click(bookAppointment);
            break;
    }
}



myModal.on('hidden.bs.modal', function () {
    ConfirmingAppointmentBtnInfo.text("Confirm")
    appointmentFailMssg.addClass('d-none')
    appointmentSuccessMssg.addClass('d-none')
    confirmingAppointmentBtn.find('.bi-check-circle').addClass('d-none').removeClass('d-inline')
    confirmingAppointmentBtn.removeClass(
        'btn-danger processing-state btn-success'
        )
        .addClass('success-state btn-primary')
    confirmingAppointmentBtn.off('click').on('click', bookAppointment);
});


function bookAppointment(){
    putInState(102);
    const csrftoken = myModal.find('form input[name=csrfmiddlewaretoken]').val()
    let docId = $('.doctor-wrapper.active')[0].id.split(/[- ]+/).pop();
    let dateTimeVal = dateTimeInputFeild.val()
    let formData = new FormData();
    formData.append('doc-id', docId)
    formData.append('date-time', dateTimeVal)
    fetch('/booking/',{
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        body: formData
    }).then(res => {
        if(res.ok){
            putInState(200)
            return;
        }
        throw {
            response: res
        };
    })
    .catch(err => {
        err.response.json().then(e => {
            appointmentFailMssg.text(e.message)
            putInState(404);
        })
    })
}