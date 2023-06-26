// // static/admin/js/custom_admin.js
// const saveButton = document.querySelector('input[name="_save"]');
// // document.addEventListener('DOMContentLoaded', function() {
// //     console.log("hello world!")

// //     // Find the save button element
// //     var saveButton = document.querySelector('input[name="_save"]');
    
// //     // Add a click event listener to the save button
    
// // });


// saveButton.addEventListener('click', function(event) {
//     // event.preventDefault();
//     // console.log(saveButton.action)
//     // console.log('LOL')
//     // // Add your condition here
//     // if (yourCondition) {
//     //     // Allow the default form submission
//     //     return true;
//     // } else {
//     //     // Prevent the default form submission
//     //     event.preventDefault();
        
//     //     // Perform any additional actions or show a message if needed
//     //     alert('Your condition is not met. Form submission is canceled.');
        
//     //     // Return false to prevent the form from being submitted
//     //     return false;
//     // }
// });

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
    console.log("showing right thing")
    spinner.addClass('d-none')
    $('#training').addClass('active').addClass('show')
    $('#go-to-training-btn').removeClass('active')
    $('#add-model').addClass('d-none')
}

function goBackAndClearProgress(){
    clearProgress()
    $('diagnoser-form').trigger('reset')
}



function clearProgress(){
    accuracyElm.text(0)
    lossElm.text(0)
}




function socketMessageHandler(data){
    let recievedData = JSON.parse(data.replace(/'/g, '"'))
    switch (recievedData.type) {
        case 'progress_update':
            console.log(recievedData)
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
    submitFaker = $('#submit-btn-faker')
    spinner = $('#spinner')
    socket.onmessage = function(e){
        console.log(e.data)
        let recievedData = JSON.parse(e.data.replace(/'/g, '"'))
        console.log(recievedData)

        socketMessageHandler(e.data)

        // updateProgres(recievedData)

        // console.log(recievedData.info.num)
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
                console.log(response);
                return Promise.all([response.text(), response.status])
            })
            .then(async ([rawHtml, statusCode]) => {
                console.log(statusCode)
                if(statusCode == 200){
                    // $('#training').remove('d-none')
                    spinner.addClass('d-none')
                    $('#go-to-training-btn').removeClass('active')
                    return;
                }
                let myDoc = new DOMParser();
                let elm = myDoc.parseFromString(rawHtml, 'text/html')
                let form = elm.querySelector('body #diagnoser-form')
                document.querySelector("#diagnoser-form").replaceWith(form)
                spinner.addClass('d-none')
                $('#add-model').addClass('show')
                $('#training').removeClass('show').removeClass('active')

                // index()
                await new Promise(resolve => setTimeout(resolve, 1000));
                console.log("closing socket now!")
                // socket.close(); 
            })
            .catch(error => {
                
                $('#go-to-add-info-btn').click()
            })


        // fetch('/admin/chatbot_models_manager/diagnoser/add/',{
        //     method: 'POST',
        //     headers: {'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val() },
        //     body:form,
        //     }).then(response => {console.log(response)})
        //     .catch(error => {
        //         console.error('Failed to start training:', error);
        // });

    //   fetch('/admin/chatbot_models_manager/diagnoser',{
    //     method: 'POST',
    //     headers: {'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val() },
    //     }).then(response => response)
    //     .then(async data => {
    //         await new Promise(resolve => setTimeout(resolve, 1000));
    //         socket.close(); 
    //         submitFaker.removeClass('d-none')
    //         console.log("socket closed!")
    //     })
    //     .catch(error => {
    //         console.error('Failed to start training:', error);
    //     });
   });

    $('#go-to-add-info-btn').on('click', function(){
      $(this).removeClass('active')
    });

    $('')

    // testingFile.on('change', function(){
    //     if(this.files.length != 0)
    //         saveBtn.val("Train and Test")
    // });
}



function setEventListeners(){
    $('cancel-training-btn').on('click', function(){
        clearProgress()
        goBackAndClearProgress()
    })
}





$(document).ready(function(){
    index()
});