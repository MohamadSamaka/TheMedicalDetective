let socket;
let accuracyElm;
let lossElm;
let submitFaker;
let spinner;

function updateTrainingProgress(recievedData){
    let accuracy = recievedData.info.accuracy.toFixed(2)
    let loss = recievedData.info.loss.toFixed(2)
    accuracyElm.text(accuracy)
    lossElm.text(loss)
}


function showTrainningProgress(){
    spinner.addClass('d-none')
    $('#training')
    .addClass('active')
    .addClass('show')
    .removeClass('pe-none')
    $('#add-model')
    .removeClass('show')
    .removeClass('active')
    .addClass('pe-none')
}

function showAddView(){
    $('#cancel-training-btn').removeClass('d-none')
    $('#goback-training-btn').addClass('d-none');
    spinner.addClass('d-none')
    $('.alert-danger').removeClass('show').addClass('d-none')
    $('.alert-success').removeClass('show').addClass('d-none')
    $('#add-model')
    .addClass('active')
    .addClass('show')
    .removeClass('pe-none')
    $('#training')
    .removeClass('show')
    .removeClass('active')
    .removeClass('pe-none')
}

function cancelTraining(){
    fetch('/admin/chatbot_models_manager/ner/cancel_training/',{
        method: 'POST',
        headers: {'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val() },
        }).then(response => {
            console.log(response);
        })
        .catch(error => {
            console.log(error)
        })
    location.reload();
}



function clearProgress(){
    accuracyElm.text(0)
    lossElm.text(0)
}




function socketMessageHandler(recievedData){
    switch (recievedData.type) {
        case 'progress_update':
            updateTrainingProgress(recievedData)
            break;
        case 'form_validiation_result':
            if(recievedData.info.validity)
                showTrainningProgress()
            break;
        default:
            break;
    }
}




function index(){
    let url = `ws://${window.location.host}/ws/socket-server/`
    let socket = new WebSocket(url);
    accuracyElm = $('#accuracy')
    lossElm = $('#loss')
    spinner = $('#spinner')
    socket.onmessage = function(e){
        let recievedData = JSON.parse(e.data.replace(/'/g, '"'))
        socketMessageHandler(recievedData)
    }
    $('#go-to-training-btn').on('click', function(){
        spinner.removeClass('d-none')
        $('#add-model').removeClass('show')
        let form = new FormData(document.querySelector('#ner-form'))
        let fileInput = document.querySelector('#id_training_file');

        if (fileInput.files.length > 0) {
            let file = fileInput.files[0];
            form.append('training_file', file, file.name);
        }

        
        fetch('/admin/chatbot_models_manager/ner/validate_ner_form/',{
            method: 'POST',
            headers: {'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val() },
            body:form,
            }).then(response => {
                return Promise.all([response.text(), response.status])
            })
            .then(async ([rawHtml, statusCode]) => {
                if(statusCode == 200){
                    spinner.addClass('d-none')
                    $('.alert-danger').removeClass('show').addClass('d-none')
                    $('.alert-success').removeClass('d-none').addClass('show')
                    $('#go-to-training-btn').removeClass('active')
                    $('#goback-training-btn').removeClass('d-none')
                    $('#cancel-training-btn').addClass('d-none');
                    return;
                }
                let myDoc = new DOMParser();
                let elm = myDoc.parseFromString(rawHtml, 'text/html')
                let form = elm.querySelector('body #ner-form')
                document.querySelector("#ner-form").replaceWith(form)
                showAddView()

                await new Promise(resolve => setTimeout(resolve, 1000));
                console.log("closing socket now!")
            })
            .catch(error => {
                $('#go-to-add-info-btn').click()
            })
   });

    $('#go-to-add-info-btn').on('click', function(){
      $(this).removeClass('active')
    });


    // testingFile.on('change', function(){
    //     if(this.files.length != 0)
    //         saveBtn.val("Train and Test")
    // });
}



function setEventListeners(){
    $('#go-to-add-info-btn').on('click', showAddView)
    $('#cancel-training-btn').on('click', cancelTraining)
}





$(document).ready(function(){
    setEventListeners();
    index()
});