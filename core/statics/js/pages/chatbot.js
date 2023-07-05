const userInput = document.getElementById('user-input')
const chatLog = document.getElementById('chatlog');
const parser = new DOMParser();
const processingMessageSkeleton = `
                                    <div class="mssg new loading badge badge-primary">
                                            <div class="loading-message">
                                                <span class="spinner-grow spinner-grow-sm" role="status"></span>
                                                <span class="spinner-grow spinner-grow-sm" role="status"></span>
                                                <span class="spinner-grow spinner-grow-sm" role="status"></span>
                                            </div>
                                    </div>
                                `

const navigationButtons = `
<div class="mssg new">
    <p class="mssg-content">Would you like to book for this doctor?</p>
    <button type="button" id="yes-btn" class="btn btn-primary rounded-pill">Yes</button>
    <button type="button" id="not-btn" class="btn btn-dark rounded-pill">No</button>
</div>

`                


const processingMessageHtmlDoc = parser.parseFromString(processingMessageSkeleton, 'text/html');
const processingMessageElm = processingMessageHtmlDoc.querySelector('.mssg');



const processingNavigationButtonsHtmlDoc = parser.parseFromString(navigationButtons, 'text/html');
const navigationButtonsElm = processingNavigationButtonsHtmlDoc.querySelector('.mssg');

const noButton = navigationButtonsElm.querySelector('#not-btn');
const yesButton = navigationButtonsElm.querySelector('#yes-btn');


function adjustInputHeight() {
    userInput.style.height = 'auto'; // Reset the height to auto
    userInput.style.height = userInput.scrollHeight + 'px'; // Set the height to fit the content
}


function generateMssgElm(content, personal=true) {
    const mssgSkeleton = `<div class="mssg new ${personal? "personal-message align-self-end": ""}"><p class="mssg-content m-0"></p></div>`;
    const mssgHtmlDoc = parser.parseFromString(mssgSkeleton, 'text/html');
    const mssgElm = mssgHtmlDoc.querySelector('.mssg');
    mssgElm.querySelector('.mssg-content').innerHTML = content.replaceAll('\n', '<br>');
    return mssgElm
}


function generateList(elm, items){
    for (let item of items)
        elm.appendChild(document.createElement('li')).innerHTML = item.replaceAll('_', ' ')
}


function generateDiagnosisMssg(symptoms, disease, purifications, recomanded_doctor_name){
    const mssgSkeleton = `
        <div class="mssg new response-message">
            <div class="mssg-content m-0">
                <h5>Captured symptoms are: </h5>
                <ul id="symptoms-list">
                </ul>
                <h5>Diagnosis: </h5>
                <p id="diagnosis" class="ps-3">${disease}</p>
                <h5>Purifications: </h5>
                <ul id="purifications-list">
                </ul>
                ${
                    recomanded_doctor_name ? `
                    <h5><b>Recomanded Doctor:</b></h5>
                    <p id="recomanded-doctor" class="ps-3">${recomanded_doctor_name}</p>` : ''
                }
                <h5><b>Cautions!</b></h5>
                <p>
                    Please be aware that our symptom checker is intended for informational 
                    purposes only and may not provide accurate diagnoses. It is strongly recommended to consult a qualified 
                    doctor or visit a clinic for a professional evaluation of your symptoms. Your health should always be 
                    prioritized, and seeking medical advice ensures that you receive proper care tailored to your specific 
                    needs.
                </p>
            </div>
            
        </div>
    `
    const mssgHtmlDoc = parser.parseFromString(mssgSkeleton, 'text/html');
    const mssgElm = mssgHtmlDoc.querySelector('.mssg.response-message');
    const symptomsList = mssgElm.querySelector('#symptoms-list')
    const purificaionsList = mssgElm.querySelector('#purifications-list')
    generateList(symptomsList, symptoms)
    generateList(purificaionsList, purifications)
    return mssgElm
}


  

let loadingMessageAppended = false;

function sendMssg(event){
    const delay = 0.3

    if (event.key === 'Enter') {
        event.preventDefault();
        if (event.shiftKey && event.key === 'Enter') {
            event.target.value += '\n';
            return;
        }
        let input = event.target.value;
        if (input == ''){
            // event.preventDefault();
            event.target.value = '';
            adjustInputHeight();
            return;
        }
        setTimeout(()=>{
            send_case(input)
        }, delay*1000)
        generatedMssgElm = generateMssgElm(input)
        chatLog.appendChild(generatedMssgElm)
        requestAnimationFrame(() => {
            if (!loadingMessageAppended) {
              requestAnimationFrame(() => {
                chatLog.appendChild(processingMessageElm);
                chatLog.scrollTop = chatLog.scrollHeight;
                loadingMessageAppended = true;
              });
            } else {
                loadingMessageAppended = false;
                chatLog.appendChild(processingMessageElm);
                chatLog.scrollTop = chatLog.scrollHeight;
            }
          });
        // chatLog.scrollTop = chatLog.scrollHeight;
        event.target.value = ''
        adjustInputHeight()
    }
}

function send_case(userCase){
    const formdata = new FormData();
    formdata.append('case', userCase)
    fetch('/chatbot/diagnose/', {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        body: formdata
    }).then(res => {
        if (res.ok){
            console.log("its ok!!")
            return res.json()
        }
        console.log("it has proceeded!!!!")
        throw {
            error: new Error('Something went wrong'),
            response: res
        };
    }).then(data => {
        let loadingMssgElm = chatLog.querySelector('.mssg.loading')
        doctorSuggestionExists = 'recomanded_doctor' in data.result
        result = generateDiagnosisMssg(
            data.result.symptoms,
            data.result.diagnosis,
            data.result.purifications,
            doctorSuggestionExists? data.result.recomanded_doctor: '',
        )
        if(doctorSuggestionExists)
            setTimeout(()=> {
                chatLog.appendChild(navigationButtonsElm)
                chatLog.scrollTop = chatLog.scrollHeight;   
            }
            ,500);
       
        loadingMssgElm.replaceWith(result)
        chatLog.scrollTop = chatLog.scrollHeight;   
    }).catch(err => {
        err.response.json().then(data => {
            let loadingMssgElm = chatLog.querySelector('.mssg.loading')
            result = generateMssgElm(data.message, false)
            loadingMssgElm.replaceWith(result)
            chatLog.scrollTop = chatLog.scrollHeight;   
        })
       
    })
}


function detatchRedirectQuestionMessage(){
    $(navigationButtonsElm).addClass('reverse-animation');
    $(navigationButtonsElm).one('animationend', function() {
        $(navigationButtonsElm).remove();
        $(navigationButtonsElm).removeClass('reverse-animation');
    });
}



userInput.addEventListener('input', adjustInputHeight);
userInput.addEventListener('keydown', sendMssg);

noButton.addEventListener('click', detatchRedirectQuestionMessage);
yesButton.addEventListener('click', ()=> window.location.href = '/booking/');
