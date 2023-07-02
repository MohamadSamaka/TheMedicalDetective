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
    spinner.addClass('d-none')
    $('#add-model')
    .addClass('active')
    .addClass('show')
    .removeClass('pe-none')
    $('#training')
    .removeClass('show')
    .removeClass('active')
    .addClass('pe-none')
}

function cancelTraining(){
    fetch('/admin/chatbot_models_manager/diagnoser/cancel_training/',{
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




function socketMessageHandler(data){
    let recievedData = JSON.parse(data.replace(/'/g, '"'))
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
    console.log("index")
    let url = `ws://${window.location.host}/ws/socket-server/`
    let socket = new WebSocket(url);
    accuracyElm = $('#accuracy')
    lossElm = $('#loss')
    spinner = $('#spinner')
    socket.onmessage = function(e){
        let recievedData = JSON.parse(e.data.replace(/'/g, '"'))

        socketMessageHandler(e.data)
    }

    // $('#diagnoser_form .card').removeClass('card')
    // const saveBtn = $("input[name='_save']")
    // const testingFile = $('#testing-file')
    
    // submitFaker.click(function() {
    //     $('#diagnoser_form').submit();
    // });

    // $('#save-button').on('click', function(e){
    $('#go-to-training-btn').on('click', function(){
        spinner.removeClass('d-none')
        $('#add-model').removeClass('show')
        let form = new FormData(document.querySelector('#diagnoser-form'))
        let fileInput = document.querySelector('#id_training_file');

        // Check if a file is selected
        if (fileInput.files.length > 0) {
            // Get the first selected file
            let file = fileInput.files[0];
            // Append the file to the form data
            form.append('training_file', file, file.name);
        }

        
        fetch('/admin/chatbot_models_manager/diagnoser/validate_diagnosis_form/',{
            method: 'POST',
            headers: {'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val() },
            body:form,
            }).then(response => {
                // console.log(response);
                return Promise.all([response.text(), response.status])
            })
            .then(async ([rawHtml, statusCode]) => {
                // console.log(statusCode)
                if(statusCode == 200){
                    // $('#training').remove('d-none')
                    spinner.addClass('d-none')
                    $('#go-to-training-btn').removeClass('active')
                    $('#goback-training-btn').removeClass('d-none')
                    $('#cancel-training-btn').remove();
                    console.log("hello mf!!")
                    return;
                }
                let myDoc = new DOMParser();
                let elm = myDoc.parseFromString(rawHtml, 'text/html')
                let form = elm.querySelector('body #diagnoser-form')
                document.querySelector("#diagnoser-form").replaceWith(form)
                showAddView()

                // index()
                await new Promise(resolve => setTimeout(resolve, 1000));
                console.log("closing socket now!")
                // socket.close(); 
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
    $('#goback-training-btn').on('click', location.reload)
    $('#cancel-training-btn').on('click', cancelTraining)
}





$(document).ready(function(){
    setEventListeners();
    index()
});